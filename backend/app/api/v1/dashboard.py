"""Dashboard API endpoints — aggregated intelligence view."""
from typing import Optional

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Opportunity, User, UserFeedback
from app.schemas.schemas import DashboardResponse
from app.services.opportunity_service import get_opportunity_counts

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    country_code: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the main intelligence dashboard data."""
    # SEC-5: Scope all queries by organization
    org_id = user.organization_id
    counts = await get_opportunity_counts(db, organization_id=org_id)

    # Top opportunities (highest intent score)
    top_query = select(Opportunity).where(
        Opportunity.organization_id == org_id,
        Opportunity.status.notin_(["dismissed", "expired"]),
    )
    if country_code:
        top_query = top_query.where(Opportunity.country_code == country_code)
    top_query = top_query.order_by(
        Opportunity.intent_score.desc()
    ).limit(10)
    top_result = await db.execute(top_query)
    top_opps = list(top_result.scalars().all())

    # Emerging demand (high intent from last 3 days)
    three_days = datetime.now(timezone.utc) - timedelta(days=3)
    emerging_query = (
        select(
            Opportunity.category,
            Opportunity.country_code,
            func.count(Opportunity.id).label("count"),
            func.avg(Opportunity.intent_score).label("avg_score"),
        )
        .where(
            and_(
                Opportunity.organization_id == org_id,
                Opportunity.created_at >= three_days,
                Opportunity.intent_score >= 0.5,
            )
        )
        .group_by(Opportunity.category, Opportunity.country_code)
        .order_by(func.avg(Opportunity.intent_score).desc())
        .limit(5)
    )
    if country_code:
        emerging_query = emerging_query.where(
            Opportunity.country_code == country_code
        )
    emerging_result = await db.execute(emerging_query)
    emerging = [
        {
            "category": r.category,
            "country_code": r.country_code,
            "count": r.count,
            "avg_score": round(float(r.avg_score or 0), 3),
        }
        for r in emerging_result.all()
    ]

    # Market trends
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    trends_query = (
        select(
            Opportunity.category,
            Opportunity.country_code,
            func.count(Opportunity.id).label("count"),
        )
        .where(
            and_(
                Opportunity.organization_id == org_id,
                Opportunity.created_at >= week_ago,
            )
        )
        .group_by(Opportunity.category, Opportunity.country_code)
        .order_by(func.count(Opportunity.id).desc())
        .limit(5)
    )
    trends_result = await db.execute(trends_query)
    trends = [
        {
            "category": r.category,
            "country_code": r.country_code,
            "count": r.count,
        }
        for r in trends_result.all()
    ]

    # Recent feedback
    fb_query = (
        select(UserFeedback)
        .where(UserFeedback.organization_id == user.organization_id)
        .order_by(UserFeedback.created_at.desc())
        .limit(10)
    )
    fb_result = await db.execute(fb_query)
    recent_feedback = list(fb_result.scalars().all())

    # Country summary
    country_query = (
        select(
            Opportunity.country_code,
            func.count(Opportunity.id).label("total"),
            func.avg(Opportunity.intent_score).label("avg_intent"),
        )
        .where(Opportunity.organization_id == org_id)
        .group_by(Opportunity.country_code)
    )
    country_result = await db.execute(country_query)
    countries_summary = [
        {
            "country_code": r.country_code,
            "total": r.total,
            "avg_intent_score": round(float(r.avg_intent or 0), 3),
        }
        for r in country_result.all()
    ]

    return DashboardResponse(
        total_opportunities=counts["total"],
        high_priority_count=counts["high_priority"],
        new_this_week=counts["new_this_week"],
        countries_summary=countries_summary,
        top_opportunities=top_opps,
        emerging_demand=emerging,
        market_trends=trends,
        recent_feedback=recent_feedback,
        intent_distribution=counts.get("intent_distribution", {}),
        urgency_distribution=counts.get("by_urgency", {}),
    )
