"""Reddit Signal Ingester.

Polls configured subreddits for posts that express commercial intent:
  - Service requests ("looking for", "need a", "hiring")
  - Business announcements ("about to launch", "opening soon")
  - Investment/expansion signals ("just raised", "new location")

Uses the Reddit public JSON API — no OAuth required for read-only access.
Set REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET in .env for higher rate limits
(60 req/min authenticated vs 10 req/min unauthenticated).
"""
import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.core.config import settings
from app.core.database import get_session_factory
from app.services.signal_service import ingest_signal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Subreddit configuration
# Each entry: (subreddit, signal_type, min_score_threshold)
# ---------------------------------------------------------------------------

SUBREDDIT_CONFIG = [
    # Explicit service requests
    ("forhire",          "service_request",   0),
    ("hiring",           "hiring",            0),
    ("jobs",             "hiring",            5),
    # Small business / entrepreneur intent
    ("smallbusiness",    "business_intent",   5),
    ("Entrepreneur",     "business_intent",   10),
    ("startups",         "business_intent",   10),
    # Real estate & construction
    ("RealEstate",       "real_estate",       10),
    ("CommercialRealEstate", "real_estate",   2),
    # Technology procurement
    ("sysadmin",         "tech_procurement",  5),
    ("devops",           "tech_procurement",  5),
    # Finance signals
    ("personalfinance",  "finance",           10),
    ("investing",        "finance",           10),
]

# High-intent phrases — posts containing these are strong signals
HIGH_INTENT_PHRASES = [
    "looking for", "need a", "need an", "searching for",
    "anyone recommend", "can anyone suggest", "seeking",
    "hiring", "want to hire", "looking to hire",
    "accepting proposals", "taking applications",
    "want to build", "planning to build",
    "about to launch", "about to open", "about to start",
    "ready to", "going to need", "will need",
    "rfp", "rfq", "request for proposal", "bid",
    "just raised", "series a", "series b", "funded",
    "new location", "expanding to", "opening in",
]

MEDIUM_INTENT_PHRASES = [
    "anyone know", "recommendations", "suggestions",
    "considering", "thinking about", "exploring",
    "interested in", "would love", "help with",
    "freelancer", "contractor", "consultant",
]


def _has_intent(text: str) -> tuple[bool, str]:
    """Return (has_intent, matched_phrase) for a post's text."""
    lowered = text.lower()
    for phrase in HIGH_INTENT_PHRASES:
        if phrase in lowered:
            return True, phrase
    for phrase in MEDIUM_INTENT_PHRASES:
        if phrase in lowered:
            return True, phrase
    return False, ""


def _build_signal(post: dict, subreddit: str, signal_type: str) -> dict:
    """Convert a Reddit post dict into a signal payload."""
    title = post.get("title", "")
    selftext = post.get("selftext", "") or ""
    # Truncate body to keep signals manageable
    description = f"{title}\n\n{selftext[:1000]}".strip()

    author = post.get("author", "unknown")
    subreddit_name = post.get("subreddit", subreddit)
    post_id = post.get("id", "")
    permalink = f"https://reddit.com{post.get('permalink', '')}"
    score = post.get("score", 0)
    num_comments = post.get("num_comments", 0)
    created_utc = post.get("created_utc", 0)

    return {
        "source": "reddit",
        "source_id": f"reddit_{post_id}",
        "country_code": "US",
        "title": title[:500],
        "description": description,
        "raw_data": {
            "subreddit": subreddit_name,
            "signal_type": signal_type,
            "author": author,
            "score": score,
            "num_comments": num_comments,
            "permalink": permalink,
            "created_utc": created_utc,
            "source_url": permalink,
        },
    }


