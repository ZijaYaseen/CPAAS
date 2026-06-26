"""FastAPI application entrypoint.

Wires up logging, middleware, error handlers, CORS, the health check, and the
versioned API router. Business logic lives in ``src.modules.*``.
"""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.core import database, redis
from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.core.logging import configure_logging, get_logger
from src.core.middleware import register_csrf, register_exception_handlers, register_middleware
from src.core.ratelimit import register_rate_limit
from src.core.sentry import init_sentry
from src.core.telemetry import init_telemetry
from src.core.websocket import manager
from src.modules.ai.router import router as ai_router
from src.modules.audit.router import router as audit_router
from src.modules.auth.router import router as auth_router
from src.modules.auth.service import get_user_for_token
from src.modules.channels.router import router as channels_router
from src.modules.channels.router import webhooks_router
from src.modules.inbox.router import router as inbox_router
from src.modules.knowledge.router import router as knowledge_router

configure_logging()
init_sentry()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("startup", environment=settings.environment)
    await manager.start()
    yield
    await manager.stop()
    await database.engine.dispose()
    await redis.redis_client.aclose()
    logger.info("shutdown")


app = FastAPI(
    title="Unified Communication Platform API",
    version="0.1.0",
    description="AI-powered multi-tenant unified communication platform (MVP).",
    lifespan=lifespan,
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middleware(app)
register_csrf(app)
register_rate_limit(app)
register_exception_handlers(app)
init_telemetry(app)  # no-op unless OTEL_EXPORTER_ENDPOINT + packages present


# ---- Health ----
@app.get("/health", tags=["system"])
async def health():
    db_ok = redis_ok = False
    try:
        db_ok = await database.ping()
    except Exception as exc:  # noqa: BLE001
        logger.warning("health_db_fail", error=str(exc))
    try:
        redis_ok = await redis.ping()
    except Exception as exc:  # noqa: BLE001
        logger.warning("health_redis_fail", error=str(exc))
    status = "ok" if (db_ok and redis_ok) else "degraded"
    return {"status": status, "database": db_ok, "redis": redis_ok}


# ---- WebSocket gateway ----
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Authenticated realtime stream. Auth via the session cookie sent on upgrade."""
    token = websocket.cookies.get(settings.session_cookie_name)
    if not token:
        await websocket.close(code=4401)
        return
    async with AsyncSessionLocal() as session:
        user = await get_user_for_token(session, token)
    if user is None:
        await websocket.close(code=4401)
        return

    tenant_id = str(user.tenant_id)
    await manager.connect(websocket, tenant_id)
    try:
        while True:
            # We don't process inbound WS messages in MVP; keep the socket alive.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, tenant_id)


# ---- Versioned API ----
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth_router)
api_v1.include_router(inbox_router)
api_v1.include_router(channels_router)
api_v1.include_router(ai_router)
api_v1.include_router(knowledge_router)
api_v1.include_router(audit_router)
app.include_router(api_v1)

# Webhooks live outside /api/v1 (public, channel-provider callbacks).
app.include_router(webhooks_router)
