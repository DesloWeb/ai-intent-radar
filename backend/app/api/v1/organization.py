"""Organization settings — per-org target country selection.

Distinct from /countries (platform-wide: which markets exist at all,
admin-only). This is the per-organization layer: which of the
platform-enabled countries THIS org wants ingestion to run for.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.models import Country, Organization, User
from app.schemas.schemas import OrganizationResponse, OrganizationUpdate

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.get("", response_model=OrganizationResponse)
async def get_organization(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the current user's organization settings."""
    result = await db.execute(
        select(Organization).where(Organization.id == user.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.patch("", response_model=OrganizationResponse)
async def update_organization(
    payload: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Update which countries this org wants ingestion to run for (admin only).

    A country can only be selected if it's enabled at the platform level
    (Country.is_enabled) — an org can narrow the platform's supported
    markets, not expand beyond them.
    """
    result = await db.execute(
        select(Organization).where(Organization.id == user.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    codes = [c.upper() for c in payload.enabled_countries]
    country_result = await db.execute(
        select(Country).where(Country.code.in_(codes), Country.is_enabled == True)
    )
    valid_codes = {c.code for c in country_result.scalars().all()}
    invalid = set(codes) - valid_codes
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Country codes not available on this platform: {', '.join(sorted(invalid))}",
        )

    org.enabled_countries = codes
    await db.flush()
    return org
