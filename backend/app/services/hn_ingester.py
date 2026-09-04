"""Hacker News Signal Ingester.

Pulls commercial intent signals from Hacker News using the free, no-auth
Firebase API (https://hacker-news.firebaseio.com/v0/).

Sources tapped:
  1. Job stories    — direct hiring posts from companies
  2. Ask HN stories — community posts expressing needs, requests, intent
  3. Monthly "Who is hiring?" threads — hundreds of hiring signals per month
  4. Monthly "Freelancer? Seeking freelancer?" threads — service requests

No API key required. Rate limit: ~10k requests/minute (Firebase).
"""
import asyncio
import logging
import re
from typing import Optional

import httpx

from app.core.database import get_session_factory
from app.services.signal_service import ingest_signal

logger = logging.getLogger(__name__)

HN_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ITEM_URL = "https://news.ycombinator.com/item?id={id}"

# ---------------------------------------------------------------------------
# Intent phrase detection
# ---------------------------------------------------------------------------

HIGH_INTENT_PHRASES = [
    # Service requests
    "looking for", "need a", "need an", "searching for",
    "seeking", "want to hire", "looking to hire", "hiring",
    "accepting applications", "taking applications",
    # Build / launch intent
    "want to build", "planning to build", "about to launch",
    "about to open", "about to start", "ready to launch",
    "going to need", "will need", "need help with",
    # Procurement
    "rfp", "rfq", "request for proposal", "request for quote",
    "vendor", "contractor", "consultant", "freelancer",
    # Investment / expansion
    "just raised", "series a", "series b", "seed round", "funded",
    "new location", "expanding to", "opening in", "new office",
    # Direct asks
    "anyone recommend", "can anyone suggest", "recommendations for",
    "who is good at", "who can help",
]

MEDIUM_INTENT_PHRASES = [
    "considering", "thinking about", "exploring options",
    "interested in hiring", "open to", "would love to find",
    "struggling with", "need advice on", "help with",
    "partnership", "co-founder", "cofounder",
    "investing in", "budget for", "set aside for",
]

# Strip HTML tags from HN comment text
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_ENTITIES = {
    "&amp;": "&", "&lt;": "<", "&gt;": ">",
    "&quot;": '"', "&#x2F;": "/", "&#x27;": "'",
    "&apos;": "'",
}


def _clean_html(text: str) -> str:
    """Strip HTML tags and decode common entities."""
    if not text:
        return ""
    text = _HTML_TAG_RE.sub(" ", text)
    for entity, char in _HTML_ENTITIES.items():
        text = text.replace(entity, char)
    return " ".join(text.split())


def _has_intent(text: str) -> tuple[bool, str]:
    """Return (has_intent, matched_phrase)."""
    lowered = text.lower()
    for phrase in HIGH_INTENT_PHRASES:
        if phrase in lowered:
            return True, phrase
    for phrase in MEDIUM_INTENT_PHRASES:
        if phrase in lowered:
            return True, phrase
    return False, ""


def _detect_category(text: str) -> str:
    """Rough category detection from text."""
    lowered = text.lower()
    category_keywords = {
        "technology": ["software", "developer", "engineer", "devops", "cloud", "api",
                       "saas", "platform", "backend", "frontend", "fullstack", "ml", "ai"],
        "defense":    ["cybersecurity", "security", "pentest", "infosec", "soc", "siem"],
        "healthcare": ["health", "medical", "hipaa", "clinical", "pharma", "biotech"],
        "finance":    ["fintech", "banking", "payments", "crypto", "accounting", "cpa",
                       "bookkeeping", "tax", "financial"],
        "infrastructure": ["construction", "real estate", "facilities", "hardware",
                           "manufacturing", "logistics", "supply chain"],
        "consulting": ["consulting", "strategy", "advisory", "management", "analyst"],
        "education":  ["education", "training", "course", "bootcamp", "learning"],
        "energy":     ["energy", "solar", "renewable", "cleantech", "climate"],
        "marketing":  ["marketing", "seo", "growth", "content", "social media",
                       "copywriting", "design", "branding"],
    }
    scores = {cat: 0 for cat in category_keywords}
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in lowered:
                scores[cat] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "consulting"


# ---------------------------------------------------------------------------
# HN API helpers
# ---------------------------------------------------------------------------

