"""
SHEtoken API — Rate Limiter
============================
Limits requests per IP address.
No database needed — uses in-memory sliding window.

Default limits:
  Public endpoints:  60 requests/minute per IP
  /v1/signals:       30 requests/minute per IP
  /v1/admin:         10 requests/minute per IP (your eyes only)

To make /v1/admin private, set ADMIN_TOKEN in .env
and pass it as: GET /v1/admin/stats?token=your_secret
"""

import os, time, logging
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# In-memory store: {ip: [timestamp, timestamp, ...]}
_request_log: dict = defaultdict(list)

# Rate limits per route prefix (requests per minute)
RATE_LIMITS = {
    "/v1/admin":     10,   # your private endpoints
    "/v1/signals":   30,   # signal endpoints
    "/v1/markets":   30,   # prediction markets
    "/v1/mfi":       30,
    "/docs":         20,
    "/":             60,   # everything else
}

# IPs to always allow (your own)
WHITELIST = set(filter(None, os.getenv("RATE_LIMIT_WHITELIST", "").split(",")))

# Admin token for /v1/admin endpoints
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def get_limit(path: str) -> int:
    """Get rate limit for a given path."""
    for prefix, limit in RATE_LIMITS.items():
        if path.startswith(prefix):
            return limit
    return 60


def get_client_ip(request: Request) -> str:
    """Get real client IP, respecting reverse proxy headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def is_rate_limited(ip: str, path: str) -> tuple[bool, int]:
    """
    Check if IP is rate limited.
    Returns (is_limited, requests_remaining)
    """
    if ip in WHITELIST:
        return False, 999

    limit   = get_limit(path)
    now     = time.time()
    window  = 60  # 1 minute sliding window

    # Clean old requests outside window
    _request_log[ip] = [t for t in _request_log[ip] if now - t < window]

    count = len(_request_log[ip])

    if count >= limit:
        return True, 0

    # Record this request
    _request_log[ip].append(now)
    return False, limit - count - 1


async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting."""
    path = request.url.path

    # Skip health check
    if path == "/health":
        return await call_next(request)

    # Check admin token for /v1/admin
    if path.startswith("/v1/admin") and ADMIN_TOKEN:
        token = request.query_params.get("token", "")
        if token != ADMIN_TOKEN:
            raise HTTPException(403, "Admin token required")

    ip = get_client_ip(request)
    limited, remaining = is_rate_limited(ip, path)

    if limited:
        logger.warning(f"Rate limited: {ip} on {path}")
        return JSONResponse(
            status_code=429,
            content={
                "error":   "Too many requests",
                "message": "Rate limit exceeded. Please wait 1 minute.",
                "limit":   get_limit(path),
                "window":  "60 seconds",
                "contact": "contact@shetoken.org",
            },
            headers={"Retry-After": "60"},
        )

    response = await call_next(request)
    # Add rate limit headers to every response
    response.headers["X-RateLimit-Limit"]     = str(get_limit(path))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Window"]    = "60s"
    return response
