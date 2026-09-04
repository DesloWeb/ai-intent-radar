"""Market Intelligence API endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, MarketTrend
from app.schemas.schemas import MarketSummaryResponse, MarketTrendResponse
from app.services.market_intelligence import get_market_summary

router = APIRouter(prefix="/market-intelligence", tags=["Market Intelligence"])


@router.get("/summary", response_model=MarketSummaryResponse)
async def market_summary(
    country_code: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get aggregated market intelligence summary."""
    summary = await get_market_summary(db, country_code)
    return MarketSummaryResponse(
        country_code=summary["country_code"],
        total_signals=summary["total_signals"],
        total_opportunities=summary["total_opportunities"],
        avg_intent_score=summary["avg_intent_score"],
        avg_confidence=summary["avg_confidence"],
        top_categories=summary["top_categories"],
        recent_trends=summary["recent_trends"],
        emerging_demand=summary["emerging_demand"],
    )


@router.get("/trends", response_model=List[MarketTrendResponse])
async def market_trends(
    country_code: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get market trends over time."""
    query = select(MarketTrend).order_by(MarketTrend.period_start.desc()).limit(50)
    if country_code:
        query = query.where(MarketTrend.country_code == country_code)

    result = await db.execute(query)
    return list(result.scalars().all())
