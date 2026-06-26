"""ChannelAccount ORM model — a connected communication channel for a tenant."""

import enum
import uuid

from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import Base, TenantMixin, TimestampMixin, uuid_pk


class ChannelType(str, enum.Enum):
    whatsapp = "whatsapp"
    email = "email"
    webchat = "webchat"
    # Post-MVP:
    sms = "sms"
    instagram = "instagram"
    facebook = "facebook"
    voice = "voice"


# Channels available in the MVP build.
MVP_CHANNELS = {ChannelType.whatsapp, ChannelType.email, ChannelType.webchat}


class ChannelAccount(Base, TenantMixin, TimestampMixin):
    """A connected channel. ``credentials`` holds provider secrets (encrypted at rest)."""

    __tablename__ = "channel_accounts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "channel_type", "name", name="uq_channel_tenant_type_name"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    channel_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    credentials: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    configuration: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
