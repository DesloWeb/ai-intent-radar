"""Market Intelligence service.

Provides aggregated market insights:
- Category trends
- Geographic demand patterns
- Growth rates
- Emerging demand detection
"""
from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Opportunity, Signal, MarketTrend


async def get_market_summary(
    db: AsyncSession,
    country_code: Optional[str] = None,
) -> dict:
    """Get aggregated market intelligence summary."""
    base_filter = []
    if country_code:
        base_filter.append(Opportunity.country_code == country_code)

    # Total counts
    opp_query = select(func.count(Opportunity.id)).where(*base_filter)
    total_result = await db.execute(opp_query)
    total_opportunities = total_result.scalar() or 0

    sig_query = select(func.count(Signal.id))
    if country_code:
        sig_query = sig_query.where(Signal.country_code == country_code)
    sig_result = await db.execute(sig_query)
    total_signals = sig_result.scalar() or 0

    # Average scores
    avg_query = select(
        func.avg(Opportunity.intent_score).label("avg_intent"),
        func.avg(Opportunity.confidence).label("avg_confidence"),
    ).where(*base_filter)
    avg_result = await db.execute(avg_query)
    avg_row = avg_result.one()
    avg_intent = round(float(avg_row.avg_intent or 0), 3)
    avg_confidence = round(float(avg_row.avg_confidence or 0), 3)

    # Top categories
    cat_query = (
        select(
            Opportunity.category,
            func.count(Opportunity.id).label("count"),
            func.avg(Opportunity.intent_score).label("avg_score"),
        )
        .where(*base_filter)
        .group_by(Opportunity.category)
        .order_by(func.count(Opportunity.id).desc())
        .limit(10)
    )
    cat_result = await db.execute(cat_query)
    top_categories = [
        {
            "category": row.category,
            "count": row.count,
            "avg_score": round(float(row.avg_score or 0), 3),
        }
        for row in cat_result.all()
    ]

    # Recent trends
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    trend_query = (
        select(MarketTrend)
        .where(MarketTrend.period_start >= week_ago)
        .order_by(MarketTrend.period_start.desc())
        .limit(20)
    )
    trend_result = await db.execute(trend_query)
    recent_trends = list(trend_result.scalars().all())

    # Emerging demand (opportunities with high intent score from last 3 days)
    three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
    emerging_query = (
        select(
            Opportunity.category,
            Opportunity.country_code,
            func.count(Opportunity.id).label("count"),
            func.avg(Opportunity.intent_score).label("avg_score"),
        )
        .where(
            and_(
                Opportunity.created_at >= three_days_ago,
                Opportunity.intent_score >= 0.6,
                *base_filter,
            )
        )
        .group_by(Opportunity.category, Opportunity.country_code)
        .order_by(func.avg(Opportunity.intent_score).desc())
        .limit(10)
    )
    emerging_result = await db.execute(emerging_query)
    emerging_demand = [
        {
            "category": row.category,
            "country_code": row.country_code,
            "count": row.count,
            "avg_score": round(float(row.avg_score or 0), 3),
        }
        for row in emerging_result.all()
    ]

    return {
        "country_code": country_code or "all",
        "total_signals": total_signals,
        "total_opportunities": total_opportunities,
        "avg_intent_score": avg_intent,
        "avg_confidence": avg_confidence,
        "top_categories": top_categories,
        "recent_trends": recent_trends,
        "emerging_demand": emerging_demand,
    }


async def compute_market_trends(db: AsyncSession) -> List[MarketTrend]:
    """Compute and store market trend data for each country/category."""
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=7)
    period_end = now

    # Get all distinct country/category combinations with recent activity
    query = (
        select(
            Opportunity.country_code,
            Opportunity.category,
            func.count(Opportunity.id).label("opp_count"),
            func.avg(Opportunity.intent_score).label("avg_intent"),
            func.avg(Opportunity.confidence).label("avg_conf"),
        )
        .where(Opportunity.created_at >= period_start)
        .group_by(Opportunity.country_code, Opportunity.category)
    )

    result = await db.execute(query)
    trends = []

    for row in result.all():
        # Calculate growth rate (compare with previous period)
        prev_start = period_start - timedelta(days=7)
        prev_query = select(func.count(Opportunity.id)).where(
            and_(
                Opportunity.country_code == row.country_code,
                Opportunity.category == row.category,
                Opportunity.created_at >= prev_start,
                Opportunity.created_at < period_start,
            )
        )
        prev_result = await db.execute(prev_query)
        prev_count = prev_result.scalar() or 0
        growth_rate = 0.0
        if prev_count > 0:
            growth_rate = round((row.opp_count - prev_count) / prev_count, 3)

        trend = MarketTrend(
            country_code=row.country_code,
            category=row.category,
            period_start=period_start,
            period_end=period_end,
            signal_count=0,  # Will be computed separately
            opportunity_count=row.opp_count,
            avg_intent_score=round(float(row.avg_intent or 0), 3),
            avg_confidence=round(float(row.avg_conf or 0), 3),
            growth_rate=growth_rate,
            top_subcategories=[],
            metadata_extra={},
        )
        db.add(trend)
        trends.append(trend)

    await db.flush()
    return trends
