"""
SHEtoken Agent — RSS Fetcher
Scrapes all news sources, returns WEI-relevant articles.
"""
import feedparser, requests, time, logging, re, sys
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (NEWS_SOURCES, WEI_KEYWORDS, MAX_ARTICLES_PER_SOURCE,
                    MAX_ARTICLE_LENGTH, REQUEST_TIMEOUT, REQUEST_DELAY, MAX_WORKERS)

logger = logging.getLogger(__name__)


def is_relevant(text):
    """Pre-filter: check if article contains any WEI keyword."""
    t = text.lower()
    return any(kw.lower() in t for kws in WEI_KEYWORDS.values() for kw in kws)


def to_aware_utc(dt):
    """
    Ensure a datetime is timezone-aware (UTC).
    Handles naive, aware, and None inputs safely.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume naive datetimes from RSS are UTC
        return dt.replace(tzinfo=timezone.utc)
    # Already aware — convert to UTC
    return dt.astimezone(timezone.utc)


def parse_entry_date(entry):
    """
    Parse publication date from a feedparser entry.
    Returns timezone-aware UTC datetime or None.
    """
    # Try published_parsed (most common)
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return to_aware_utc(datetime(*entry.published_parsed[:6]))
        except Exception:
            pass

    # Try updated_parsed (fallback)
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return to_aware_utc(datetime(*entry.updated_parsed[:6]))
        except Exception:
            pass

    # No parseable date — return None (article will be included)
    return None


def fetch_source(name, url, language, region, tier, days_back=7):
    """
    Fetch articles from a single RSS source.
    Returns list of relevant article dicts.
    """
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; SHEtoken-WEI-Agent/1.0; "
                "+https://shetoken.org)"
            )
        }
        resp = requests.get(url, headers=headers,
                            timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        if not feed.entries:
            logger.info(f"  {name}: 0 articles (empty feed)")
            return []

        count = 0
        for entry in feed.entries:
            if count >= MAX_ARTICLES_PER_SOURCE:
                break

            # Parse and compare dates safely
            pub = parse_entry_date(entry)
            if pub is not None and pub < cutoff:
                continue  # Article too old

            # Build text for keyword matching
            title   = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or ""
            summary = re.sub(r"<[^>]+>", " ", summary)
            summary = re.sub(r"\s+", " ", summary).strip()
            text    = f"{title}. {summary}"[:MAX_ARTICLE_LENGTH]

            if not is_relevant(text):
                continue

            articles.append({
                "source":     name,
                "language":   language,
                "region":     region,
                "tier":       tier,
                "title":      title,
                "summary":    summary[:400],
                "text":       text,
                "url":        getattr(entry, "link", ""),
                "published":  pub.isoformat() if pub else "",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
            count += 1

        if count > 0:
            logger.info(f"  {name}: {count} articles")
        else:
            logger.info(f"  {name}: 0 relevant articles")

        time.sleep(REQUEST_DELAY)

    except requests.exceptions.ConnectionError as e:
        if "getaddrinfo failed" in str(e) or "NameResolutionError" in str(e):
            logger.debug(f"  {name}: DNS/network unreachable (skipped)")
        else:
            logger.warning(f"  {name}: connection error — {e}")
    except requests.exceptions.HTTPError as e:
        logger.debug(f"  {name}: HTTP {e.response.status_code} (skipped)")
    except Exception as e:
        logger.warning(f"  {name}: {e}")

    return articles


def fetch_all_sources(days_back=7):
    """
    Fetch all news sources in parallel.
    Returns flat list of all relevant articles.
    """
    logger.info(f"Fetching {len(NEWS_SOURCES)} sources "
                f"({days_back} days back)...")
    all_articles = []
    ok_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {
            ex.submit(fetch_source, *src, days_back): src[0]
            for src in NEWS_SOURCES
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                arts = future.result()
                all_articles.extend(arts)
                if arts:
                    ok_count += 1
            except Exception as e:
                logger.warning(f"  {name}: unexpected error — {e}")
                fail_count += 1

    logger.info(f"Fetch complete: {len(all_articles)} relevant articles "
                f"from {ok_count} sources ({fail_count} unreachable)")
    return all_articles
