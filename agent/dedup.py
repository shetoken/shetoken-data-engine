"""
SHEtoken Agent — Article URL deduplication store
=================================================
Prevents the same news article from being re-classified in a later run.

Storage strategy
----------------
Primary  → Supabase table ``she_seen_urls``
           Works on Cloud Run where the container filesystem is wiped between runs.
           Requires SUPABASE_URL + SUPABASE_ANON_KEY env vars.

Fallback → Local SQLite at  agent/output/seen_urls.db
           Used automatically when Supabase is unreachable or env vars are absent.
           Good for local development; persists between runs on the same machine.

Supabase table setup (run once in the SQL editor)
--------------------------------------------------
    CREATE TABLE IF NOT EXISTS she_seen_urls (
        url_hash   TEXT PRIMARY KEY,      -- 16-char SHA-256 prefix
        url        TEXT NOT NULL,
        week       TEXT NOT NULL,         -- e.g. "2026-W21"
        seen_at    TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS idx_seen_urls_seen_at
        ON she_seen_urls (seen_at);

    -- Row-level security: anon key can read and insert, not delete
    ALTER TABLE she_seen_urls ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "anon_select" ON she_seen_urls FOR SELECT USING (true);
    CREATE POLICY "anon_insert" ON she_seen_urls FOR INSERT WITH CHECK (true);

    -- Deletion of old rows requires the service-role key (called from a
    -- scheduled DB function or a trusted backend — not the agent itself).
    -- Alternatively call prune_old() with the service-role key in env.

Usage in run_agent.py
---------------------
    from dedup import filter_new, mark_seen, prune_old, stats as dedup_stats

    # After fetching, before classifying:
    articles, n_skipped = filter_new(articles, week)

    # After aggregation (pipeline succeeded):
    mark_seen(articles, week)
    prune_old(days_keep=90)
"""

from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")   # preferred: can also DELETE rows
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
)
SUPABASE_TABLE = "she_seen_urls"

# Local SQLite fallback (only used when Supabase is unreachable/unconfigured)
_AGENT_DIR = Path(__file__).parent
SQLITE_PATH = _AGENT_DIR / "output" / "seen_urls.db"

