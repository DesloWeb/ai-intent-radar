"""Google News RSS Signal Ingester.

Uses Google News' free, no-auth RSS feeds to pull real commercial intent signals.
Queries are tuned to catch buying signals: service requests, expansion announcements,
hiring surges, funding news, and procurement activity.

No API key required. Rate limit: ~100 requests/minute (reasonable use).
"""
import asyncio
import hashlib
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional
import re

import httpx

from app.core.database import get_session_factory
from app.services.signal_service import ingest_signal

logger = logging.getLogger(__name__)

GNEWS_BASE = "https://news.google.com/rss/search"

# Search queries targeting commercial intent signals
# Each tuple: (query, signal_type, weight)
INTENT_QUERIES = [
    # Direct service/vendor requests
    ("\"looking for\" contractor OR vendor OR supplier OR consultant US",    "service_request",   1.0),
    ("\"seeking proposals\" OR \"request for proposal\" OR RFP OR RFQ US",  "procurement",       1.0),
    ("\"accepting applications\" OR \"taking bids\" US business",            "procurement",       0.9),

    # Business expansion signals
    ("\"new facility\" OR \"new office\" OR \"expanding to\" US 2026",       "expansion",         0.9),
    ("\"opening new\" location OR branch OR office US",                      "expansion",         0.8),
    ("\"new headquarters\" OR \"relocating\" US company",                    "expansion",         0.7),

    # Hiring as buying intent
    ("company hiring engineers OR developers OR consultants US 2026",        "hiring",            0.8),
    ("\"rapidly hiring\" OR \"scaling team\" OR \"growing team\" US",        "hiring",            0.8),

    # Funding = imminent spend
    ("startup \"raises\" OR \"raised\" \"million\" US 2026",                 "funding",           0.9),
    ("\"series A\" OR \"series B\" OR \"seed round\" US funding 2026",       "funding",           1.0),
    ("\"secured funding\" OR \"new investment\" US company 2026",            "funding",           0.9),

    # Infrastructure / construction
    ("\"construction contract\" OR \"infrastructure project\" US awarded",   "infrastructure",    0.9),
    ("\"breaking ground\" OR \"new development\" US commercial 2026",        "infrastructure",    0.8),
]

# Intent keywords for scoring (same approach as HN ingester)
HIGH_INTENT_PHRASES = [
    "looking for", "seeking", "request for proposal", "rfp", "rfq",
    "accepting bids", "contract awarded", "new facility", "expansion",
    "series a", "series b", "seed round", "raises million", "funded",
    "hiring", "scaling", "breaking ground", "procurement",
]

MEDIUM_INTENT_PHRASES = [
    "partnership", "new office", "growth", "investment", "launch",
    "opening", "new location", "acquisition", "merger",
]


def _has_intent(text: str) -> tuple[bool, str]:
    lowered = text.lower()
    for phrase in HIGH_INTENT_PHRASES:
        if phrase in lowered:
            return True, phrase
    for phrase in MEDIUM_INTENT_PHRASES:
        if phrase in lowered:
            return True, phrase
    return False, ""


def _clean_title(title: str) -> str:
    """Remove source name from Google News titles (e.g. 'Company raises $5M - TechCrunch')."""
    if title and " - " in title:
        title = title.rsplit(" - ", 1)[0]
    return title.strip()


async def fetch_gnews(
    client: httpx.AsyncClient,
    query: str,
    max_results: int = 10,
) -> list[dict]:
    """Fetch articles from Google News RSS for a given query."""
    params = {
        "q": query,
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en",
    }
    headers = {"User-Agent": "Mozilla/5.0 IntentRadar/1.0 (commercial-intelligence)"}
    try:
        r = await client.get(GNEWS_BASE, params=params, headers=headers, timeout=15.0)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        items = root.findall(".//item")[:max_results]
        results = []
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")
            source_el = item.find("source")

            title = _clean_title(title_el.text or "") if title_el is not None else ""
            link = link_el.text or "" if link_el is not None else ""
            desc = re.sub(r"<[^>]+>", " ", desc_el.text or "") if desc_el is not None else ""
            pub_date = pub_el.text or "" if pub_el is not None else ""
            source_name = source_el.text or "" if source_el is not None else ""

            if title:
                results.append({
                    "title": title,
                    "link": link,
                    "description": desc.strip(),
                    "pub_date": pub_date,
                    "source_name": source_name,
                })
        return results
    except Exception as e:
        logger.warning(f"Google News fetch failed for query '{query[:40]}': {e}")
        return []


