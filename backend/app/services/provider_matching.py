"""Provider Matching Engine.

Matches opportunities with relevant providers based on:
- Service fit: category/services alignment
- Geographic fit: location overlap
- Project size fit: value range compatibility
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Opportunity, Provider, ProviderMatch


async def match_opportunity_to_providers(
    db: AsyncSession, opportunity: Opportunity
) -> list[ProviderMatch]:
    """Find and score all relevant providers for an opportunity."""
    # Get active providers in the same country
    result = await db.execute(
        select(Provider).where(
            Provider.is_active == True,
            Provider.country_codes.contains(opportunity.country_code),
        )
    )
    providers = list(result.scalars().all())

    matches = []
    for provider in providers:
        match_score = _calculate_match(opportunity, provider)
        if match_score["total_score"] > 0.1:  # Minimum threshold
            # Upsert — update if match already exists for this pair
            existing_result = await db.execute(
                select(ProviderMatch).where(
                    ProviderMatch.opportunity_id == opportunity.id,
                    ProviderMatch.provider_id == provider.id,
                )
            )
            existing_match = existing_result.scalar_one_or_none()
            if existing_match:
                existing_match.service_fit = match_score["service_fit"]
                existing_match.geographic_fit = match_score["geographic_fit"]
                existing_match.project_size_fit = match_score["project_size_fit"]
                existing_match.total_score = match_score["total_score"]
                existing_match.reasoning = match_score["reasoning"]
                matches.append(existing_match)
            else:
                match = ProviderMatch(
                    opportunity_id=opportunity.id,
                    provider_id=provider.id,
                    service_fit=match_score["service_fit"],
                    geographic_fit=match_score["geographic_fit"],
                    project_size_fit=match_score["project_size_fit"],
                    total_score=match_score["total_score"],
                    reasoning=match_score["reasoning"],
                )
                db.add(match)
                matches.append(match)

    await db.flush()
    return matches


def _calculate_match(
    opportunity: Opportunity, provider: Provider
) -> dict:
    """Calculate match score between an opportunity and a provider."""
    opp_category = opportunity.category.lower()
    opp_location = (opportunity.location or "").lower()

    # --- Service Fit (0-1) ---
    provider_categories = [
        c.lower() for c in (provider.categories or [])
    ]
    provider_services = [
        s.lower() for s in (provider.services or [])
    ]

    if opp_category in provider_categories:
        service_fit = 1.0
    elif any(opp_category in cat for cat in provider_categories):
        service_fit = 0.7
    elif any(cat in opp_category for cat in provider_categories):
        service_fit = 0.5
    else:
        # Check if any service keyword matches
        service_fit = 0.2 if provider_services else 0.1

    # --- Geographic Fit (0-1) ---
    provider_locations = [
        loc.lower() for loc in (provider.locations or [])
    ]
    provider_countries = [
        c.upper() for c in (provider.country_codes or [])
    ]

    if opportunity.country_code in provider_countries:
        if any(opp_location in loc for loc in provider_locations):
            geographic_fit = 1.0
        elif provider_locations:
            geographic_fit = 0.7  # Country match but no city match
        else:
            geographic_fit = 0.5  # Country match only
    else:
        geographic_fit = 0.1

    # --- Project Size Fit (0-1) ---
    opp_value = opportunity.estimated_value_min or 0
    prov_min = provider.min_project_value or 0
    prov_max = provider.max_project_value or float("inf")

    if opp_value == 0:
        project_size_fit = 0.5  # Unknown value, neutral
    elif prov_min <= opp_value <= prov_max:
        project_size_fit = 1.0
    elif opp_value < prov_min:
        # Opportunity smaller than provider's minimum
        ratio = opp_value / prov_min if prov_min > 0 else 0
        project_size_fit = max(0.1, ratio)
    else:
        # Opportunity larger than provider's maximum
        ratio = prov_max / opp_value if opp_value > 0 else 0
        project_size_fit = max(0.1, ratio)

    # --- Total Score (weighted) ---
    total_score = (
        service_fit * 0.5
        + geographic_fit * 0.25
        + project_size_fit * 0.25
    )

    # --- Reasoning ---
    reasoning_parts = []
    if service_fit >= 0.7:
        reasoning_parts.append(f"Strong service/category alignment ({service_fit:.0%})")
    elif service_fit >= 0.4:
        reasoning_parts.append(f"Moderate service alignment ({service_fit:.0%})")
    else:
        reasoning_parts.append(f"Limited service alignment ({service_fit:.0%})")

    if geographic_fit >= 0.7:
        reasoning_parts.append(f"Good geographic fit ({geographic_fit:.0%})")
    elif geographic_fit >= 0.4:
        reasoning_parts.append(f"Some geographic overlap ({geographic_fit:.0%})")
    else:
        reasoning_parts.append(f"Geographic mismatch ({geographic_fit:.0%})")

    if project_size_fit >= 0.7:
        reasoning_parts.append(f"Project size well-matched ({project_size_fit:.0%})")
    elif project_size_fit >= 0.4:
        reasoning_parts.append(f"Project size within range ({project_size_fit:.0%})")
    else:
        reasoning_parts.append(f"Project size mismatch ({project_size_fit:.0%})")

    return {
        "service_fit": round(service_fit, 3),
        "geographic_fit": round(geographic_fit, 3),
        "project_size_fit": round(project_size_fit, 3),
        "total_score": round(total_score, 3),
        "reasoning": "; ".join(reasoning_parts),
    }
