"""Redis-backed fixed-window rate limiting middleware.

Limits requests per identifier (authenticated session token, else client IP) per
minute. Stateless across backend instances since the counter lives in Redis.
"""

import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.redis import redis_client


def _identifier(request: Request) -> str:
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        return f"sess:{token[:24]}"
    client = request.client.host if request.client else "unknown"
    return f"ip:{client}"


def register_rate_limit(app: FastAPI) -> None:
    if not settings.rate_limit_enabled:
        return

    limit = settings.rate_limit_per_minute

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Only throttle the API surface; skip health and docs.
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        window = int(time.time() // 60)
        key = f"ratelimit:{_identifier(request)}:{window}"
        try:
            count = await redis_client.incr(key)
            if count == 1:
                await redis_client.expire(key, 60)
        except Exception:  # noqa: BLE001 — never fail open-loudly if Redis is down
            return await call_next(request)

        if count > limit:
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limited", "message": "Too many requests"}},
                headers={"Retry-After": "60"},
            )
        return await call_next(request)
