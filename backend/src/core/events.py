"""Synchronous event publishing for Celery workers.

Workers run outside the async event loop, so they publish realtime events to the
same Redis channel the WebSocket gateway listens on, using a sync Redis client.
"""

import json

import redis

from src.core.config import settings
from src.core.websocket import WS_CHANNEL

_sync_redis = redis.from_url(settings.redis_url, decode_responses=True)


def publish_event(tenant_id: str, event_type: str, data: dict) -> None:
    payload = json.dumps({"tenant_id": str(tenant_id), "type": event_type, "data": data})
    _sync_redis.publish(WS_CHANNEL, payload)
