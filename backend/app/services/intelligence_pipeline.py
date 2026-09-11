"""Core AI Intelligence Pipeline.

Processes signals through:
1. Intent classification
2. Opportunity extraction
3. Scoring & validation
4. Explanation generation
5. Opportunity creation
6. Provider matching
"""
import logging
from typing import Optional
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Opportunity,
    OpportunityStatus,
    Signal,
    SignalStatus,
    UrgencyLevel,
)
from app.services.ai_provider import get_ai_provider

logger = logging.getLogger("pipeline")


async def process_signal(db: AsyncSession, signal: Signal) -> Optional[Signal]:
    """
    Run a signal through the full AI intelligence pipeline.

    Returns the updated signal, or None if processing failed permanently.
    """
    ai = get_ai_provider()

    try:
        # Step 1: Classify commercial intent
        signal.status = SignalStatus.PROCESSING
        await db.flush()

        classification = await ai.classify_intent({
            "title": signal.title,
            "description": signal.description,
            "country_code": signal.country_code,
            "source": signal.source,
        })

        # Validate classification output
        if "intent_score" not in classification or "confidence" not in classification:
            raise ValueError("Invalid classification output: missing required fields")

        signal.intent_classification = classification
        signal.intent_score = classification["intent_score"]
        signal.confidence = classification["confidence"]
        signal.status = SignalStatus.CLASSIFIED
        await db.flush()

        # Step 2: Extract structured opportunity data
        extracted = await ai.extract_opportunity(
            {"title": signal.title, "description": signal.description,
             "country_code": signal.country_code, "source": signal.source},
            classification,
        )

        # Validate extraction output
        required_fields = ["category", "urgency", "why_now"]
        for field in required_fields:
            if field not in extracted:
                raise ValueError(f"Invalid extraction output: missing '{field}'")

        signal.extracted_data = extracted
        signal.status = SignalStatus.EXTRACTED
        await db.flush()

        # Step 3: Score & Validate
        intent_score = classification["intent_score"]
        confidence = classification["confidence"]

        # Apply scoring thresholds
        from app.core.config import settings
        if intent_score < settings.MIN_INTENT_SCORE or confidence < settings.MIN_CONFIDENCE:
            signal.status = SignalStatus.REJECTED
            signal.processed_at = datetime.now(timezone.utc)
            await db.flush()
            return signal

        signal.status = SignalStatus.VALIDATED
        await db.flush()

        # Step 4: Create the Opportunity
        opportunity = _create_opportunity_from_signal(signal, classification, extracted)
        db.add(opportunity)
        await db.flush()

        # Step 5: Auto-match providers now that the opportunity exists, so an
        # admin sees pre-scored, ranked providers immediately instead of having
        # to click "Run Matching" manually. Best-effort and isolated from the
        # outer exception handler below — a matching failure must not mark an
        # otherwise-successful opportunity's signal as ERROR, and the manual
        # "Run Matching" button remains available as a fallback either way.
        if opportunity.organization_id:
            try:
                from app.services.provider_matching import match_opportunity_to_providers
                await match_opportunity_to_providers(db, opportunity)
            except Exception as e:
                logger.warning(
                    "Auto-matching failed for opportunity %s: %s", opportunity.id, e
                )

        signal.processed_at = datetime.now(timezone.utc)
        await db.flush()

        return signal

    except Exception as e:
        signal.status = SignalStatus.ERROR
        signal.error_message = str(e)
        signal.retry_count += 1
        await db.flush()
        return signal


def _create_opportunity_from_signal(
    signal: Signal,
    classification: dict,
    extracted: dict,
) -> Opportunity:
    """Create an Opportunity record from processed signal data."""

    # Determine urgency from extracted data
    urgency_raw = extracted.get("urgency", "medium")
    urgency_map = {
        "low": UrgencyLevel.LOW,
        "medium": UrgencyLevel.MEDIUM,
        "high": UrgencyLevel.HIGH,
        "critical": UrgencyLevel.CRITICAL,
    }
    urgency = urgency_map.get(urgency_raw, UrgencyLevel.MEDIUM)

    # Format requirements
    requirements = extracted.get("requirements", [])
    if isinstance(requirements, str):
        requirements = [requirements]

    # Format evidence
    evidence = extracted.get("evidence", [])
    if isinstance(evidence, str):
        evidence = [evidence]

    # category/subcategory/buyer_name/buyer_organization/location/currency come
    # from free-text AI extraction (unbounded) or raw ingester data, but their
    # columns are length-limited VARCHARs — an over-length value crashes the
    # INSERT (and, worse, poisons the whole batch's DB session) rather than
    # just failing validation. Truncate defensively instead of trusting the
    # source data to already fit.
    def _capped(value: Optional[str], max_len: int) -> Optional[str]:
        return value[:max_len] if value else value

    source_url = signal.raw_data.get("source_url") if signal.raw_data else None
    if source_url and len(source_url) > 500:
        # A truncated URL wouldn't resolve anyway — dropping it is more honest
        # than storing a broken link (Google News redirect URLs routinely
        # exceed 500 characters).
        source_url = None

    opportunity = Opportunity(
        organization_id=signal.organization_id,  # SEC-5: Inherit org from signal
        signal_id=signal.id,
        country_code=signal.country_code,
        title=signal.title,
        description=signal.description[:2000],
        category=_capped(extracted.get("category", "general"), 100),
        subcategory=_capped(extracted.get("subcategory"), 100),
        intent_score=classification["intent_score"],
        confidence=classification["confidence"],
        urgency=urgency,
        buyer_name=_capped(extracted.get("buyer_name"), 255),
        buyer_organization=_capped(extracted.get("buyer_organization"), 255),
        location=_capped(extracted.get("location"), 255),
        estimated_value_min=extracted.get("estimated_value_min"),
        estimated_value_max=extracted.get("estimated_value_max"),
        currency=_capped(extracted.get("currency"), 3),
        deadline=extracted.get("deadline"),
        requirements=requirements,
        why_now=extracted.get("why_now"),
        recommended_action=extracted.get("recommended_action"),
        evidence=evidence,
        market_context=extracted.get("market_context", {}),
        source_url=source_url,
        status=OpportunityStatus.VALIDATED,
    )

    return opportunity
