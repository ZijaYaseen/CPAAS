"""Async database engine, session management, and Row-Level Security helpers.

Multi-tenant isolation is enforced at the PostgreSQL level via RLS policies that
read the `app.current_tenant_id` session variable. Every request that touches
tenant-scoped tables MUST set this variable on its DB session via
``set_tenant_context`` (the tenant middleware/dependency wires this up).
"""

import time
from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger("db")

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------
# Neon's pooled endpoint runs PgBouncer (transaction mode), which is incompatible
# with asyncpg's prepared-statement cache — disable it to avoid "prepared statement
# already exists" errors. Harmless on non-pooled endpoints too.
_connect_args = {"statement_cache_size": 0} if "asyncpg" in settings.database_url else {}

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,  # recycle connections every 30 min (Neon-friendly)
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# Slow query logging — warn when a statement exceeds the configured threshold.
# ---------------------------------------------------------------------------
@event.listens_for(engine.sync_engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.monotonic()


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    elapsed_ms = (time.monotonic() - getattr(context, "_query_start_time", time.monotonic())) * 1000
    if elapsed_ms >= settings.slow_query_ms:
        logger.warning("slow_query", duration_ms=round(elapsed_ms, 1), statement=statement[:300])


async def set_tenant_context(session: AsyncSession, tenant_id: str) -> None:
    """Set the per-transaction tenant id used by RLS policies.

    Uses ``SET LOCAL`` so the value is scoped to the current transaction and
    cleared automatically on commit/rollback — safe for pooled connections.
    """
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(tenant_id)},
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a DB session (no tenant context).

    Use for unauthenticated paths (auth, webhooks). Tenant-scoped routes should
    depend on ``get_tenant_db`` instead (see modules/auth/dependencies.py).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def ping() -> bool:
    """Lightweight connectivity check for the health endpoint."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    return True
