"""Provider Brief API — shareable signed opportunity briefs.

Flow:
  1. User runs provider matching on an opportunity
  2. User calls POST /briefs to generate a signed link for a specific match
  3. System returns a public URL: /brief/{token}
  4. User sends the URL to the provider via email/WhatsApp/LinkedIn
  5. Provider opens the URL (no login required), sees the full brief
  6. Provider can click "I'm Interested" or "Not Interested"
  7. User sees the response in their dashboard
"""
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    Opportunity,
    Provider,
    ProviderBrief,
    ProviderMatch,
    User,
)

router = APIRouter(prefix="/briefs", tags=["Provider Briefs"])

BRIEF_EXPIRY_DAYS = 7


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class BriefCreate(BaseModel):
    opportunity_id: uuid.UUID
    provider_match_id: Optional[uuid.UUID] = None


class BriefResponse(BaseModel):
    id: uuid.UUID
    token: str
    opportunity_id: uuid.UUID
    provider_match_id: Optional[uuid.UUID] = None
    expires_at: datetime
    status: str
    view_count: int
    public_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicBriefResponse(BaseModel):
    """What the provider sees — no auth required."""
    opportunity_title: str
    opportunity_description: str
    opportunity_category: str
    opportunity_urgency: str
    opportunity_intent_score: float
    opportunity_confidence: float
    opportunity_why_now: Optional[str]
    opportunity_recommended_action: Optional[str]
    opportunity_requirements: list
    opportunity_evidence: list
    opportunity_source_url: Optional[str]
    opportunity_estimated_value_min: Optional[float]
    opportunity_estimated_value_max: Optional[float]
    opportunity_currency: Optional[str]
    opportunity_deadline: Optional[datetime]
    opportunity_buyer_organization: Optional[str]
    opportunity_location: Optional[str]
    # Match details
    match_score: Optional[float]
    match_reasoning: Optional[str]
    match_service_fit: Optional[float]
    match_geographic_fit: Optional[float]
    match_project_size_fit: Optional[float]
    # Provider details (if matched to a registered provider)
    provider_name: Optional[str]
    # Brief metadata
    brief_id: uuid.UUID
    status: str
    expires_at: datetime
    already_responded: bool


class ProviderInterestRequest(BaseModel):
    action: str  # "interested" | "not_interested"
    provider_name: str
    provider_email: str
    message: Optional[str] = None


# ---------------------------------------------------------------------------
# Authenticated endpoints (for the platform user)
# ---------------------------------------------------------------------------

