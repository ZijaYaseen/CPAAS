"""Shared async Redis client (cache + Celery broker + WebSocket pub/sub)."""

import redis.asyncio as redis

from src.core.config import settings

redis_client: redis.Redis = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def ping() -> bool:
    return bool(await redis_client.ping())
