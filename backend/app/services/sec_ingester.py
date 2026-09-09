"""SEC EDGAR Signal Ingester.

Pulls Form D filings from SEC EDGAR — the most reliable leading indicator of
commercial spend. Every US private funding round (seed, Series A/B/C) must be
filed with the SEC within 15 days of the first sale.

A Form D filing means:
  - A company just raised capital
  - They are about to spend it on technology, infrastructure, staff, services
  - This signal arrives BEFORE any press release

API: https://www.sec.gov/cgi-bin/browse-edgar (Atom RSS feed)
     https://efts.sec.gov/LATEST/search-index (full-text search)

No API key required. Rate limit: 10 requests/second per SEC guidelines.
Required: User-Agent header with company name + contact email.
"""
import asyncio
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx

from app.core.database import get_session_factory
from app.services.signal_service import ingest_signal

logger = logging.getLogger(__name__)

SEC_RSS_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
SEC_USER_AGENT = "IntentRadar commercial-intelligence contact@intentradar.ai"

# Form D offering types that indicate real commercial spend incoming
RELEVANT_EXEMPTIONS = {
    "06b",   # Rule 506(b) — most common VC/PE raise
    "06c",   # Rule 506(c) — publicly solicited
    "04",    # Section 4(a)(2) — private placement
    "04a",   # Section 4(a)(6) — crowdfunding
}

# Industry categories to focus on (exclude real estate funds, oil royalties etc.)
FOCUS_INDUSTRIES = {
    "Technology",
    "Software",
    "Health Care",
    "Healthcare",
    "Business Services",
    "Consulting",
    "Financial Services",
    "Manufacturing",
    "Infrastructure",
    "Energy",
    "Communications",
    "Transportation",
    "Education",
}


async def fetch_recent_form_d(
    client: httpx.AsyncClient,
    count: int = 40,
) -> list[dict]:
    """Fetch recent Form D filings from SEC EDGAR RSS feed."""
    params = {
        "action": "getcurrent",
        "type": "D",
        "dateb": "",
        "owner": "include",
        "count": count,
        "search_text": "",
        "output": "atom",
    }
    headers = {"User-Agent": SEC_USER_AGENT}

    try:
        r = await client.get(SEC_RSS_URL, params=params, headers=headers, timeout=15.0)
        r.raise_for_status()

        # Parse Atom feed
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(r.content)
        entries = root.findall("atom:entry", ns)

        filings = []
        for entry in entries:
            title_el = entry.find("atom:title", ns)
            link_el = entry.find("atom:link", ns)
            summary_el = entry.find("atom:summary", ns)
            updated_el = entry.find("atom:updated", ns)
            id_el = entry.find("atom:id", ns)

            title = title_el.text or "" if title_el is not None else ""
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            summary = summary_el.text or "" if summary_el is not None else ""
            updated = updated_el.text or "" if updated_el is not None else ""
            filing_id = id_el.text or "" if id_el is not None else ""

            # Extract company name from title (format: "D - Company Name")
            company_name = title.replace("D - ", "").strip() if title.startswith("D - ") else title

            filings.append({
                "company_name": company_name,
                "filing_url": link,
                "summary": summary,
                "filed_at": updated,
                "filing_id": filing_id,
            })

        return filings

    except Exception as e:
        logger.warning(f"SEC EDGAR RSS fetch failed: {e}")
        return []


async def fetch_filing_detail(
    client: httpx.AsyncClient,
    filing_url: str,
) -> dict:
    """
    Fetch basic detail from a Form D filing index page.
    Returns company info extracted from the filing index HTML.
    """
    if not filing_url:
        return {}
    try:
        headers = {"User-Agent": SEC_USER_AGENT}
        r = await client.get(filing_url, headers=headers, timeout=10.0)
        r.raise_for_status()
        text = r.text

        # Extract offering amount (rough parse from HTML)
        amount = None
        if "Total Offering Amount" in text:
            idx = text.find("Total Offering Amount")
            snippet = text[idx:idx+200]
            import re
            match = re.search(r'\$[\d,]+', snippet)
            if match:
                amount = match.group(0)

        # Extract state
        state = None
        if "State of Incorporation" in text or "Principal State" in text:
            for label in ["Principal State", "State of Incorporation"]:
                idx = text.find(label)
                if idx > 0:
                    snippet = text[idx:idx+100]
                    # State is usually 2 letters after the label
                    import re
                    match = re.search(r'\b([A-Z]{2})\b', snippet[len(label):])
                    if match:
                        state = match.group(1)
                        break

        return {"amount": amount, "state": state}
    except Exception as e:
        logger.debug(f"Failed to fetch filing detail for {filing_url}: {e}")
        return {}


async def ingest_sec_signals(
    count: int = 40,
    dry_run: bool = False,
    organization_id=None,
) -> dict:
    """
    Pull recent Form D filings from SEC EDGAR and ingest as intent signals.

    Each filing = a company that just raised money = imminent commercial spend.

    Args:
        count: Number of recent filings to check
        dry_run: Detect without writing to DB
        organization_id: Org to scope signals to

    Returns:
        Summary dict with counts
    """
    ingested = 0
    skipped = 0
    errors = 0
    signals_to_ingest = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        filings = await fetch_recent_form_d(client, count=count)
        logger.info(f"Fetched {len(filings)} Form D filings from SEC EDGAR")

        for filing in filings:
            company = filing["company_name"]
            if not company or len(company) < 3:
                skipped += 1
                continue

            filing_url = filing["filing_url"]
            filed_at = filing["filed_at"]

            # Build a rich signal description
            title = f"{company} — New Funding Round (SEC Form D Filing)"
            description = (
                f"{company} has filed a Form D with the SEC, indicating a new private "
                f"capital raise. Form D filings are required within 15 days of the first "
                f"sale of securities. This signals imminent commercial spending across "
                f"technology, infrastructure, staffing, and professional services.\n\n"
                f"Filing date: {filed_at[:10] if filed_at else 'Recent'}\n"
                f"Source: SEC EDGAR\n"
                f"Filing URL: {filing_url}"
            )

            payload = {
                "source": "sec_edgar",
                "source_id": f"sec_{filing['filing_id'].replace('/', '_')[-20:]}",
                "country_code": "US",
                "title": title[:500],
                "description": description[:2000],
                "raw_data": {
                    "signal_type": "funding_round",
                    "company_name": company,
                    "source_url": filing_url,
                    "filed_at": filed_at,
                    "filing_id": filing["filing_id"],
                },
            }
            signals_to_ingest.append(("sec_form_d", payload, title))

            # Rate limit: SEC asks for max 10 req/sec
            await asyncio.sleep(0.15)

    # Write to DB
    if dry_run:
        logger.info(f"[DRY RUN] Would ingest {len(signals_to_ingest)} SEC Form D signals:")
        for _, _, label in signals_to_ingest[:5]:
            logger.info(f"  {label[:80]}")
        ingested = len(signals_to_ingest)
    else:
        async with get_session_factory()() as db:
            for stype, payload, label in signals_to_ingest:
                try:
                    await ingest_signal(db, payload, organization_id=organization_id)
                    ingested += 1
                except Exception as e:
                    logger.warning(f"Failed to ingest SEC signal {label[:60]}: {e}")
                    errors += 1
            await db.commit()

    summary = {
        "ingested": ingested,
        "skipped": skipped,
        "errors": errors,
        "breakdown": {
            "form_d_filings": len(signals_to_ingest),
        },
    }
    logger.info(f"SEC EDGAR ingest complete: {summary}")
    return summary
