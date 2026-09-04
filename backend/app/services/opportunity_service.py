"""Opportunity CRUD and filtering service."""
from typing import List, Optional, Tuple, Dict
import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Opportunity, OpportunityStatus


async def list_opportunities(
    db: AsyncSession,
    organization_id: Optional[uuid.UUID] = None,
    country_code: Optional[str] = None,
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    min_intent_score: Optional[float] = None,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[Opportunity], int]:
    """List opportunities with filtering and pagination."""
    filters = []
    # SEC-5: Always filter by organization if provided
    if organization_id:
        filters.append(Opportunity.organization_id == organization_id)
    if country_code:
        filters.append(Opportunity.country_code == country_code)
    if category:
        filters.append(Opportunity.category == category)
    if urgency:
        filters.append(Opportunity.urgency == urgency)
    if min_intent_score is not None:
        filters.append(Opportunity.intent_score >= min_intent_score)
    if status:
        filters.append(Opportunity.status == status)

    where_clause = and_(*filters) if filters else True

    # Count
    count_query = select(func.count(Opportunity.id)).where(where_clause)
    total = (await db.execute(count_query)).scalar() or 0

    # Paginated results
    offset = (page - 1) * per_page
    query = (
        select(Opportunity)
        .where(where_clause)
        .order_by(
            Opportunity.intent_score.desc(),
            Opportunity.created_at.desc(),
        )
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(query)
    opportunities = list(result.scalars().all())

    return opportunities, total


async def get_opportunity_by_id(
    db: AsyncSession,
    opportunity_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = None,
) -> Optional[Opportunity]:
    """Get a single opportunity by ID, scoped by organization."""
    filters = [Opportunity.id == opportunity_id]
    if organization_id:
        filters.append(Opportunity.organization_id == organization_id)
    result = await db.execute(
        select(Opportunity).where(and_(*filters))
    )
    return result.scalar_one_or_none()


async def get_opportunity_counts(
    db: AsyncSession,
    organization_id: Optional[uuid.UUID] = None,
) -> dict:
    """Get opportunity counts by various dimensions."""
    # SEC-5: Scope by organization if provided
    base_filter = [Opportunity.organization_id == organization_id] if organization_id else []
    
    total = (
        await db.execute(
            select(func.count(Opportunity.id)).where(and_(*base_filter) if base_filter else True)
        )
    ).scalar() or 0

    high_priority = (
        await db.execute(
            select(func.count(Opportunity.id)).where(
                and_(*base_filter, Opportunity.intent_score >= 0.7) if base_filter else Opportunity.intent_score >= 0.7
            )
        )
    ).scalar() or 0

    from datetime import timedelta
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_this_week = (
        await db.execute(
            select(func.count(Opportunity.id)).where(
                and_(*base_filter, Opportunity.created_at >= week_ago) if base_filter else Opportunity.created_at >= week_ago
            )
        )
    ).scalar() or 0

    # By country
    country_query = (
        select(
            Opportunity.country_code,
            func.count(Opportunity.id).label("count"),
        )
        .where(and_(*base_filter) if base_filter else True)
        .group_by(Opportunity.country_code)
    )
    country_result = await db.execute(country_query)
    by_country = [
        {"country_code": row.country_code, "count": row.count}
        for row in country_result.all()
    ]

    # By urgency
    urgency_query = (
        select(
            Opportunity.urgency,
            func.count(Opportunity.id).label("count"),
        )
        .where(and_(*base_filter) if base_filter else True)
        .group_by(Opportunity.urgency)
    )
    urgency_result = await db.execute(urgency_query)
    by_urgency = {
        row.urgency: row.count for row in urgency_result.all()
    }

    # By intent score range
    intent_ranges = [
        ("high", 0.7, 1.0),
        ("medium", 0.35, 0.7),
        ("low", 0.0, 0.35),
    ]
    intent_distribution = {}
    for label, low, high in intent_ranges:
        count = (
            await db.execute(
                select(func.count(Opportunity.id)).where(
                    and_(*base_filter, Opportunity.intent_score >= low, Opportunity.intent_score < high) if base_filter else and_(Opportunity.intent_score >= low, Opportunity.intent_score < high)
                )
            )
        ).scalar() or 0
        intent_distribution[label] = count

    return {
        "total": total,
        "high_priority": high_priority,
        "new_this_week": new_this_week,
        "by_country": by_country,
        "by_urgency": by_urgency,
        "intent_distribution": intent_distribution,
    }
