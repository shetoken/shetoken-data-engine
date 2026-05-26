"""
SHEtoken Agent — Social & Blog Scanner
========================================
Covers three platforms:

  • Substack — curated list of gender/women-rights newsletters (RSS-based)
  • Medium   — tag-based RSS feeds for gender/reproductive rights topics
  • LinkedIn — not directly scrapable (see notes below)

Substack
--------
Every Substack publication has a public RSS feed at:
    https://{slug}.substack.com/feed
These return standard RSS 2.0 XML — feedparser handles them identically to
any other news source. The curated list in config.py (SUBSTACK_SOURCES) can
be extended by the team at any time.

Medium
------
Medium exposes tag-based RSS feeds:
    https://medium.com/feed/tag/{tag-slug}
These return the 10 most recent posts for that tag. We query ~10 tags
relevant to WEI pillars. Medium occasionally returns 200 with an HTML
paywall for logged-in-only stories — feedparser handles this gracefully by
returning empty entries.

LinkedIn
--------
LinkedIn has no public RSS or scraping-friendly API:
  • All endpoints require OAuth2 login
  • The main feed is fully Cloudflare-protected
  • The "official" API (via Partner Program) requires an approved app
  • Scraping violates LinkedIn ToS and triggers immediate IP blocks

Workaround: GDELT indexes articles that get SYNDICATED from LinkedIn posts
to external blogs/news sites. For example, if a LinkedIn article by an HR
professional on the gender pay gap gets picked up by a news site, GDELT
sees it. That coverage is already handled by fetch_gdelt.py.

If you obtain LinkedIn API Partner access in the future, wire it in here.
Until then this file provides a clear placeholder and the rationale.

Output schema
-------------
Same as all other scanners:
  source, language, region, tier, title, summary, text, url,
  published, fetched_at  +  platform ("substack" | "medium")
"""

from __future__ import annotations

import logging
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    MAX_ARTICLES_PER_SOURCE,
    MAX_ARTICLE_LENGTH,
    REQUEST_TIMEOUT,
    REQUEST_DELAY,
    WEI_KEYWORDS,
    SUBSTACK_SOURCES,
    MEDIUM_TAG_SOURCES,
)

logger = logging.getLogger(__name__)

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


# ── Relevance filter (reuse WEI keywords) ─────────────────────────────────────

def _is_relevant(text: str) -> bool:
    t = text.lower()
    return any(kw.lower() in t for kws in WEI_KEYWORDS.values() for kw in kws)


# ── Date parser ────────────────────────────────────────────────────────────────

