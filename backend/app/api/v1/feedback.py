"""User feedback API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import FeedbackCreate, FeedbackResponse
from app.services.feedback_service import (
    get_feedback_stats,
    get_user_feedbacks,
    submit_feedback,
)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    payload: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit feedback on an opportunity."""
    try:
        feedback = await submit_feedback(
            db,
            user,
            payload.opportunity_id,
            payload.feedback_type,
            payload.notes,
            payload.outcome_value,
        )
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[FeedbackResponse])
async def list_feedbacks(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current user's feedback history."""
    return await get_user_feedbacks(db, user.id)


@router.get("/stats")
async def feedback_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get aggregated feedback statistics."""
    return await get_feedback_stats(db, user.organization_id)
