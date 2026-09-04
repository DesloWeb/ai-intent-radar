"""Signal collection, normalization, and deduplication service."""
import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Signal, SignalStatus


def compute_dedup_hash(source: str, source_id: str, title: str) -> str:
    """Compute a hash for deduplication."""
    raw = f"{source}:{source_id}:{title}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()


def normalize_signal(raw_signal: dict) -> dict:
    """Normalize raw signal data into standard format."""
    title = raw_signal.get("title", "").strip()
    description = raw_signal.get("description", "").strip()
    country_code = raw_signal.get("country_code", "US").upper()
    source = raw_signal.get("source", "unknown").lower()
    source_id = raw_signal.get("source_id", "")

    # Normalize country code
    if len(country_code) != 2:
        country_code = "US"

    normalized = {
        "source": source,
        "source_id": source_id,
        "country_code": country_code,
        "title": title,
        "description": description,
        "raw_data": raw_signal.get("raw_data", {}),
        "normalized_data": {
            "original_source": source,
            "language": "en",
            "content_length": len(description),
        },
    }
    return normalized


async def ingest_signal(
    db: AsyncSession,
    raw_signal: dict,
    organization_id: uuid.UUID = None,
) -> Signal:
    """Ingest a new signal: normalize, deduplicate, and store."""
    normalized = normalize_signal(raw_signal)

    # Check for duplicates
    dedup_hash = compute_dedup_hash(
        normalized["source"],
        normalized["source_id"],
        normalized["title"],
    )

    existing = await db.execute(
        select(Signal).where(Signal.dedup_hash == dedup_hash)
    )
    existing_signal = existing.scalar_one_or_none()
    if existing_signal:
        return existing_signal

    signal = Signal(
        organization_id=organization_id,
        source=normalized["source"],
        source_id=normalized["source_id"],
        country_code=normalized["country_code"],
        title=normalized["title"],
        description=normalized["description"],
        raw_data=normalized["raw_data"],
        normalized_data=normalized["normalized_data"],
        status=SignalStatus.RAW,
        dedup_hash=dedup_hash,
    )
    db.add(signal)
    await db.flush()
    return signal


async def get_pending_signals(
    db: AsyncSession, limit: int = 50
) -> list[Signal]:
    """Get signals pending AI processing."""
    result = await db.execute(
        select(Signal)
        .where(Signal.status.in_([SignalStatus.RAW, SignalStatus.ERROR]))
        .where(Signal.retry_count < 3)
        .order_by(Signal.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())
