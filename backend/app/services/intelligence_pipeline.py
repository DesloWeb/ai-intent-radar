"""Core AI Intelligence Pipeline.

Processes signals through:
1. Intent classification
2. Opportunity extraction
3. Scoring & validation
4. Explanation generation
5. Opportunity creation
"""
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

    opportunity = Opportunity(
        organization_id=signal.organization_id,  # SEC-5: Inherit org from signal
        signal_id=signal.id,
        country_code=signal.country_code,
        title=signal.title,
        description=signal.description[:2000],
        category=extracted.get("category", "general"),
        subcategory=extracted.get("subcategory"),
        intent_score=classification["intent_score"],
        confidence=classification["confidence"],
        urgency=urgency,
        buyer_name=extracted.get("buyer_name"),
        buyer_organization=extracted.get("buyer_organization"),
        location=extracted.get("location"),
        estimated_value_min=extracted.get("estimated_value_min"),
        estimated_value_max=extracted.get("estimated_value_max"),
        currency=extracted.get("currency"),
        deadline=extracted.get("deadline"),
        requirements=requirements,
        why_now=extracted.get("why_now"),
        recommended_action=extracted.get("recommended_action"),
        evidence=evidence,
        market_context=extracted.get("market_context", {}),
        status=OpportunityStatus.VALIDATED,
    )

    return opportunity
