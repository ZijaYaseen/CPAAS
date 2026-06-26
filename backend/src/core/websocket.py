"""Realtime WebSocket gateway backed by Redis pub/sub.

Horizontal scaling: each backend instance keeps only its *local* connections. All
inbox events are published to a single Redis channel (``ws:events``) with the
tenant id in the payload; every instance subscribes and fans out to the local
connections belonging to that tenant. This keeps the backend stateless — the only
shared state is Redis.

Event types (constitution III): ``message_created``, ``message_updated``,
``assignment_changed``.
"""

import asyncio
import json
from collections import defaultdict

import redis.asyncio as redis
from fastapi import WebSocket

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger("ws")

WS_CHANNEL = "ws:events"


class ConnectionManager:
    """Tracks local WebSocket connections grouped by tenant."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._listener_task: asyncio.Task | None = None
        self._pub: redis.Redis = redis.from_url(settings.redis_url, decode_responses=True)

    async def connect(self, ws: WebSocket, tenant_id: str) -> None:
        await ws.accept()
        self._connections[tenant_id].add(ws)
        logger.info("ws_connect", tenant_id=tenant_id, count=len(self._connections[tenant_id]))

    def disconnect(self, ws: WebSocket, tenant_id: str) -> None:
        conns = self._connections.get(tenant_id)
        if conns:
            conns.discard(ws)
            if not conns:
                self._connections.pop(tenant_id, None)

    async def emit(self, tenant_id: str, event_type: str, data: dict) -> None:
        """Publish an event to all instances via Redis."""
        payload = json.dumps({"tenant_id": str(tenant_id), "type": event_type, "data": data})
        await self._pub.publish(WS_CHANNEL, payload)

    async def _broadcast_local(self, tenant_id: str, message: str) -> None:
        conns = list(self._connections.get(tenant_id, set()))
        dead: list[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:  # noqa: BLE001 — connection dropped
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, tenant_id)

    async def _listen(self) -> None:
        sub = self._pub.pubsub()
        await sub.subscribe(WS_CHANNEL)
        logger.info("ws_listener_started")
        async for msg in sub.listen():
            if msg.get("type") != "message":
                continue
            try:
                envelope = json.loads(msg["data"])
                tenant_id = envelope["tenant_id"]
            except (KeyError, json.JSONDecodeError):
                continue
            await self._broadcast_local(tenant_id, msg["data"])

    async def start(self) -> None:
        if self._listener_task is None:
            self._listener_task = asyncio.create_task(self._listen())

    async def stop(self) -> None:
        if self._listener_task:
            self._listener_task.cancel()
        await self._pub.aclose()


manager = ConnectionManager()


async def emit_event(tenant_id: str, event_type: str, data: dict) -> None:
    """Convenience helper used by services to broadcast an inbox event."""
    await manager.emit(tenant_id, event_type, data)
