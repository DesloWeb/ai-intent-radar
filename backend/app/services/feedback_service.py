"""User feedback and learning service.

Tracks user actions (save, dismiss, contact, won/lost) and uses
outcomes to improve future scoring.
"""
from typing import Dict, List, Optional
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    FeedbackType,
    Opportunity,
    OpportunityStatus,
    User,
    UserFeedback,
)


async def submit_feedback(
    db: AsyncSession,
    user: User,
    opportunity_id: uuid.UUID,
    feedback_type: str,
    notes: Optional[str] = None,
    outcome_value: Optional[float] = None,
) -> UserFeedback:
    """Record user feedback on an opportunity."""
    # Verify opportunity exists
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opportunity = result.scalar_one_or_none()
    if not opportunity:
        raise ValueError("Opportunity not found")

    # Prevent duplicate feedback of same type
    existing = await db.execute(
        select(UserFeedback).where(
            UserFeedback.user_id == user.id,
            UserFeedback.opportunity_id == opportunity_id,
            UserFeedback.feedback_type == feedback_type,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Feedback already submitted")

    feedback = UserFeedback(
        user_id=user.id,
        organization_id=user.organization_id,
        opportunity_id=opportunity_id,
        feedback_type=feedback_type,
        notes=notes,
        outcome_value=outcome_value,
    )
    db.add(feedback)

    # Update opportunity status based on feedback
    status_map = {
        "saved": OpportunityStatus.EXPOSED,
        "dismissed": OpportunityStatus.DISMISSED,
        "contacted": OpportunityStatus.CONTACTED,
        "won": OpportunityStatus.WON,
        "lost": OpportunityStatus.LOST,
    }
    new_status = status_map.get(feedback_type)
    if new_status:
        opportunity.status = new_status

    await db.flush()
    return feedback


async def get_feedback_stats(
    db: AsyncSession,
    organization_id: uuid.UUID,
) -> dict:
    """Get aggregated feedback statistics for an organization."""
    result = await db.execute(
        select(
            UserFeedback.feedback_type,
            func.count(UserFeedback.id).label("count"),
        )
        .where(UserFeedback.organization_id == organization_id)
        .group_by(UserFeedback.feedback_type)
    )

    stats = {}
    for row in result.all():
        stats[row.feedback_type] = row.count

    # Calculate win rate
    won = stats.get("won", 0)
    lost = stats.get("lost", 0)
    total_decided = won + lost
    stats["win_rate"] = round(won / total_decided, 3) if total_decided > 0 else None

    return stats


async def get_user_feedbacks(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
) -> List[UserFeedback]:
    """Get recent feedback for a user."""
    result = await db.execute(
        select(UserFeedback)
        .where(UserFeedback.user_id == user_id)
        .order_by(UserFeedback.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
