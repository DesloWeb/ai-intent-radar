"""Provider Matching Engine.

Matches opportunities with relevant providers (businesses or individuals) based on:

Business scoring:
  - Service fit (50%): category/services alignment
  - Geographic fit (25%): location overlap
  - Project size fit (25%): value range compatibility

Individual scoring:
  - Skill fit (50%): skills vs opportunity requirements/category
  - Geographic fit (25%): location overlap
  - Rate fit (25%): hourly rate vs estimated opportunity value
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Opportunity, Provider, ProviderMatch


async def match_opportunity_to_providers(
    db: AsyncSession, opportunity: Opportunity
) -> list[ProviderMatch]:
    """Find and score all active providers for an opportunity."""
    result = await db.execute(
        select(Provider).where(
            Provider.is_active == True,
            Provider.country_codes.contains(opportunity.country_code),
        )
    )
    providers = list(result.scalars().all())

    matches = []
    for provider in providers:
        if provider.provider_type == "individual":
            match_score = _calculate_individual_match(opportunity, provider)
        else:
            match_score = _calculate_business_match(opportunity, provider)

        if match_score["total_score"] > 0.1:
            # Upsert — update existing match if it exists
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
    # Return sorted by score descending
    return sorted(matches, key=lambda m: m.total_score, reverse=True)


# ---------------------------------------------------------------------------
# Business matching
# ---------------------------------------------------------------------------

def _calculate_business_match(opportunity: Opportunity, provider: Provider) -> dict:
    """Score a business provider against an opportunity."""
    opp_category = opportunity.category.lower()
    opp_location = (opportunity.location or "").lower()

    # --- Service Fit (50%) ---
    provider_categories = [c.lower() for c in (provider.categories or [])]
    provider_services = [s.lower() for s in (provider.services or [])]

    if opp_category in provider_categories:
        service_fit = 1.0
    elif any(opp_category in cat for cat in provider_categories):
        service_fit = 0.7
    elif any(cat in opp_category for cat in provider_categories):
        service_fit = 0.5
    else:
        service_fit = 0.2 if provider_services else 0.1

    # --- Geographic Fit (25%) ---
    geographic_fit = _geo_fit(opportunity, provider, opp_location)

    # --- Project Size Fit (25%) ---
    opp_value = opportunity.estimated_value_min or 0
    prov_min = provider.min_project_value or 0
    prov_max = provider.max_project_value or float("inf")

    if opp_value == 0:
        project_size_fit = 0.5
    elif prov_min <= opp_value <= prov_max:
        project_size_fit = 1.0
    elif opp_value < prov_min:
        ratio = opp_value / prov_min if prov_min > 0 else 0
        project_size_fit = max(0.1, ratio)
    else:
        ratio = prov_max / opp_value if opp_value > 0 else 0
        project_size_fit = max(0.1, ratio)

    total_score = service_fit * 0.5 + geographic_fit * 0.25 + project_size_fit * 0.25

    reasoning = _build_reasoning(
        service_fit, geographic_fit, project_size_fit,
        service_label="service/category alignment",
        size_label="project size",
    )

    return {
        "service_fit": round(service_fit, 3),
        "geographic_fit": round(geographic_fit, 3),
        "project_size_fit": round(project_size_fit, 3),
        "total_score": round(total_score, 3),
        "reasoning": reasoning,
    }


# ---------------------------------------------------------------------------
# Individual matching
# ---------------------------------------------------------------------------

def _calculate_individual_match(opportunity: Opportunity, provider: Provider) -> dict:
    """Score an individual provider against an opportunity.

    Uses skills instead of services/categories, and hourly rate instead of
    project value range.
    """
    opp_category = opportunity.category.lower()
    opp_location = (opportunity.location or "").lower()

    # Combine opportunity signals for skill matching
    opp_text = " ".join([
        opp_category,
        opportunity.title.lower(),
        (opportunity.description or "").lower()[:300],
        " ".join(r.lower() for r in (opportunity.requirements or [])),
    ])

    # --- Skill Fit (50%) ---
    provider_skills = [s.lower() for s in (provider.skills or [])]
    provider_categories = [c.lower() for c in (provider.categories or [])]
    all_tags = provider_skills + provider_categories

    if not all_tags:
        service_fit = 0.1
    else:
        matched = sum(1 for tag in all_tags if tag in opp_text)
        # Partial word matching — "python" matches "python developer"
        partial = sum(
            1 for tag in all_tags
            if any(tag in word or word in tag for word in opp_text.split())
            and tag not in opp_text
        )
        hit_rate = (matched + partial * 0.5) / len(all_tags)
        service_fit = min(1.0, 0.2 + hit_rate * 0.8)

    # --- Geographic Fit (25%) ---
    geographic_fit = _geo_fit(opportunity, provider, opp_location)

    # --- Rate Fit (25%) — individual rate vs opportunity implied budget ---
    # Estimate implied hourly from project value (assumes ~500hr engagement)
    opp_value = opportunity.estimated_value_min or 0
    implied_hourly = opp_value / 500 if opp_value > 0 else 0

    rate_min = provider.hourly_rate_min or 0
    rate_max = provider.hourly_rate_max or float("inf")

    if implied_hourly == 0:
        # No value signal — neutral but slightly positive (don't penalise)
        project_size_fit = 0.6
    elif rate_min <= implied_hourly <= rate_max:
        project_size_fit = 1.0
    elif implied_hourly < rate_min:
        # Budget below individual's minimum rate
        ratio = implied_hourly / rate_min if rate_min > 0 else 0
        project_size_fit = max(0.1, ratio)
    else:
        # Budget above individual's maximum — they could upscale
        project_size_fit = 0.8

    total_score = service_fit * 0.5 + geographic_fit * 0.25 + project_size_fit * 0.25

    # Add availability note to reasoning
    availability_note = ""
    if provider.availability:
        availability_map = {
            "full_time": "available full-time",
            "part_time": "available part-time",
            "contract": "available for contract",
            "weekends": "available weekends",
        }
        availability_note = f"; {availability_map.get(provider.availability, provider.availability)}"

    verified_note = " ✓ Verified individual" if provider.verified else ""

    reasoning = _build_reasoning(
        service_fit, geographic_fit, project_size_fit,
        service_label="skill alignment",
        size_label="rate fit",
    ) + availability_note + verified_note

    return {
        "service_fit": round(service_fit, 3),
        "geographic_fit": round(geographic_fit, 3),
        "project_size_fit": round(project_size_fit, 3),
        "total_score": round(total_score, 3),
        "reasoning": reasoning,
    }


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _geo_fit(opportunity: Opportunity, provider: Provider, opp_location: str) -> float:
    """Calculate geographic fit score."""
    provider_locations = [loc.lower() for loc in (provider.locations or [])]
    provider_countries = [c.upper() for c in (provider.country_codes or [])]

    if opportunity.country_code not in provider_countries:
        return 0.1

    if not opp_location:
        return 0.6  # Country match, no city to compare

    # City/state level match
    if any(opp_location in loc or loc in opp_location for loc in provider_locations):
        return 1.0
    elif provider_locations:
        return 0.7  # Country match, different city
    else:
        return 0.5  # Country match only


def _build_reasoning(
    service_fit: float,
    geographic_fit: float,
    project_size_fit: float,
    service_label: str = "service alignment",
    size_label: str = "project size",
) -> str:
    parts = []

    if service_fit >= 0.7:
        parts.append(f"Strong {service_label} ({service_fit:.0%})")
    elif service_fit >= 0.4:
        parts.append(f"Moderate {service_label} ({service_fit:.0%})")
    else:
        parts.append(f"Limited {service_label} ({service_fit:.0%})")

    if geographic_fit >= 0.7:
        parts.append(f"Good geographic fit ({geographic_fit:.0%})")
    elif geographic_fit >= 0.4:
        parts.append(f"Some geographic overlap ({geographic_fit:.0%})")
    else:
        parts.append(f"Geographic mismatch ({geographic_fit:.0%})")

    if project_size_fit >= 0.7:
        parts.append(f"{size_label.capitalize()} well-matched ({project_size_fit:.0%})")
    elif project_size_fit >= 0.4:
        parts.append(f"{size_label.capitalize()} within range ({project_size_fit:.0%})")
    else:
        parts.append(f"{size_label.capitalize()} mismatch ({project_size_fit:.0%})")

    return "; ".join(parts)
