"""
SHEtoken API — Rate Limiter (token-tier aware)
===============================================
Two layers:
  1. TOKEN tiers (Authorization: Bearer <token>, or ?token=<token>)
        free  → 5,000 / day
        paid  → 100,000 / day
        admin → unlimited
     Tokens + tiers live in the she_api_keys Supabase table (see api_keys.py).
  2. PUBLIC (no token) → per-IP sliding-window minute limit (the original behaviour).

A valid token raises you above the anonymous IP limit and gives a daily quota.
An invalid token is treated as anonymous (public IP limit).

Admin: pass your admin token to bypass everything, including /v1/admin endpoints.
"""

import os, time, logging
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from api_keys import validate_token, check_quota

logger = logging.getLogger(__name__)

_request_log: dict = defaultdict(list)

# Public (anonymous) per-minute limits by route prefix
RATE_LIMITS = {
    "/v1/admin":   10,
    "/v1/signals": 30,
    "/v1/markets": 30,
    "/v1/mfi":     30,
    "/docs":       20,
    "/":           60,
}

WHITELIST = set(filter(None, os.getenv("RATE_LIMIT_WHITELIST", "").split(",")))
# Legacy single admin token still honoured (env), in addition to admin-tier tokens in the table.
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def get_limit(path: str) -> int:
    for prefix, limit in RATE_LIMITS.items():
        if path.startswith(prefix):
            return limit
    return 60


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def extract_token(request: Request) -> str:
    """Bearer header takes priority; ?token= is a convenience fallback."""
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return request.query_params.get("token", "").strip()


def is_ip_rate_limited(ip: str, path: str) -> tuple[bool, int]:
    if ip in WHITELIST:
        return False, 999
    limit, now, window = get_limit(path), time.time(), 60
    _request_log[ip] = [t for t in _request_log[ip] if now - t < window]
    count = len(_request_log[ip])
    if count >= limit:
        return True, 0
    _request_log[ip].append(now)
    return False, limit - count - 1


async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path == "/health":
        return await call_next(request)

    token = extract_token(request)

    # ── Admin (env token OR admin-tier table token) → bypass everything ──────
    key_info = validate_token(token) if token else None
    is_admin = (token and ADMIN_TOKEN and token == ADMIN_TOKEN) or (key_info and key_info["tier"] == "admin")

    # /v1/admin routes require admin
    if path.startswith("/v1/admin") and not is_admin:
        raise HTTPException(403, "Admin token required")

    if is_admin:
        response = await call_next(request)
        response.headers["X-RateLimit-Tier"] = "admin"
        response.headers["X-RateLimit-Remaining"] = "unlimited"
        return response

    # ── Valid non-admin token → daily quota by tier ──────────────────────────
    if key_info:
        allowed, remaining = check_quota(token, key_info["daily_limit"])
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Daily quota exceeded",
                    "message": f"Your '{key_info['tier']}' tier allows "
                               f"{key_info['daily_limit']} requests/day.",
                    "upgrade": "Email contact@shetoken.org to raise your limit.",
                    "tier": key_info["tier"],
                },
                headers={"Retry-After": "3600"},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Tier"] = key_info["tier"]
        response.headers["X-RateLimit-Limit"] = str(key_info["daily_limit"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    # ── No / invalid token → anonymous per-IP minute limit ───────────────────
    ip = get_client_ip(request)
    limited, remaining = is_ip_rate_limited(ip, path)
    if limited:
        logger.warning(f"Rate limited (public): {ip} on {path}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too many requests",
                "message": "Anonymous rate limit exceeded. Get a free API token "
                           "for higher limits.",
                "limit": get_limit(path),
                "window": "60 seconds",
                "get_token": "Email contact@shetoken.org",
            },
            headers={"Retry-After": "60"},
        )
    response = await call_next(request)
    response.headers["X-RateLimit-Tier"] = "public"
    response.headers["X-RateLimit-Limit"] = str(get_limit(path))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Window"] = "60s"
    return response
