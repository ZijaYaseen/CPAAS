"""Auth & tenancy ORM models: Tenant, User, Session, Role, Team.

RBAC for MVP uses the ``User.role`` enum column (super_admin / org_admin / agent
/ read_only). The ``roles``/``user_roles`` tables exist for post-MVP custom roles
but are not required by MVP authorization logic.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, uuid_pk


class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    org_admin = "org_admin"
    agent = "agent"
    read_only = "read_only"


class TenantStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    deleted = "deleted"


class Tenant(Base, TimestampMixin):
    """An organization (business customer). Root of the tenant hierarchy."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=TenantStatus.active.value, index=True
    )
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free")
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")


class User(Base, TenantMixin, TimestampMixin, SoftDeleteMixin):
    """A user account scoped to a tenant."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=UserRole.agent.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Session(Base):
    """An authenticated session. No RLS — looked up before tenant context exists.

    Only a hash of the cookie token is stored at rest (``token`` column holds the
    sha256 of the opaque token issued to the client).
    """

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")


class Role(Base, TenantMixin):
    """Custom role with JSON permissions (post-MVP; table created in MVP migration)."""

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    permissions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Team(Base, TenantMixin, TimestampMixin):
    """A group of users for assignment/routing (members table created in migration)."""

    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_teams_tenant_name"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
