"""Background worker for the intelligence pipeline.

Processes signals through the AI pipeline using Redis/RQ.
"""
import asyncio
import sys
import os

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import get_session_factory
from app.models.models import Signal, SignalStatus
from app.services.intelligence_pipeline import process_signal
from app.services.signal_service import get_pending_signals
from app.services.provider_matching import match_opportunity_to_providers
from app.services.market_intelligence import compute_market_trends


def process_pending_signals():
    """Process all pending signals through the AI pipeline."""
    asyncio.run(_process_pending_signals())


async def _process_pending_signals():
    async with get_session_factory()() as db:
        signals = await get_pending_signals(db, limit=50)
        processed = 0
        failed = 0

        for signal in signals:
            result = await process_signal(db, signal)
            if result and result.status in [SignalStatus.VALIDATED, SignalStatus.REJECTED]:
                processed += 1

                # If validated, run provider matching
                if result.status == SignalStatus.VALIDATED and result.opportunities:
                    for opp in result.opportunities:
                        await match_opportunity_to_providers(db, opp)
            else:
                failed += 1

        await db.commit()
        return {"processed": processed, "failed": failed}


def refresh_market_trends():
    """Recompute market trend data."""
    asyncio.run(_refresh_market_trends())


async def _refresh_market_trends():
    async with get_session_factory()() as db:
        trends = await compute_market_trends(db)
        await db.commit()
        return {"trends_computed": len(trends)}


if __name__ == "__main__":
    import redis
    from rq import Queue

    redis_conn = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    q = Queue(connection=redis_conn)

    print("Starting signal processing...")
    job = q.enqueue(process_pending_signals)
    print(f"Job enqueued: {job.id}")

    print("Starting market trends refresh...")
    job2 = q.enqueue(refresh_market_trends)
    print(f"Trends job enqueued: {job2.id}")
