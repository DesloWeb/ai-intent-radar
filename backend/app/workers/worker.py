"""Background worker for the intelligence pipeline.

Jobs:
  - process_pending_signals: Run raw signals through the AI pipeline
  - ingest_reddit_signals:   Poll Reddit for new intent signals
  - refresh_market_trends:   Recompute market trend data

Run with RQ:
  rq worker --url redis://localhost:6379/0
Or trigger via the API:
  POST /api/v1/signals/process
"""
import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings
from app.core.database import get_session_factory
from app.models.models import Signal, SignalStatus
from app.services.intelligence_pipeline import process_signal
from app.services.signal_service import get_pending_signals
from app.services.provider_matching import match_opportunity_to_providers
from app.services.market_intelligence import compute_market_trends
from app.services.hn_ingester import ingest_hn_signals as _ingest_hn

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Signal pipeline
# ---------------------------------------------------------------------------

def process_pending_signals():
    """Process all pending raw signals through the AI pipeline."""
    return asyncio.run(_process_pending_signals())


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
        summary = {"processed": processed, "failed": failed}
        logger.info(f"Pipeline complete: {summary}")
        return summary


# ---------------------------------------------------------------------------
# HN ingestion
# ---------------------------------------------------------------------------

def ingest_from_hn(dry_run: bool = False):
    """Poll Hacker News and ingest intent signals. No credentials required."""
    return asyncio.run(
        _ingest_hn(
            limit_stories=50,
            limit_comments_per_thread=50,
            dry_run=dry_run,
        )
    )


def ingest_and_process_hn():
    """Ingest HN signals then immediately run the AI pipeline on them."""
    ingest_summary = ingest_from_hn()
    pipeline_summary = process_pending_signals()
    return {
        "ingest": ingest_summary,
        "pipeline": pipeline_summary,
    }


# ---------------------------------------------------------------------------
# Market trends
# ---------------------------------------------------------------------------

def refresh_market_trends():
    """Recompute market trend data."""
    return asyncio.run(_refresh_market_trends())


async def _refresh_market_trends():
    async with get_session_factory()() as db:
        trends = await compute_market_trends(db)
        await db.commit()
        summary = {"trends_computed": len(trends)}
        logger.info(f"Trends refreshed: {summary}")
        return summary


# ---------------------------------------------------------------------------
# CLI / manual trigger
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Intent Radar worker tasks")
    parser.add_argument(
        "task",
        choices=["pipeline", "hn", "hn_dry", "hn_and_process", "trends", "all"],
        help="Task to run",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    if args.task == "pipeline":
        print(process_pending_signals())
    elif args.task == "hn":
        print(ingest_from_hn())
    elif args.task == "hn_dry":
        print(ingest_from_hn(dry_run=True))
    elif args.task == "hn_and_process":
        print(ingest_and_process_hn())
    elif args.task == "trends":
        print(refresh_market_trends())
    elif args.task == "all":
        print("Ingesting HN signals...")
        print(ingest_from_hn())
        print("Running pipeline...")
        print(process_pending_signals())
        print("Refreshing trends...")
        print(refresh_market_trends())
