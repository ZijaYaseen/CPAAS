"""Auth dependencies: session resolution, tenant-scoped DB, and RBAC guards.

A single generator dependency (``_authenticated``) resolves the session cookie to
a user, opens a DB session, and sets the RLS tenant context. FastAPI caches it
per-request, so ``get_current_user`` and ``get_tenant_db`` share one session/txn.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import AsyncSessionLocal, set_tenant_context
from src.core.exceptions import AuthenticationError, AuthorizationError
from src.modules.auth.models import User, UserRole
from src.modules.auth.service import get_user_for_token


def _extract_token(request: Request) -> str | None:
    return request.cookies.get(settings.session_cookie_name)


async def _authenticated(
    request: Request,
) -> AsyncGenerator[tuple[AsyncSession, User], None]:
    token = _extract_token(request)
    if not token:
        raise AuthenticationError("Not authenticated")

    async with AsyncSessionLocal() as session:
        user = await get_user_for_token(session, token)
        if user is None:
            raise AuthenticationError("Invalid or expired session")
        # Enforce tenant isolation at the DB layer (RLS) for this transaction.
        await set_tenant_context(session, str(user.tenant_id))
        try:
            yield session, user
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    ctx: Annotated[tuple[AsyncSession, User], Depends(_authenticated)],
) -> User:
    return ctx[1]


async def get_tenant_db(
    ctx: Annotated[tuple[AsyncSession, User], Depends(_authenticated)],
) -> AsyncSession:
    return ctx[0]


CurrentUser = Annotated[User, Depends(get_current_user)]
TenantDB = Annotated[AsyncSession, Depends(get_tenant_db)]


def require_role(*allowed: UserRole):
    """Dependency factory enforcing that the current user has one of ``allowed`` roles."""

    allowed_values = {r.value for r in allowed}

    async def _guard(user: CurrentUser) -> User:
        if user.role not in allowed_values:
            raise AuthorizationError("Insufficient permissions for this action")
        return user

    return _guard
