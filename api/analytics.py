"""
SHEtoken API — Analytics Middleware
=====================================
Tracks every API call:
  - Which endpoint was called
  - How many times
  - Response time
  - Status code
  - Date/week

Storage options (configure in .env):
  ANALYTICS_BACKEND=memory    → in-memory (resets on redeploy, for dev)
  ANALYTICS_BACKEND=supabase  → Supabase table (permanent, free tier)
  ANALYTICS_BACKEND=sheets    → Google Sheets tab (easy to view)
  ANALYTICS_BACKEND=file      → local JSON file (simple, portable)
"""

import os, json, time, logging
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

BACKEND = os.getenv("ANALYTICS_BACKEND", "memory")

# ── IN-MEMORY STORE ───────────────────────────────────────────────────────────
# Resets when API restarts. Good for development / quick checks.

_calls = defaultdict(int)           # endpoint → total calls
_calls_today = defaultdict(int)     # endpoint → calls today
_response_times = defaultdict(list) # endpoint → list of ms
_errors = defaultdict(int)          # endpoint → error count
_last_called = {}                   # endpoint → last called timestamp
_total_calls = 0
_start_time = datetime.now(timezone.utc)


def record_call(endpoint: str, status_code: int, duration_ms: float):
    """Record a single API call."""
    global _total_calls
    _total_calls += 1
    _calls[endpoint] += 1
    _calls_today[endpoint] += 1
    _last_called[endpoint] = datetime.now(timezone.utc).isoformat()
    _response_times[endpoint].append(duration_ms)
    # Keep only last 100 response times per endpoint
    if len(_response_times[endpoint]) > 100:
        _response_times[endpoint] = _response_times[endpoint][-100:]
    if status_code >= 400:
        _errors[endpoint] += 1

    # If Supabase configured, also log there
    if BACKEND == "supabase":
        _log_to_supabase(endpoint, status_code, duration_ms)
    elif BACKEND == "file":
        _log_to_file(endpoint, status_code, duration_ms)


def get_stats() -> dict:
    """Return current analytics summary."""
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()
    top_endpoints = sorted(_calls.items(), key=lambda x: x[1], reverse=True)

    endpoint_details = []
    for ep, count in top_endpoints:
        times = _response_times.get(ep, [])
        avg_ms = round(sum(times)/len(times), 1) if times else 0
        endpoint_details.append({
            "endpoint":       ep,
            "total_calls":    count,
            "errors":         _errors.get(ep, 0),
            "error_rate_pct": round(_errors.get(ep,0)/count*100, 1) if count else 0,
            "avg_response_ms": avg_ms,
            "last_called":    _last_called.get(ep, ""),
        })

    return {
        "total_calls":         _total_calls,
        "uptime_hours":        round(uptime / 3600, 1),
        "calls_per_hour":      round(_total_calls / max(uptime/3600, 0.01), 1),
        "unique_endpoints":    len(_calls),
        "api_start_time":      _start_time.isoformat(),
        "top_endpoints":       endpoint_details[:20],
        "backend":             BACKEND,
        "generated_at":        datetime.now(timezone.utc).isoformat(),
    }


# ── SUPABASE BACKEND ──────────────────────────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def _log_to_supabase(endpoint: str, status_code: int, duration_ms: float):
    """Log call to Supabase api_calls table."""
    try:
        import httpx
        now = datetime.now(timezone.utc)
        httpx.post(
            f"{SUPABASE_URL}/rest/v1/api_calls",
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type":  "application/json",
                "Prefer":        "return=minimal",
            },
            json={
                "endpoint":    endpoint,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 1),
                "called_at":   now.isoformat(),
                "week":        now.strftime("%Y-W%W"),
                "date":        now.strftime("%Y-%m-%d"),
            },
            timeout=2.0,
        )
    except Exception:
        pass   # Never let analytics break the API


# ── FILE BACKEND ──────────────────────────────────────────────────────────────

_log_file = Path(__file__).parent / "analytics_log.jsonl"

def _log_to_file(endpoint: str, status_code: int, duration_ms: float):
    """Append call to local JSONL file."""
    try:
        now = datetime.now(timezone.utc)
        record = {
            "endpoint":    endpoint,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 1),
            "called_at":   now.isoformat(),
            "week":        now.strftime("%Y-W%W"),
        }
        with open(_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


# ── FASTAPI MIDDLEWARE ────────────────────────────────────────────────────────

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Intercepts every request and records it.
    Adds < 1ms overhead per request.
    """
    SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip health checks and docs
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        # Normalise path (remove specific IDs for grouping)
        # e.g. /v1/wei/countries/IND → /v1/wei/countries/{iso}
        path = _normalise_path(request.url.path)
        record_call(path, response.status_code, duration_ms)

        return response


def _normalise_path(path: str) -> str:
    """Group paths with IDs into a single endpoint key."""
    parts = path.split("/")
    normalised = []
    for i, part in enumerate(parts):
        # Known dynamic segments
        if i > 0:
            prev = parts[i-1] if i > 0 else ""
            if prev in ("countries","cities","states","country","gpi") and part and part[0].isupper():
                part = "{id}"
            elif prev in ("india-states",) and len(part) == 2:
                part = "{code}"
        normalised.append(part)
    return "/".join(normalised)
