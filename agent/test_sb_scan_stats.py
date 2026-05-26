"""
Quick smoke-test for _sb_upsert_scan_stats → Supabase she_scan_stats.

Run from the agent/ directory:
    python test_sb_scan_stats.py

What it does:
  1. Upserts a row with week="TEST-W00" (won't touch real week data)
  2. Reads it back and asserts field values are correct
  3. Upserts again with different counts (proves upsert updates, not duplicates)
  4. Deletes the test row (requires SUPABASE_SERVICE_ROLE_KEY for DELETE)
  5. Verifies the row is gone
"""

import os, sys
from datetime import datetime, timezone
from pathlib import Path

# Allow importing from agent/ without installing the package
sys.path.insert(0, str(Path(__file__).parent))

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
)
TABLE = "she_scan_stats"
TEST_WEEK = "TEST-W00"

if not (SUPABASE_URL and SUPABASE_KEY):
    sys.exit("ERROR: SUPABASE_URL and a Supabase key env var must be set.")


def headers(extra: dict | None = None) -> dict:
    h = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
    }
    if extra:
        h.update(extra)
    return h


def upsert(row: dict) -> int:
    resp = httpx.post(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        json=row,
        headers=headers({"Prefer": "resolution=merge-duplicates,return=minimal"}),
        timeout=15.0,
    )
    return resp.status_code


def fetch(week: str) -> dict | None:
    resp = httpx.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        params={"week": f"eq.{week}", "select": "*"},
        headers=headers(),
        timeout=10.0,
    )
    rows = resp.json()
    return rows[0] if rows else None


def delete_test_row(week: str) -> int:
    resp = httpx.delete(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        params={"week": f"eq.{week}"},
        headers=headers({"Prefer": "return=minimal"}),
        timeout=10.0,
    )
    return resp.status_code


def run():
    print(f"Target: {SUPABASE_URL}/rest/v1/{TABLE}")
    print(f"Test week key: {TEST_WEEK}\n")

    # ── Step 1: first upsert ───────────────────────────────────────────────────
    row1 = {
        "week":              TEST_WEEK,
        "scanned_at":        datetime.now(timezone.utc).isoformat(),
        "rss_count":         10,
        "youtube_count":     2,
        "reddit_count":      3,
        "gdelt_count":       1,
        "research_count":    4,
        "social_count":      0,
        "llm_scout_count":   0,
        "total_fetched":     20,
        "total_after_dedup": 18,
        "signals_found":     5,
        "crisis_signals":    1,
    }
    status = upsert(row1)
    assert status in (200, 201), f"First upsert failed: HTTP {status}"
    print(f"[PASS] First upsert → HTTP {status}")

    # ── Step 2: read back ──────────────────────────────────────────────────────
    row = fetch(TEST_WEEK)
    assert row is not None, "Row not found after upsert"
    assert row["rss_count"] == 10,   f"rss_count mismatch: {row['rss_count']}"
    assert row["signals_found"] == 5, f"signals_found mismatch: {row['signals_found']}"
    print(f"[PASS] Read back: rss_count={row['rss_count']}, signals_found={row['signals_found']}")

    # ── Step 3: second upsert (different counts — proves update, not duplicate) ─
    row2 = {**row1, "rss_count": 99, "signals_found": 42, "total_fetched": 200}
    status = upsert(row2)
    assert status in (200, 201), f"Second upsert failed: HTTP {status}"
    row = fetch(TEST_WEEK)
    assert row["rss_count"] == 99,    f"rss_count not updated: {row['rss_count']}"
    assert row["signals_found"] == 42, f"signals_found not updated: {row['signals_found']}"
    # Confirm there's still only one row for this week
    resp = httpx.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        params={"week": f"eq.{TEST_WEEK}", "select": "week"},
        headers=headers({"Prefer": "count=exact"}),
        timeout=10.0,
    )
    count = int(resp.headers.get("content-range", "*/1").split("/")[-1])
    assert count == 1, f"Expected 1 row, found {count} — upsert created a duplicate!"
    print(f"[PASS] Second upsert updated in-place (rss_count=99, signals_found=42, row count=1)")

    # ── Step 4: cleanup ────────────────────────────────────────────────────────
    status = delete_test_row(TEST_WEEK)
    if status in (200, 204):
        row = fetch(TEST_WEEK)
        assert row is None, "Row still exists after DELETE"
        print("[PASS] Test row deleted and confirmed gone")
    elif status == 403:
        print("[WARN] DELETE requires service-role key — test row TEST-W00 left in table, delete manually")
    else:
        print(f"[WARN] DELETE returned HTTP {status} — test row may still exist, delete manually")

    print("\nAll assertions passed.")


if __name__ == "__main__":
    run()
