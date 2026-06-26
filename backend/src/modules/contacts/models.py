"""Contact ORM model (CRM). MVP uses auto-creation + dedup; full CRM is post-MVP."""

import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import Base, SoftDeleteMixin, TenantMixin, TimestampMixin, uuid_pk


class Contact(Base, TenantMixin, TimestampMixin, SoftDeleteMixin):
    """A customer/lead. Channel identifiers (WhatsApp WAID, etc.) live in extra_data."""

    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_contacts_tenant_email"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    lifecycle_stage: Mapped[str] = mapped_column(String(50), default="lead")
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
