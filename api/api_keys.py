"""
SHEtoken API — API Key & Tier Management
=========================================
Validates developer bearer tokens against the she_api_keys Supabase table
and enforces per-token daily quotas.

DESIGN (keeps Supabase load near zero):
  • The key table is fetched from Supabase at most once every KEY_CACHE_TTL
    seconds (default 5 min) — NOT on every request. One small query per refresh.
  • Per-token usage is counted IN MEMORY and reset daily. This is best-effort:
    counts reset if the Railway service restarts. For a launch-stage public API
    that's an acceptable trade; upgrade to persistent counting (Redis / Supabase
    increments) later if paid usage demands exact enforcement.

TIERS (daily request limits):
  public  — no token, IP-limited per minute (handled in rate_limiter)
  free    — 5,000 / day
  paid    — 100,000 / day
  admin   — unlimited

The API reads she_api_keys with the SERVICE ROLE key (the table is RLS-locked
with no public policy). Set SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY on Railway.
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
# Prefer service role (can read the locked table); fall back to anon if that's
# all that's set (works only if you add a read policy — not recommended).
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

KEY_CACHE_TTL = 300  # seconds — how often to refresh the key table from Supabase

# Tier daily limits (-1 = unlimited)
TIER_DAILY_LIMITS = {
    "free":  5_000,
    "paid":  100_000,
    "admin": -1,
}

# ── in-memory caches ──────────────────────────────────────────────────────────
_keys_cache: dict[str, dict] = {}   # token -> {tier, daily_limit, owner_email}
_keys_cache_time: float = 0.0
_usage: dict[str, dict] = {}        # token -> {"date": "YYYY-MM-DD", "count": int}


def _refresh_keys() -> None:
    """Fetch active keys from Supabase (cached; called at most every TTL)."""
    global _keys_cache, _keys_cache_time
    now = datetime.now(timezone.utc).timestamp()
    if _keys_cache and (now - _keys_cache_time) < KEY_CACHE_TTL:
        return
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("api_keys: SUPABASE_URL / key not set — token auth disabled")
        _keys_cache, _keys_cache_time = {}, now
        return
    try:
        import httpx
        resp = httpx.get(
            f"{SUPABASE_URL}/rest/v1/she_api_keys",
            params={"select": "token,tier,daily_limit,owner_email,active", "active": "eq.true"},
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=4.0,
        )
        rows = resp.json() if resp.status_code == 200 else []
        _keys_cache = {
            r["token"]: {
                "tier": r.get("tier", "free"),
                "daily_limit": r.get("daily_limit"),
                "owner_email": r.get("owner_email"),
            }
            for r in rows if r.get("token")
        }
        _keys_cache_time = now
        logger.info(f"api_keys: refreshed {len(_keys_cache)} active keys")
    except Exception as e:
        logger.warning(f"api_keys: refresh failed ({e}); keeping previous cache")
        _keys_cache_time = now  # avoid hammering on repeated failures


def validate_token(token: str) -> dict | None:
    """Return {tier, daily_limit, owner_email} for a valid active token, else None."""
    if not token:
        return None
    _refresh_keys()
    info = _keys_cache.get(token)
    if not info:
        return None
    tier = info["tier"]
    # Explicit per-key limit overrides the tier default
    limit = info["daily_limit"] if info.get("daily_limit") is not None else TIER_DAILY_LIMITS.get(tier, 5_000)
    return {"tier": tier, "daily_limit": limit, "owner_email": info.get("owner_email")}


def check_quota(token: str, limit: int) -> tuple[bool, int]:
    """
    Count one call against a token's daily quota (in-memory, resets daily).
    Returns (allowed, remaining). limit == -1 means unlimited.
    """
    if limit == -1:
        return True, -1
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rec = _usage.get(token)
    if not rec or rec["date"] != today:
        rec = {"date": today, "count": 0}
        _usage[token] = rec
    if rec["count"] >= limit:
        return False, 0
    rec["count"] += 1
    return True, limit - rec["count"]
