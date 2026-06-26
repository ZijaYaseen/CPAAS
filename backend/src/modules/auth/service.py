"""Authentication business logic: register, login, logout, session lookup.

Backend is the single source of truth for auth. Sessions are opaque tokens
stored hashed; the raw token is delivered to the client in an HttpOnly cookie.
"""

import re
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import AuthenticationError, ConflictError
from src.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from src.modules.auth.models import Session, Tenant, User, UserRole


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "org"
    return f"{base}-{uuid.uuid4().hex[:6]}"


async def register(
    db: AsyncSession, *, organization_name: str, email: str, password: str, full_name: str | None
) -> tuple[User, Tenant]:
    """Create a tenant and its first admin user."""
    email = email.strip().lower()  # normalize to avoid duplicate accounts
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ConflictError("A user with this email already exists", code="email_taken")

    tenant = Tenant(name=organization_name, slug=_slugify(organization_name))
    db.add(tenant)
    await db.flush()  # assign tenant.id

    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=UserRole.org_admin.value,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user, tenant


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User:
    email = email.strip().lower()  # match the normalized form stored at registration
    user = await db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or user.deleted_at is not None:
        raise AuthenticationError("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")
    user.last_login_at = datetime.now(UTC)
    return user


async def create_session(
    db: AsyncSession, *, user: User, ip: str | None, user_agent: str | None
) -> str:
    """Create a session row and return the raw token for the cookie."""
    raw_token = generate_session_token()
    session = Session(
        user_id=user.id,
        token=hash_session_token(raw_token),
        expires_at=datetime.now(UTC) + timedelta(seconds=settings.session_ttl_seconds),
        ip_address=ip,
        user_agent=user_agent,
    )
    db.add(session)
    await db.flush()
    return raw_token


async def get_user_for_token(db: AsyncSession, raw_token: str) -> User | None:
    """Resolve the active user for a raw session token, or None if invalid/expired."""
    token_hash = hash_session_token(raw_token)
    session = await db.scalar(select(Session).where(Session.token == token_hash))
    if session is None:
        return None
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < datetime.now(UTC):
        return None
    user = await db.scalar(select(User).where(User.id == session.user_id))
    if user is None or not user.is_active or user.deleted_at is not None:
        return None
    return user


async def logout(db: AsyncSession, raw_token: str) -> None:
    token_hash = hash_session_token(raw_token)
    session = await db.scalar(select(Session).where(Session.token == token_hash))
    if session is not None:
        await db.delete(session)
