"""
SHEtoken API — Newsletter Archive Reader
=========================================
Reads the she_newsletters table so the website can show a public newsletter
archive. Supabase-only (no CSV — the agent writes these rows).

SAFETY: the 'founder' edition contains internal data (raw stats, admin links),
so the public endpoints serve ONLY the 'public' tier by default. 'founder' is
never exposed through these routes.
"""

from __future__ import annotations
import os, logging

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

PUBLIC_TIERS = ("public", "ngo")   # never expose 'founder'


def _query(select: str, filters: dict | None = None, order: str | None = None,
           limit: int | None = None) -> list[dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        import httpx
        params = {"select": select}
        if order:
            params["order"] = order
        if limit:
            params["limit"] = str(limit)
        if filters:
            params.update(filters)
        resp = httpx.get(
            f"{SUPABASE_URL}/rest/v1/she_newsletters",
            params=params,
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=4.0,
        )
        return resp.json() if resp.status_code == 200 else []
    except Exception as e:
        logger.warning(f"newsletter_source: query failed ({e})")
        return []


def list_newsletters(limit: int = 50) -> list[dict]:
    """Metadata only (no HTML) for the archive list — public/ngo tiers only."""
    rows = _query(
        select="week,tier,subject,sent_at",
        filters={"tier": "in.(public,ngo)"},
        order="sent_at.desc",
        limit=limit,
    )
    return rows


def get_newsletter(week: str, tier: str = "public") -> dict | None:
    """Full edition (incl. HTML) for one week — public/ngo only."""
    if tier not in PUBLIC_TIERS:
        tier = "public"
    rows = _query(
        select="week,tier,subject,html,text,sent_at",
        filters={"week": f"eq.{week}", "tier": f"eq.{tier}"},
        limit=1,
    )
    return rows[0] if rows else None


def get_latest_newsletter(tier: str = "public") -> dict | None:
    """Most recent edition for a tier (public/ngo only)."""
    if tier not in PUBLIC_TIERS:
        tier = "public"
    rows = _query(
        select="week,tier,subject,html,text,sent_at",
        filters={"tier": f"eq.{tier}"},
        order="sent_at.desc",
        limit=1,
    )
    return rows[0] if rows else None