@router.post("", response_model=BriefResponse, status_code=201)
async def generate_brief(
    payload: BriefCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate a shareable signed brief for a provider match."""
    # Verify opportunity belongs to this org
    result = await db.execute(
        select(Opportunity).where(
            Opportunity.id == payload.opportunity_id,
            Opportunity.organization_id == user.organization_id,
        )
    )
    opportunity = result.scalar_one_or_none()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # Verify match if provided
    match = None
    if payload.provider_match_id:
        match_result = await db.execute(
            select(ProviderMatch).where(
                ProviderMatch.id == payload.provider_match_id,
                ProviderMatch.opportunity_id == payload.opportunity_id,
            )
        )
        match = match_result.scalar_one_or_none()
        if not match:
            raise HTTPException(status_code=404, detail="Provider match not found")

    # Generate secure token
    token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(days=BRIEF_EXPIRY_DAYS)

    brief = ProviderBrief(
        organization_id=user.organization_id,
        created_by=user.id,
        opportunity_id=payload.opportunity_id,
        provider_match_id=payload.provider_match_id,
        token=token,
        expires_at=expires_at,
        status="pending",
    )

    # Pre-fill provider contact if we have a match with a known provider
    if payload.provider_match_id and match:
        prov_result = await db.execute(
            select(Provider).where(Provider.id == match.provider_id)
        )
        provider = prov_result.scalar_one_or_none()
        if provider:
            brief.provider_name = provider.name
    db.add(brief)
    await db.flush()
    await db.commit()

    # Build public URL
    base_url = str(request.base_url).rstrip("/")
    # For production, use the frontend URL
    import os
    frontend_url = os.getenv("FRONTEND_URL", "https://ai-intent-radar.vercel.app")
    public_url = f"{frontend_url}/brief/{token}"

    return BriefResponse(
        id=brief.id,
        token=brief.token,
        opportunity_id=brief.opportunity_id,
        provider_match_id=brief.provider_match_id,
        expires_at=brief.expires_at,
        status=brief.status,
        view_count=brief.view_count,
        public_url=public_url,
        created_at=brief.created_at,
    )


@router.get("", response_model=list[BriefResponse])
async def list_briefs(
    opportunity_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all briefs generated by this organisation."""
    import os
    frontend_url = os.getenv("FRONTEND_URL", "https://ai-intent-radar.vercel.app")

    query = select(ProviderBrief).where(
        ProviderBrief.organization_id == user.organization_id
    ).order_by(ProviderBrief.created_at.desc())

    if opportunity_id:
        query = query.where(ProviderBrief.opportunity_id == opportunity_id)

    result = await db.execute(query)
    briefs = result.scalars().all()

    return [
        BriefResponse(
            id=b.id,
            token=b.token,
            opportunity_id=b.opportunity_id,
            provider_match_id=b.provider_match_id,
            expires_at=b.expires_at,
            status=b.status,
            view_count=b.view_count,
            public_url=f"{frontend_url}/brief/{b.token}",
            created_at=b.created_at,
        )
        for b in briefs
    ]


# ---------------------------------------------------------------------------
# Public endpoints (no auth — token is the credential)
# ---------------------------------------------------------------------------

@router.get("/public/{token}", response_model=PublicBriefResponse)
async def get_public_brief(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Get brief data by token — public, no auth required."""
    result = await db.execute(
        select(ProviderBrief).where(ProviderBrief.token == token)
    )
    brief = result.scalar_one_or_none()

    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found or expired")

    if brief.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="This brief has expired")

    # Fetch opportunity
    opp_result = await db.execute(
        select(Opportunity).where(Opportunity.id == brief.opportunity_id)
    )
    opp = opp_result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # Fetch match if attached
    match = None
    provider = None
    if brief.provider_match_id:
        match_result = await db.execute(
            select(ProviderMatch).where(ProviderMatch.id == brief.provider_match_id)
        )
        match = match_result.scalar_one_or_none()

        if match:
            prov_result = await db.execute(
                select(Provider).where(Provider.id == match.provider_id)
            )
            provider = prov_result.scalar_one_or_none()

    # Track view
    brief.view_count += 1
    brief.last_viewed_at = datetime.now(timezone.utc)
    await db.commit()

    return PublicBriefResponse(
        opportunity_title=opp.title,
        opportunity_description=opp.description,
        opportunity_category=opp.category,
        opportunity_urgency=opp.urgency,
        opportunity_intent_score=opp.intent_score,
        opportunity_confidence=opp.confidence,
        opportunity_why_now=opp.why_now,
        opportunity_recommended_action=opp.recommended_action,
        opportunity_requirements=opp.requirements or [],
        opportunity_evidence=opp.evidence or [],
        opportunity_source_url=opp.source_url,
        opportunity_estimated_value_min=opp.estimated_value_min,
        opportunity_estimated_value_max=opp.estimated_value_max,
        opportunity_currency=opp.currency,
        opportunity_deadline=opp.deadline,
        opportunity_buyer_organization=opp.buyer_organization,
        opportunity_location=opp.location,
        match_score=match.total_score if match else None,
        match_reasoning=match.reasoning if match else None,
        match_service_fit=match.service_fit if match else None,
        match_geographic_fit=match.geographic_fit if match else None,
        match_project_size_fit=match.project_size_fit if match else None,
        provider_name=provider.name if provider else None,
        brief_id=brief.id,
        status=brief.status,
        expires_at=brief.expires_at,
        already_responded=brief.status != "pending",
    )


@router.post("/public/{token}/respond")
async def respond_to_brief(
    token: str,
    payload: ProviderInterestRequest,
    db: AsyncSession = Depends(get_db),
):
    """Provider responds to the brief — no auth required."""
    if payload.action not in ("interested", "not_interested"):
        raise HTTPException(status_code=400, detail="action must be 'interested' or 'not_interested'")

    result = await db.execute(
        select(ProviderBrief).where(ProviderBrief.token == token)
    )
    brief = result.scalar_one_or_none()

    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    if brief.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="This brief has expired")

    if brief.status != "pending":
        raise HTTPException(status_code=409, detail="You have already responded to this brief")

    brief.status = payload.action
    brief.provider_name = payload.provider_name
    brief.provider_email = payload.provider_email
    brief.provider_message = payload.message
    brief.responded_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "message": "Thank you for your response. The team will be in touch shortly.",
        "status": brief.status,
    }
