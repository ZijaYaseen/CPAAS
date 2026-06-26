"""Lightweight Redis JSON cache helpers.

Used for read-mostly data (contact profiles, channel configs). Always tenant-namespace
the key to prevent cross-tenant cache bleed.
"""

import json
from typing import Any

from src.core.redis import redis_client


async def cache_get(key: str) -> Any | None:
    raw = await redis_client.get(key)
    return json.loads(raw) if raw else None


async def cache_set(key: str, value: Any, *, ttl_seconds: int = 300) -> None:
    await redis_client.set(key, json.dumps(value), ex=ttl_seconds)


async def cache_delete(*keys: str) -> None:
    if keys:
        await redis_client.delete(*keys)


def tenant_key(tenant_id: str, *parts: str) -> str:
    """Build a tenant-namespaced cache key."""
    return ":".join(["t", str(tenant_id), *parts])
