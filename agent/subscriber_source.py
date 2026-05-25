"""
SHEtoken — Subscriber List Reader
==================================
Reads the she_subscribers table (the newsletter mailing list) so email_sender
can build its recipient list from Supabase instead of env vars.

PRIVATE table: read with the SERVICE ROLE key (no public RLS policy).
Returns [] on any failure so the caller can fall back to env-var lists.
"""

from __future__ import annotations
import os, logging

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
# Service role required — the list is private (no public read policy).
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def get_subscribers() -> list[dict]:
    """Return active subscribers as [{'email':..., 'tier':...}]. [] on failure."""
    if not SUPABASE_URL or not SERVICE_KEY:
        logger.info("subscribers: Supabase service creds not set — falling back to env")
        return []
    try:
        import httpx
        resp = httpx.get(
            f"{SUPABASE_URL}/rest/v1/she_subscribers",
            params={"select": "email,tier", "active": "eq.true"},
            headers={"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"},
            timeout=5.0,
        )
        if resp.status_code != 200:
            logger.warning(f"subscribers: query returned {resp.status_code}")
            return []
        rows = resp.json()
        return [{"email": (r.get("email") or "").strip(),
                 "tier": r.get("tier", "subscriber")}
                for r in rows if r.get("email")]
    except Exception as e:
        logger.warning(f"subscribers: query failed ({e}) — falling back to env")
        return []
