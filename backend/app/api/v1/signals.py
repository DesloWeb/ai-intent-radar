"""Signal management API endpoints."""
import uuid
from typing import List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Signal, User
from app.schemas.schemas import SignalCreate, SignalResponse
from app.services.signal_service import ingest_signal

router = APIRouter(prefix="/signals", tags=["Signals"])


@router.post("", response_model=SignalResponse, status_code=201)
async def create_signal(
    payload: SignalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Ingest a new intelligence signal."""
    source_id = payload.source_id or str(uuid.uuid4())[:12]
    signal = await ingest_signal(db, {
        "source": payload.source,
        "source_id": source_id,
        "country_code": payload.country_code,
        "title": payload.title,
        "description": payload.description,
        "raw_data": payload.raw_data or {},
    })
    return signal


@router.get("", response_model=List[SignalResponse])
async def list_signals(
    country_code: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List signals with optional filtering."""
    query = select(Signal)
    if country_code:
        query = query.where(Signal.country_code == country_code)
    if status_filter:
        query = query.where(Signal.status == status_filter)

    offset = (page - 1) * per_page
    query = query.order_by(Signal.created_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single signal by ID."""
    from uuid import UUID
    result = await db.execute(
        select(Signal).where(Signal.id == UUID(signal_id))
    )
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


class ProcessResult(BaseModel):
    processed: int
    created: int
    rejected: int
    errors: int


@router.post("/process", response_model=ProcessResult)
async def process_pending_signals(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Process pending signals through the AI pipeline inline (for testing without Redis)."""
    from app.services.signal_service import get_pending_signals
    from app.services.intelligence_pipeline import process_signal
    from app.models.models import SignalStatus
    from sqlalchemy.orm import Session

    pending = await get_pending_signals(db, limit=limit)
    processed = 0
    created = 0
    rejected = 0
    errors = 0

    for signal in pending:
        try:
            result = await process_signal(db, signal)
            processed += 1
            if result and result.status == SignalStatus.VALIDATED:
                created += 1
            elif result and result.status == SignalStatus.REJECTED:
                rejected += 1
        except Exception:
            errors += 1

    await db.commit()
    return ProcessResult(processed=processed, created=created, rejected=rejected, errors=errors)
