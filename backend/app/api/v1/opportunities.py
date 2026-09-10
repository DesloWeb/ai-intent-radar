"""Opportunity management API endpoints."""
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.models import User
from app.schemas.schemas import (
    OpportunityListResponse,
    OpportunityResponse,
)
from app.services.opportunity_service import (
    DEFAULT_MAX_AGE_DAYS,
    expire_stale_opportunities,
    get_opportunity_by_id,
    list_opportunities,
)

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("", response_model=OpportunityListResponse)
async def list_opps(
    country_code: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    min_intent_score: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List opportunities with filtering and pagination."""
    # SEC-5: Scope by organization
    opportunities, total = await list_opportunities(
        db,
        organization_id=user.organization_id,
        country_code=country_code,
        category=category,
        urgency=urgency,
        min_intent_score=min_intent_score,
        status=status,
        page=page,
        per_page=per_page,
    )
    return OpportunityListResponse(
        opportunities=opportunities,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/expire")
async def expire_opportunities(
    max_age_days: int = Query(
        DEFAULT_MAX_AGE_DAYS,
        ge=1,
        description="Opportunities older than this with no passed deadline are also expired",
    ),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    """Mark stale opportunities (deadline passed, or too old with no deadline)
    as expired. Platform-wide — not scoped to the caller's organization."""
    from app.services.audit_service import audit

    result = await expire_stale_opportunities(db, max_age_days=max_age_days)
    await audit(
        db, user.organization_id, user.id,
        "opportunity:expire", "opportunity", None,
        result,
    )
    await db.commit()
    return result


# IMPORTANT: this route must stay above /{opportunity_id} — otherwise
# "/opportunities/expire" would be swallowed by the dynamic route and fail
# UUID parsing instead of hitting this handler.
@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single opportunity with full details."""
    opp = await get_opportunity_by_id(
        db, uuid.UUID(opportunity_id), organization_id=user.organization_id
    )
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp
