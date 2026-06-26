"""Inbox ORM models: Conversation, Message, MessageStatus.

These are the channel-normalized core of the product — every channel adapter maps
inbound/outbound traffic onto this uniform schema.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models import Base, TenantMixin, TimestampMixin, uuid_pk


class ConversationStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class MessageDirection(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"


class SenderType(str, enum.Enum):
    contact = "contact"
    user = "user"
    ai_agent = "ai_agent"


class DeliveryStatus(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class Conversation(Base, TenantMixin, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = uuid_pk()
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channel_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ConversationStatus.open.value
    )
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to_team_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base, TenantMixin, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = uuid_pk()
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(50), nullable=False)
    sender_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_urls: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    channel_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Internal agent-only note (not delivered to the contact). MVP "internal notes".
    is_internal_note: Mapped[bool] = mapped_column(default=False, nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    statuses: Mapped[list["MessageStatus"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class MessageStatus(Base, TenantMixin):
    __tablename__ = "message_status"

    id: Mapped[uuid.UUID] = uuid_pk()
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    channel_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    message: Mapped["Message"] = relationship(back_populates="statuses")