def _parse_entry_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return datetime(*raw[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


# ── Generic RSS fetcher (shared by Substack + Medium) ─────────────────────────

def _fetch_rss(
    name: str,
    url: str,
    platform: str,
    language: str,
    region: str,
    tier: str,
    days_back: int = 7,
) -> list[dict]:
    """
    Fetch an RSS/Atom feed and return WEI-relevant article dicts.
    Shared by Substack and Medium tag feeds.
    """
    cutoff   = datetime.now(timezone.utc) - timedelta(days=days_back)
    articles = []

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": _UA},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        if not feed.entries:
            logger.debug(f"  {name} ({platform}): empty feed")
            return []

        count = 0
        for entry in feed.entries:
            if count >= MAX_ARTICLES_PER_SOURCE:
                break

            pub = _parse_entry_date(entry)
            if pub is not None and pub < cutoff:
                continue

            title   = (getattr(entry, "title",   "") or "").strip()
            summary = (getattr(entry, "summary", "") or "").strip()
            summary = re.sub(r"<[^>]+>", " ", summary)
            summary = re.sub(r"\s+",     " ", summary).strip()

            text = f"{title}. {summary}"[:MAX_ARTICLE_LENGTH]
            if not _is_relevant(text):
                continue

            link = getattr(entry, "link", "") or ""
            articles.append({
                "source":     f"{platform}/{name}",
                "language":   language,
                "region":     region,
                "tier":       tier,
                "title":      title,
                "summary":    summary[:400],
                "text":       text,
                "url":        link,
                "published":  pub.isoformat() if pub else "",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "platform":   platform,
            })
            count += 1

        if count:
            logger.info(f"  {name} ({platform}): {count} articles")
        else:
            logger.debug(f"  {name} ({platform}): 0 relevant articles")

        time.sleep(REQUEST_DELAY)

    except requests.exceptions.ConnectionError as exc:
        if "getaddrinfo" in str(exc) or "NameResolution" in str(exc):
            logger.debug(f"  {name} ({platform}): DNS unreachable (skipped)")
        else:
            logger.warning(f"  {name} ({platform}): connection error — {exc}")
    except requests.exceptions.HTTPError as exc:
        logger.debug(f"  {name} ({platform}): HTTP {exc.response.status_code} (skipped)")
    except Exception as exc:
        logger.warning(f"  {name} ({platform}): {exc}")

    return articles


# ── Substack ───────────────────────────────────────────────────────────────────

def fetch_all_substack(days_back: int = 7) -> list[dict]:
    """
    Fetch all Substack newsletters defined in config.SUBSTACK_SOURCES.

    SUBSTACK_SOURCES format (same as NEWS_SOURCES):
        (name, rss_url, language, region, tier)

    Returns flat list of WEI-relevant article dicts.
    """
    if not SUBSTACK_SOURCES:
        logger.debug("  Substack: no sources configured (SUBSTACK_SOURCES is empty)")
        return []

    logger.info(f"  Substack: fetching {len(SUBSTACK_SOURCES)} newsletters...")
    all_articles: list[dict] = []

    for name, url, language, region, tier in SUBSTACK_SOURCES:
        articles = _fetch_rss(name, url, "substack", language, region, tier, days_back)
        all_articles.extend(articles)

    logger.info(f"  Substack total: {len(all_articles)} relevant articles")
    return all_articles


# ── Medium ─────────────────────────────────────────────────────────────────────

def fetch_all_medium(days_back: int = 7) -> list[dict]:
    """
    Fetch Medium tag RSS feeds defined in config.MEDIUM_TAG_SOURCES.

    MEDIUM_TAG_SOURCES format:
        (tag_label, rss_url)   e.g. ("gender-equality", "https://medium.com/feed/tag/gender-equality")

    Returns flat list of WEI-relevant article dicts.
    """
    if not MEDIUM_TAG_SOURCES:
        logger.debug("  Medium: no tag sources configured (MEDIUM_TAG_SOURCES is empty)")
        return []

    logger.info(f"  Medium: fetching {len(MEDIUM_TAG_SOURCES)} tag feeds...")
    all_articles: list[dict] = []
    seen_urls: set[str]      = set()

    for tag_label, url in MEDIUM_TAG_SOURCES:
        articles = _fetch_rss(
            name=tag_label,
            url=url,
            platform="medium",
            language="en",
            region="global",
            tier="blog",
            days_back=days_back,
        )
        for art in articles:
            link = art.get("url", "")
            if link and link not in seen_urls:
                seen_urls.add(link)
                all_articles.append(art)

    logger.info(f"  Medium total: {len(all_articles)} unique relevant articles")
    return all_articles


# ── LinkedIn placeholder ───────────────────────────────────────────────────────

def fetch_linkedin_note() -> None:
    """
    LinkedIn is NOT scrapable without an approved Partner API access.

    Coverage strategy:
    1. GDELT already indexes articles syndicated from LinkedIn to news sites
       (handled in fetch_gdelt.py — no action needed here)
    2. If SHEtoken obtains LinkedIn Partner API access:
       - Use the /v2/ugcPosts endpoint with OAuth2 Bearer token
       - Filter by #WomensRights #GenderEquality #GBV hashtags
       - Wire results through this function in the same dict format

    Until then, this function intentionally does nothing.
    """
    logger.debug("  LinkedIn: no API access configured — GDELT provides indirect coverage")


# ── Combined entry point ───────────────────────────────────────────────────────

def fetch_all_social(days_back: int = 7) -> list[dict]:
    """
    Run Substack + Medium scanners.
    LinkedIn is noted but not scraped (see fetch_linkedin_note docstring).

    Returns combined list of WEI-relevant article dicts.
    """
    substack_arts = fetch_all_substack(days_back=days_back)
    medium_arts   = fetch_all_medium(days_back=days_back)

    total = substack_arts + medium_arts
    logger.info(
        f"  Social total: {len(total)} articles "
        f"(Substack: {len(substack_arts)}, Medium: {len(medium_arts)})"
    )
    return total
