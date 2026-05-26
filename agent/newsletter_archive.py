"""
SHEtoken — Newsletter Archive
==============================
Saves every sent newsletter edition to Supabase (she_newsletters) so the full
history is permanently stored, queryable, and available to show on the website
as a public archive. Best-effort: never blocks or breaks the send.

Also generates a PDF version and uploads it to Supabase Storage bucket
'newsletters' so logged-in users can download past editions.

Supabase setup (run once):
    ALTER TABLE she_newsletters ADD COLUMN IF NOT EXISTS pdf_url TEXT;

    -- Storage: create a public bucket named 'newsletters' in Supabase dashboard
    -- Dashboard → Storage → New bucket → name: newsletters → Public: on
"""

from __future__ import annotations
import os, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")


def _generate_pdf(html: str) -> bytes | None:
    """Convert HTML → PDF bytes using weasyprint. Returns None on failure."""
    try:
        from weasyprint import HTML
        return HTML(string=html, base_url=None).write_pdf()
    except Exception as e:
        logger.warning(f"PDF generation failed ({e}) — skipping PDF upload")
        return None


def _upload_pdf(pdf_bytes: bytes, week: str, tier: str) -> str | None:
    """
    Upload PDF to Supabase Storage bucket 'newsletters'.
    Returns public URL or None on failure.
    Path: newsletters/{week}/{tier}.pdf  e.g. newsletters/2026-W21/subscriber.pdf
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        import httpx
        path     = f"{week}/{tier}.pdf"
        endpoint = f"{SUPABASE_URL}/storage/v1/object/newsletters/{path}"
        resp = httpx.post(
            endpoint,
            content=pdf_bytes,
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type":  "application/pdf",
                # Overwrite on re-runs for the same week
                "x-upsert":      "true",
            },
            timeout=30.0,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/newsletters/{path}"
            logger.info(f"archive: PDF uploaded → {public_url}")
            return public_url
        logger.warning(f"archive: PDF upload returned {resp.status_code}: {resp.text[:200]}")
        return None
    except Exception as e:
        logger.warning(f"archive: PDF upload failed ({e})")
        return None


def archive_newsletter(week: str, tier: str, subject: str, html: str, text: str) -> bool:
    """
    Save one edition to she_newsletters and upload a PDF to Supabase Storage.
    Returns True on success, False on any failure (non-fatal).
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("archive: Supabase not configured — newsletter not archived")
        return False

    # Generate and upload PDF (best-effort — doesn't block archiving)
    pdf_url = None
    pdf_bytes = _generate_pdf(html)
    if pdf_bytes:
        pdf_url = _upload_pdf(pdf_bytes, week, tier)

    try:
        import httpx
        now = datetime.now(timezone.utc)
        row = {
            "week":     week,
            "tier":     tier,
            "subject":  subject,
            "html":     html,
            "text":     text,
            "sent_at":  now.isoformat(),
        }
        if pdf_url:
            row["pdf_url"] = pdf_url

        httpx.post(
            f"{SUPABASE_URL}/rest/v1/she_newsletters",
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type":  "application/json",
                "Prefer":        "resolution=merge-duplicates",
            },
            json=row,
            timeout=5.0,
        )
        logger.info(f"archive: saved {tier} edition for {week}"
                    + (" (with PDF)" if pdf_url else ""))
        return True
    except Exception as e:
        logger.warning(f"archive: failed for {tier}/{week} ({e}) — non-fatal")
        return False