async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> Optional[dict]:
    """Fetch a single HN item (story or comment)."""
    try:
        r = await client.get(f"{HN_BASE}/item/{item_id}.json", timeout=10.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.debug(f"Failed to fetch HN item {item_id}: {e}")
        return None


async def _fetch_story_ids(client: httpx.AsyncClient, feed: str, limit: int) -> list[int]:
    """Fetch story IDs from a HN feed (askstories, jobstories, newstories)."""
    try:
        r = await client.get(f"{HN_BASE}/{feed}.json", timeout=10.0)
        r.raise_for_status()
        ids = r.json()
        return ids[:limit] if isinstance(ids, list) else []
    except Exception as e:
        logger.warning(f"Failed to fetch HN {feed}: {e}")
        return []


async def _find_monthly_thread(
    client: httpx.AsyncClient,
    keyword: str,
    limit: int = 30,
) -> Optional[dict]:
    """Find the most recent monthly HN thread matching a keyword in title."""
    ids = await _fetch_story_ids(client, "askstories", limit)
    for sid in ids:
        item = await _fetch_item(client, sid)
        if item and keyword.lower() in (item.get("title") or "").lower():
            return item
        await asyncio.sleep(0.05)
    return None


def _story_to_signal(item: dict, source_type: str) -> Optional[dict]:
    """Convert an HN story item to a signal payload."""
    title = (item.get("title") or "").strip()
    body = _clean_html(item.get("text") or "")
    if not title:
        return None

    description = f"{title}\n\n{body}".strip()[:2000]
    item_id = item.get("id", "")
    score = item.get("score", 0)
    url = HN_ITEM_URL.format(id=item_id)

    return {
        "source": "hacker_news",
        "source_id": f"hn_{item_id}",
        "country_code": "US",
        "title": title[:500],
        "description": description,
        "raw_data": {
            "hn_id": item_id,
            "source_type": source_type,
            "score": score,
            "descendants": item.get("descendants", 0),
            "author": item.get("by", "unknown"),
            "source_url": url,
            "url": item.get("url", url),
        },
    }


def _comment_to_signal(comment: dict, thread_title: str, source_type: str) -> Optional[dict]:
    """Convert an HN comment (from monthly threads) to a signal payload."""
    text = _clean_html(comment.get("text") or "")
    if not text or len(text) < 50:
        return None

    item_id = comment.get("id", "")
    # First line of comment often contains company/role info
    first_line = text.split(".")[0][:120].strip()
    title = f"{thread_title[:60]} | {first_line}"

    return {
        "source": "hacker_news",
        "source_id": f"hn_{item_id}",
        "country_code": "US",
        "title": title[:500],
        "description": text[:2000],
        "raw_data": {
            "hn_id": item_id,
            "source_type": source_type,
            "author": comment.get("by", "unknown"),
            "source_url": HN_ITEM_URL.format(id=item_id),
            "parent_thread": thread_title,
        },
    }


# ---------------------------------------------------------------------------
# Main ingestion function
# ---------------------------------------------------------------------------

async def ingest_hn_signals(
    limit_stories: int = 50,
    limit_comments_per_thread: int = 50,
    dry_run: bool = False,
    min_score: int = 1,
) -> dict:
    """
    Fetch and ingest intent signals from Hacker News.

    Args:
        limit_stories: Max stories to check from ask/job feeds
        limit_comments_per_thread: Max comments to pull from monthly threads
        dry_run: Detect signals without writing to DB
        min_score: Minimum HN score to consider a story

    Returns:
        Summary dict with counts
    """
    ingested = 0
    skipped = 0
    errors = 0

    signals_to_ingest = []

    async with httpx.AsyncClient() as client:

        # ── 1. Job stories (direct company hiring posts) ──────────────────
        logger.info("Fetching HN job stories...")
        job_ids = await _fetch_story_ids(client, "jobstories", limit_stories)
        for sid in job_ids:
            item = await _fetch_item(client, sid)
            if not item:
                skipped += 1
                continue
            if (item.get("score") or 0) < min_score:
                skipped += 1
                continue
            title = item.get("title", "")
            body = _clean_html(item.get("text") or "")
            has_intent, matched = _has_intent(f"{title} {body}")
            # Job posts are inherently high intent — include all
            payload = _story_to_signal(item, "hn_job")
            if payload:
                signals_to_ingest.append(("job", payload, title))
            await asyncio.sleep(0.05)

        # ── 2. Ask HN stories (community requests/questions) ─────────────
        logger.info("Fetching Ask HN stories...")
        ask_ids = await _fetch_story_ids(client, "askstories", limit_stories)
        for sid in ask_ids:
            item = await _fetch_item(client, sid)
            if not item:
                skipped += 1
                continue
            if (item.get("score") or 0) < min_score:
                skipped += 1
                continue
            title = item.get("title", "")
            body = _clean_html(item.get("text") or "")
            has_intent, matched = _has_intent(f"{title} {body}")
            if not has_intent:
                skipped += 1
                continue
            payload = _story_to_signal(item, "hn_ask")
            if payload:
                signals_to_ingest.append(("ask", payload, f"{title} (matched: '{matched}')"))
            await asyncio.sleep(0.05)

        # ── 3. Monthly "Who is hiring?" thread comments ───────────────────
        logger.info("Looking for monthly 'Who is hiring?' thread...")
        hiring_thread = await _find_monthly_thread(client, "who is hiring", limit=30)
        if hiring_thread:
            thread_title = hiring_thread.get("title", "Who is hiring?")
            kids = (hiring_thread.get("kids") or [])[:limit_comments_per_thread]
            logger.info(f"Found '{thread_title}' — fetching {len(kids)} comments")
            for kid_id in kids:
                comment = await _fetch_item(client, kid_id)
                if not comment or comment.get("deleted") or comment.get("dead"):
                    skipped += 1
                    continue
                payload = _comment_to_signal(comment, thread_title, "hn_hiring_thread")
                if payload:
                    signals_to_ingest.append(("hiring_comment", payload, payload["title"]))
                await asyncio.sleep(0.05)
        else:
            logger.info("No 'Who is hiring?' thread found in recent Ask HN")

        # ── 4. Monthly "Freelancer? Seeking freelancer?" thread ───────────
        logger.info("Looking for monthly freelancer thread...")
        freelancer_thread = await _find_monthly_thread(client, "freelancer", limit=30)
        if freelancer_thread:
            thread_title = freelancer_thread.get("title", "Freelancer thread")
            kids = (freelancer_thread.get("kids") or [])[:limit_comments_per_thread]
            logger.info(f"Found '{thread_title}' — fetching {len(kids)} comments")
            for kid_id in kids:
                comment = await _fetch_item(client, kid_id)
                if not comment or comment.get("deleted") or comment.get("dead"):
                    skipped += 1
                    continue
                text = _clean_html(comment.get("text") or "")
                has_intent, matched = _has_intent(text)
                if not has_intent:
                    skipped += 1
                    continue
                payload = _comment_to_signal(comment, thread_title, "hn_freelancer_thread")
                if payload:
                    signals_to_ingest.append(("freelancer_comment", payload, payload["title"]))
                await asyncio.sleep(0.05)

    # ── Write to DB ───────────────────────────────────────────────────────
    if dry_run:
        logger.info(f"[DRY RUN] Would ingest {len(signals_to_ingest)} signals:")
        for stype, payload, label in signals_to_ingest:
            logger.info(f"  [{stype}] {label[:80]}")
        ingested = len(signals_to_ingest)
    else:
        async with get_session_factory()() as db:
            for stype, payload, label in signals_to_ingest:
                try:
                    await ingest_signal(db, payload)
                    ingested += 1
                    logger.debug(f"Ingested [{stype}]: {label[:60]}")
                except Exception as e:
                    logger.warning(f"Failed to ingest [{stype}] {label[:60]}: {e}")
                    errors += 1
            await db.commit()

    summary = {
        "ingested": ingested,
        "skipped": skipped,
        "errors": errors,
        "breakdown": {
            "job_posts": sum(1 for t, _, _ in signals_to_ingest if t == "job"),
            "ask_hn": sum(1 for t, _, _ in signals_to_ingest if t == "ask"),
            "hiring_thread_comments": sum(1 for t, _, _ in signals_to_ingest if t == "hiring_comment"),
            "freelancer_thread_comments": sum(1 for t, _, _ in signals_to_ingest if t == "freelancer_comment"),
        },
    }
    logger.info(f"HN ingest complete: {summary}")
    return summary
