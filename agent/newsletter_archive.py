"""
SHEtoken — Newsletter Archive
==============================
Saves every sent newsletter edition to Supabase (she_newsletters) so the full
history is permanently stored, queryable, and available to show on the website
as a public archive. Best-effort: never blocks or breaks the send.
"""

from __future__ import annotations
import os, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
# Anon key is fine — she_newsletters allows public read; writes use whichever key
# is set (service role preferred so writes always succeed regardless of RLS).
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")


def archive_newsletter(week: str, tier: str, subject: str, html: str, text: str) -> bool:
    """Save one edition. Returns True on success, False on any failure (non-fatal)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("archive: Supabase not configured — newsletter not archived")
        return False
    try:
        import httpx
        now = datetime.now(timezone.utc)
        httpx.post(
            f"{SUPABASE_URL}/rest/v1/she_newsletters",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates",   # upsert on (week,tier)
            },
            json={
                "week": week,
                "tier": tier,
                "subject": subject,
                "html": html,
                "text": text,
                "sent_at": now.isoformat(),
            },
            timeout=5.0,
        )
        logger.info(f"archive: saved {tier} edition for {week}")
        return True
    except Exception as e:
        logger.warning(f"archive: failed for {tier}/{week} ({e}) — non-fatal")
        return False