# How many URL hashes to send per Supabase IN-query
# (keep below ~200 to stay well inside HTTP query-string limits)
_CHUNK_SIZE = 100


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(url: str) -> str:
    """16-char hex prefix of SHA-256 — collision-resistant at our scale."""
    return hashlib.sha256(url.strip().encode()).hexdigest()[:16]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cutoff_iso(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


# ── Supabase backend ──────────────────────────────────────────────────────────

def _sb_headers() -> dict:
    return {
        "apikey":          SUPABASE_KEY,
        "Authorization":   f"Bearer {SUPABASE_KEY}",
        "Content-Type":    "application/json",
        "Prefer":          "resolution=ignore-duplicates",   # INSERT OR IGNORE
    }


def _sb_filter_new(articles: list, week: str) -> tuple[list, int]:
    """
    Check which article URLs are already in Supabase.
    Returns (new_articles, skipped_count).
    Sends hashes in batches of _CHUNK_SIZE to stay within query-string limits.
    """
    import httpx

    url_map: dict[str, dict] = {}   # hash → article
    for art in articles:
        raw_url = (art.get("url") or "").strip()
        if raw_url:
            url_map[_hash(raw_url)] = art
        # Articles with no URL are always passed through
    no_url_arts = [a for a in articles if not (a.get("url") or "").strip()]

    # Batch-fetch seen hashes
    all_hashes  = list(url_map.keys())
    seen_hashes: set[str] = set()
    endpoint = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"

    for i in range(0, len(all_hashes), _CHUNK_SIZE):
        chunk = all_hashes[i : i + _CHUNK_SIZE]
        in_clause = f"({','.join(chunk)})"
        resp = httpx.get(
            endpoint,
            params={"url_hash": f"in.{in_clause}", "select": "url_hash"},
            headers=_sb_headers(),
            timeout=8.0,
        )
        if resp.status_code == 200:
            seen_hashes.update(r["url_hash"] for r in resp.json())
        else:
            logger.warning(f"Supabase dedup check returned {resp.status_code}: {resp.text[:200]}")

    new_arts = [art for h, art in url_map.items() if h not in seen_hashes]
    new_arts += no_url_arts
    skipped  = len(articles) - len(new_arts)
    return new_arts, skipped


def _sb_mark_seen(articles: list, week: str) -> int:
    """Insert processed URLs into Supabase. Returns number of rows inserted."""
    import httpx

    now = _now_iso()
    rows = [
        {
            "url_hash": _hash(art["url"].strip()),
            "url":      art["url"].strip(),
            "week":     week,
            "seen_at":  now,
        }
        for art in articles
        if (art.get("url") or "").strip()
    ]
    if not rows:
        return 0

    # Batch insert (Supabase REST supports array body)
    endpoint = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    resp = httpx.post(endpoint, json=rows, headers=_sb_headers(), timeout=15.0)
    if resp.status_code in (200, 201):
        return len(rows)
    logger.warning(f"Supabase mark_seen returned {resp.status_code}: {resp.text[:200]}")
    return 0


def _sb_prune_old(days_keep: int) -> int:
    """
    Delete rows older than days_keep days.
    Requires service-role key (anon key cannot DELETE).
    Returns number deleted, or 0 if permission denied.
    """
    import httpx

    cutoff  = _cutoff_iso(days_keep)
    endpoint = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {**_sb_headers(), "Prefer": "return=minimal"}
    resp = httpx.delete(
        endpoint,
        params={"seen_at": f"lt.{cutoff}"},
        headers=headers,
        timeout=15.0,
    )
    if resp.status_code in (200, 204):
        # Supabase doesn't always return a count — log what we know
        return 1   # pruning occurred
    if resp.status_code == 403:
        logger.debug("Supabase prune skipped (anon key — service-role required for DELETE)")
        return 0
    logger.warning(f"Supabase prune returned {resp.status_code}: {resp.text[:200]}")
    return 0


def _sb_stats() -> dict:
    """Fetch summary stats from Supabase for logging."""
    import httpx

    endpoint = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    try:
        # total count
        r1 = httpx.get(
            endpoint,
            params={"select": "url_hash", "limit": "1"},
            headers={**_sb_headers(), "Prefer": "count=exact"},
            timeout=5.0,
        )
        total = int(r1.headers.get("content-range", "*/0").split("/")[-1])

        # distinct weeks
        r2 = httpx.get(
            endpoint,
            params={"select": "week", "limit": "1000"},
            headers=_sb_headers(),
            timeout=5.0,
        )
        weeks = len({r["week"] for r in r2.json()}) if r2.status_code == 200 else "?"

        return {"total_urls": total, "weeks_covered": weeks, "backend": "supabase"}
    except Exception:
        return {"total_urls": "?", "weeks_covered": "?", "backend": "supabase"}


# ── SQLite fallback backend ───────────────────────────────────────────────────

def _sqlite_connect() -> sqlite3.Connection:
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_urls (
            url_hash  TEXT PRIMARY KEY,
            url       TEXT NOT NULL,
            week      TEXT NOT NULL,
            seen_at   TEXT NOT NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_seen_at ON seen_urls (seen_at)"
    )
    conn.commit()
    return conn


def _sqlite_filter_new(articles: list, week: str) -> tuple[list, int]:
    conn = _sqlite_connect()
    try:
        new, skipped = [], 0
        for art in articles:
            raw_url = (art.get("url") or "").strip()
            if not raw_url:
                new.append(art)
                continue
            h = _hash(raw_url)
            row = conn.execute(
                "SELECT week FROM seen_urls WHERE url_hash = ?", (h,)
            ).fetchone()
            if row is None:
                new.append(art)
            else:
                skipped += 1
                logger.debug(
                    f"  Dedup skip (seen {row[0]}): {art.get('title','')[:60]}"
                )
        return new, skipped
    finally:
        conn.close()


def _sqlite_mark_seen(articles: list, week: str) -> int:
    now = _now_iso()
    conn = _sqlite_connect()
    try:
        rows = [
            (_hash(art["url"].strip()), art["url"].strip(), week, now)
            for art in articles
            if (art.get("url") or "").strip()
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO seen_urls (url_hash, url, week, seen_at) "
            "VALUES (?,?,?,?)",
            rows,
        )
        inserted = conn.total_changes
        conn.commit()
        return inserted
    finally:
        conn.close()


def _sqlite_prune_old(days_keep: int) -> int:
    cutoff = _cutoff_iso(days_keep)
    conn = _sqlite_connect()
    try:
        deleted = conn.execute(
            "DELETE FROM seen_urls WHERE seen_at < ?", (cutoff,)
        ).rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()


def _sqlite_stats() -> dict:
    conn = _sqlite_connect()
    try:
        total  = conn.execute("SELECT COUNT(*) FROM seen_urls").fetchone()[0]
        oldest = conn.execute("SELECT MIN(seen_at) FROM seen_urls").fetchone()[0]
        weeks  = conn.execute(
            "SELECT COUNT(DISTINCT week) FROM seen_urls"
        ).fetchone()[0]
        return {"total_urls": total, "weeks_covered": weeks,
                "oldest_entry": oldest, "backend": "sqlite"}
    finally:
        conn.close()


# ── Public API ────────────────────────────────────────────────────────────────

def _use_supabase() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def filter_new(articles: list, week: str) -> tuple[list, int]:
    """
    Remove articles whose URL was already processed in a previous run.

    Returns (new_articles, skipped_count).
    Articles without a URL are always kept (can't deduplicate them).

    Tries Supabase first; falls back to SQLite on any failure.
    """
    if not articles:
        return articles, 0

    if _use_supabase():
        try:
            return _sb_filter_new(articles, week)
        except Exception as exc:
            logger.warning(f"Supabase dedup unavailable ({exc}), falling back to SQLite")

    return _sqlite_filter_new(articles, week)


def mark_seen(articles: list, week: str) -> int:
    """
    Record article URLs as processed.  Call AFTER a successful pipeline run
    so that a mid-run crash doesn't permanently suppress articles.

    Returns number of new rows written.
    """
    if not articles:
        return 0

    if _use_supabase():
        try:
            return _sb_mark_seen(articles, week)
        except Exception as exc:
            logger.warning(f"Supabase mark_seen failed ({exc}), falling back to SQLite")

    return _sqlite_mark_seen(articles, week)


def prune_old(days_keep: int = 90) -> int:
    """
    Delete seen-URL entries older than days_keep days.
    Keeps the store from growing unboundedly while retaining enough history
    to catch slow-publishing sources (academic journals, quarterly NGO reports).

    Returns number of rows deleted (0 if using Supabase anon key without DELETE).
    """
    if _use_supabase():
        try:
            deleted = _sb_prune_old(days_keep)
            if deleted:
                logger.info(f"  Dedup: pruned entries older than {days_keep} days (Supabase)")
            return deleted
        except Exception as exc:
            logger.warning(f"Supabase prune failed ({exc}), trying SQLite")

    deleted = _sqlite_prune_old(days_keep)
    if deleted:
        logger.info(f"  Dedup: pruned {deleted} old entries from SQLite")
    return deleted


def stats() -> dict:
    """Return store stats dict for logging."""
    if _use_supabase():
        try:
            return _sb_stats()
        except Exception:
            pass
    return _sqlite_stats()