async def _get_reddit_token(client: httpx.AsyncClient) -> Optional[str]:
    """Get a Reddit OAuth token using client credentials."""
    if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
        return None
    try:
        r = await client.post(
            "https://www.reddit.com/api/v1/access_token",
            data={"grant_type": "client_credentials"},
            auth=(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET),
            headers={"User-Agent": settings.REDDIT_USER_AGENT},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception as e:
        logger.warning(f"Failed to get Reddit OAuth token: {e}")
        return None


async def fetch_subreddit_posts(
    client: httpx.AsyncClient,
    subreddit: str,
    limit: int = 25,
    after: Optional[str] = None,
    token: Optional[str] = None,
) -> list[dict]:
    """Fetch posts from a subreddit via the Reddit API."""
    params: dict = {"limit": limit, "raw_json": 1}
    if after:
        params["after"] = after

    headers = {"User-Agent": settings.REDDIT_USER_AGENT}

    if token:
        url = f"https://oauth.reddit.com/r/{subreddit}/new"
        headers["Authorization"] = f"Bearer {token}"
    else:
        url = f"https://www.reddit.com/r/{subreddit}/new.json"

    try:
        response = await client.get(url, params=params, headers=headers, timeout=15.0)
        if response.status_code == 403:
            logger.warning(
                f"Reddit returned 403 for r/{subreddit}. "
                "Reddit requires OAuth credentials for server-side access. "
                "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env."
            )
            return []
        response.raise_for_status()
        data = response.json()
        posts = data.get("data", {}).get("children", [])
        return [p["data"] for p in posts if p.get("kind") == "t3"]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            logger.warning(f"Rate limited on r/{subreddit} — backing off")
            await asyncio.sleep(5)
        else:
            logger.warning(f"HTTP {e.response.status_code} fetching r/{subreddit}: {e}")
        return []
    except Exception as e:
        logger.warning(f"Error fetching r/{subreddit}: {e}")
        return []


async def ingest_reddit_signals(
    limit_per_subreddit: int = 25,
    dry_run: bool = False,
) -> dict:
    """
    Poll configured subreddits and ingest intent signals.

    Args:
        limit_per_subreddit: Max posts to check per subreddit
        dry_run: If True, detect signals but don't write to DB

    Returns:
        Summary dict with counts
    """
    ingested = 0
    skipped = 0
    errors = 0
    subreddits_polled = 0

    async with httpx.AsyncClient() as client:
        # Get OAuth token if credentials are configured
        token = await _get_reddit_token(client)
        if not token:
            logger.warning(
                "No Reddit OAuth token available. "
                "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env to enable Reddit ingestion. "
                "Get free credentials at https://www.reddit.com/prefs/apps"
            )
            return {
                "subreddits_polled": 0,
                "ingested": 0,
                "skipped": 0,
                "errors": 0,
                "message": "Reddit credentials not configured. Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env.",
            }

        async with get_session_factory()() as db:
            for subreddit, signal_type, min_score in SUBREDDIT_CONFIG:
                try:
                    posts = await fetch_subreddit_posts(
                        client, subreddit,
                        limit=limit_per_subreddit,
                        token=token,
                    )
                    subreddits_polled += 1

                    for post in posts:
                        # Filter by minimum score (upvotes) to reduce noise
                        if post.get("score", 0) < min_score:
                            skipped += 1
                            continue

                        # Skip removed/deleted posts
                        if post.get("removed_by_category") or post.get("selftext") == "[removed]":
                            skipped += 1
                            continue

                        # Check for intent signals
                        title = post.get("title", "")
                        body = post.get("selftext", "") or ""
                        has_intent, matched = _has_intent(f"{title} {body}")

                        if not has_intent:
                            skipped += 1
                            continue

                        signal_payload = _build_signal(post, subreddit, signal_type)

                        if dry_run:
                            logger.info(
                                f"[DRY RUN] Would ingest: {title[:60]}... "
                                f"(matched: '{matched}', r/{subreddit})"
                            )
                            ingested += 1
                            continue

                        try:
                            signal = await ingest_signal(db, signal_payload)
                            ingested += 1
                            logger.debug(
                                f"Ingested signal {signal.id} from r/{subreddit}: "
                                f"{title[:50]}..."
                            )
                        except Exception as e:
                            logger.warning(f"Failed to ingest signal: {e}")
                            errors += 1

                    # Polite delay between subreddits to respect rate limits
                    await asyncio.sleep(1.0)

                except Exception as e:
                    logger.error(f"Error processing r/{subreddit}: {e}")
                    errors += 1

            if not dry_run:
                await db.commit()

    summary = {
        "subreddits_polled": subreddits_polled,
        "ingested": ingested,
        "skipped": skipped,
        "errors": errors,
    }
    logger.info(f"Reddit ingest complete: {summary}")
    return summary
