"""Per-task async DB session for Celery workers.

Celery tasks are synchronous and each runs via ``asyncio.run`` in a fresh event
loop, so we build a dedicated NullPool engine per call to avoid sharing connections
across event loops (which asyncpg forbids).
"""

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

# Import all models so SQLAlchemy metadata has every table (including tenants)
# before the worker engine is created. Without this, FK resolution fails.
import src.modules.auth.models  # noqa: F401
import src.modules.inbox.models  # noqa: F401
import src.modules.channels.models  # noqa: F401
import src.modules.contacts.models  # noqa: F401
import src.modules.ai.models  # noqa: F401
import src.modules.knowledge.models  # noqa: F401
import src.modules.audit.service  # noqa: F401

T = TypeVar("T")


@asynccontextmanager
async def worker_session():
    engine = create_async_engine(settings.database_url, poolclass=None, pool_pre_ping=True)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        await engine.dispose()


def run_async(coro_fn: Callable[[AsyncSession], Awaitable[T]]) -> T:
    """Run an async function that needs a worker DB session, in a fresh loop."""

    async def _runner() -> T:
        async with worker_session() as session:
            return await coro_fn(session)

    return asyncio.run(_runner())
