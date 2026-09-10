"""Opportunity CRUD and filtering service."""
from typing import List, Optional, Tuple, Dict
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Opportunity, OpportunityStatus

# Terminal statuses an opportunity can already be in — never overwrite these
# with EXPIRED, they represent a real outcome, not staleness.
_TERMINAL_STATUSES = (
    OpportunityStatus.WON,
    OpportunityStatus.LOST,
    OpportunityStatus.DISMISSED,
    OpportunityStatus.EXPIRED,
)

# Statuses hidden from the default (no explicit status filter) list view —
# same convention dashboard.py already uses for its own queries. WON/LOST
# stay visible by default since they're outcomes a user likely still wants
# to see; DISMISSED/EXPIRED are the ones that just clutter the list.
_TERMINAL_HIDDEN_STATUSES = (OpportunityStatus.DISMISSED, OpportunityStatus.EXPIRED)

# Fallback cutoff for opportunities with no extracted deadline — the buying
# window described in VISION.md is typically 30-90 days, so anything older
# than this without a firmer signal is treated as stale.
DEFAULT_MAX_AGE_DAYS = 30


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
    else:
        # No explicit status requested — default view excludes dismissed/expired
        # so stale opportunities don't clutter the list. Pass status=expired (or
        # dismissed) explicitly to see them.
        filters.append(Opportunity.status.notin_(_TERMINAL_HIDDEN_STATUSES))

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
            Opportunity.created_at.desc(),
            Opportunity.intent_score.desc(),
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


async def expire_stale_opportunities(
    db: AsyncSession,
    max_age_days: int = DEFAULT_MAX_AGE_DAYS,
) -> Dict[str, int]:
    """Mark stale opportunities as EXPIRED.

    Two independent conditions, either of which qualifies an opportunity for
    expiry (never touches WON/LOST/DISMISSED/EXPIRED — those are real outcomes):
      - deadline has passed (only covers opportunities with an extracted deadline)
      - created more than `max_age_days` ago, regardless of deadline (catches
        opportunities where no deadline was ever extracted)

    This is a platform-wide maintenance operation, not scoped to one org —
    every org's stale opportunities get cleaned up in the same pass.
    """
    now = datetime.now(timezone.utc)
    age_cutoff = now - timedelta(days=max_age_days)

    not_terminal = Opportunity.status.notin_(_TERMINAL_STATUSES)
    stale = or_(
        and_(Opportunity.deadline.isnot(None), Opportunity.deadline < now),
        Opportunity.created_at < age_cutoff,
    )

    # Count before updating so the caller gets a meaningful number back —
    # UPDATE's rowcount isn't reliably reported across every async driver.
    count_query = select(func.count(Opportunity.id)).where(not_terminal, stale)
    expired_count = (await db.execute(count_query)).scalar() or 0

    if expired_count:
        await db.execute(
            update(Opportunity)
            .where(not_terminal, stale)
            .values(status=OpportunityStatus.EXPIRED)
        )

    return {"expired": expired_count, "max_age_days": max_age_days}