async def ingest_google_news_signals(
    max_per_query: int = 10,
    dry_run: bool = False,
    organization_id=None,
) -> dict:
    """
    Pull commercial intent signals from Google News RSS feeds.

    Args:
        max_per_query: Max articles to check per search query
        dry_run: Detect without writing to DB
        organization_id: Org to scope signals to

    Returns:
        Summary dict with counts
    """
    ingested = 0
    skipped = 0
    errors = 0
    seen_titles: set[str] = set()  # dedup within this run

    signals_to_ingest = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for query, signal_type, weight in INTENT_QUERIES:
            try:
                articles = await fetch_gnews(client, query, max_results=max_per_query)

                for article in articles:
                    title = article["title"]
                    desc = article["description"]
                    link = article["link"]

                    # Skip if already seen in this run
                    title_key = title.lower().strip()
                    if title_key in seen_titles:
                        skipped += 1
                        continue
                    seen_titles.add(title_key)

                    # Check intent
                    combined = f"{title} {desc}"
                    has_intent, matched = _has_intent(combined)
                    if not has_intent and signal_type not in ("procurement", "funding"):
                        skipped += 1
                        continue

                    payload = {
                        "source": "google_news",
                        "source_id": f"gnews_{hashlib.md5(link.encode()).hexdigest()[:12]}",
                        "country_code": "US",
                        "title": title[:500],
                        "description": f"{title}\n\n{desc}"[:2000],
                        "raw_data": {
                            "signal_type": signal_type,
                            "query": query,
                            "source_url": link,
                            "source_name": article["source_name"],
                            "pub_date": article["pub_date"],
                            "intent_match": matched,
                            "weight": weight,
                        },
                    }
                    signals_to_ingest.append((signal_type, payload, title))

                # Polite delay between queries
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error processing Google News query '{query[:40]}': {e}")
                errors += 1

    # Write to DB
    if dry_run:
        logger.info(f"[DRY RUN] Would ingest {len(signals_to_ingest)} Google News signals:")
        for stype, payload, label in signals_to_ingest[:5]:
            logger.info(f"  [{stype}] {label[:80]}")
        ingested = len(signals_to_ingest)
    else:
        async with get_session_factory()() as db:
            for stype, payload, label in signals_to_ingest:
                try:
                    await ingest_signal(db, payload, organization_id=organization_id)
                    ingested += 1
                    logger.debug(f"Ingested Google News [{stype}]: {label[:60]}")
                except Exception as e:
                    logger.warning(f"Failed to ingest [{stype}] {label[:60]}: {e}")
                    errors += 1
            await db.commit()

    summary = {
        "ingested": ingested,
        "skipped": skipped,
        "errors": errors,
        "breakdown": {
            "service_requests": sum(1 for t, _, _ in signals_to_ingest if t == "service_request"),
            "procurement": sum(1 for t, _, _ in signals_to_ingest if t == "procurement"),
            "expansion": sum(1 for t, _, _ in signals_to_ingest if t == "expansion"),
            "hiring": sum(1 for t, _, _ in signals_to_ingest if t == "hiring"),
            "funding": sum(1 for t, _, _ in signals_to_ingest if t == "funding"),
            "infrastructure": sum(1 for t, _, _ in signals_to_ingest if t == "infrastructure"),
        },
    }
    logger.info(f"Google News ingest complete: {summary}")
    return summary
