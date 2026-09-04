"""Provider management and matching API endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Opportunity, Provider, ProviderMatch, User
from app.schemas.schemas import (
    ProviderCreate,
    ProviderMatchResponse,
    ProviderResponse,
)
from app.services.provider_matching import match_opportunity_to_providers

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.post("", response_model=ProviderResponse, status_code=201)
async def create_provider(
    payload: ProviderCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register a new provider/business."""
    provider = Provider(
        organization_id=user.organization_id,
        name=payload.name,
        description=payload.description,
        services=payload.services,
        categories=payload.categories,
        locations=payload.locations,
        country_codes=payload.country_codes,
        min_project_value=payload.min_project_value,
        max_project_value=payload.max_project_value,
    )
    db.add(provider)
    await db.flush()
    return provider


@router.get("", response_model=list[ProviderResponse])
async def list_providers(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List providers in the current organization."""
    result = await db.execute(
        select(Provider).where(
            Provider.organization_id == user.organization_id,
            Provider.is_active == True,
        )
    )
    return list(result.scalars().all())


@router.post("/{opportunity_id}/match", response_model=list[ProviderMatchResponse])
async def match_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Run provider matching for an opportunity."""
    from uuid import UUID
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == UUID(opportunity_id))
    )
    opportunity = result.scalar_one_or_none()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    matches = await match_opportunity_to_providers(db, opportunity)
    return matches


@router.get("/{opportunity_id}/matches", response_model=list[ProviderMatchResponse])
async def get_matches(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get existing matches for an opportunity."""
    from uuid import UUID
    result = await db.execute(
        select(ProviderMatch).where(
            ProviderMatch.opportunity_id == UUID(opportunity_id)
        )
    )
    return list(result.scalars().all())
