"""Inbox business logic: conversation queries, inbound ingestion, outbound send.

Realtime: every state change persists first, then emits a WebSocket event
(constitution III — events are replayable from the DB). Outbound delivery is
handed to a worker via Celery so the API stays responsive.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError, ValidationError
from src.core.websocket import emit_event
from src.modules.channels.base import NormalizedInbound
from src.modules.channels.models import ChannelAccount
from src.modules.contacts.models import Contact
from src.modules.contacts.service import get_or_create_contact
from src.modules.inbox.models import (
    Conversation,
    ConversationStatus,
    Message,
    MessageDirection,
    SenderType,
)

# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


async def list_conversations(
    db: AsyncSession,
    *,
    status: str | None = None,
    assigned_to_user_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Return conversations (newest activity first) with contact + last-message preview."""
    stmt = select(Conversation)
    if status:
        stmt = stmt.where(Conversation.status == status)
    if assigned_to_user_id:
        stmt = stmt.where(Conversation.assigned_to_user_id == assigned_to_user_id)
    stmt = stmt.order_by(desc(Conversation.last_message_at)).limit(limit).offset(offset)

    conversations = list((await db.scalars(stmt)).all())
    if not conversations:
        return []

    contact_ids = {c.contact_id for c in conversations}
    contacts = {
        c.id: c
        for c in (await db.scalars(select(Contact).where(Contact.id.in_(contact_ids)))).all()
    }

    # Last message per conversation (DISTINCT ON for a single round-trip).
    conv_ids = [c.id for c in conversations]
    last_msgs_stmt = (
        select(Message)
        .where(Message.conversation_id.in_(conv_ids), Message.is_internal_note.is_(False))
        .order_by(Message.conversation_id, desc(Message.created_at))
        .distinct(Message.conversation_id)
    )
    last_by_conv: dict[uuid.UUID, Message] = {
        m.conversation_id: m for m in (await db.scalars(last_msgs_stmt)).all()
    }

    result = []
    for conv in conversations:
        last = last_by_conv.get(conv.id)
        result.append(
            {
                "conversation": conv,
                "contact": contacts.get(conv.contact_id),
                "last_message_preview": (last.content[:120] if last and last.content else None),
            }
        )
    return result


async def get_conversation(db: AsyncSession, conversation_id: uuid.UUID) -> Conversation:
    conv = await db.scalar(select(Conversation).where(Conversation.id == conversation_id))
    if conv is None:
        raise NotFoundError("Conversation not found")
    return conv


async def list_messages(
    db: AsyncSession, conversation_id: uuid.UUID, *, limit: int = 100, offset: int = 0
) -> list[Message]:
    await get_conversation(db, conversation_id)  # ensures existence within tenant (RLS)
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
        .offset(offset)
    )
    return list((await db.scalars(stmt)).all())


# ---------------------------------------------------------------------------
# Inbound ingestion (called by workers / adapters)
# ---------------------------------------------------------------------------


async def _get_or_open_conversation(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    contact_id: uuid.UUID,
    channel_account_id: uuid.UUID | None,
) -> Conversation:
    stmt = (
        select(Conversation)
        .where(
            Conversation.contact_id == contact_id,
            Conversation.status == ConversationStatus.open.value,
        )
        .order_by(desc(Conversation.last_message_at))
    )
    conv = await db.scalar(stmt)
    if conv is not None:
        return conv
    conv = Conversation(
        tenant_id=tenant_id,
        contact_id=contact_id,
        channel_account_id=channel_account_id,
        status=ConversationStatus.open.value,
    )
    db.add(conv)
    await db.flush()
    return conv


async def ingest_inbound(
    db: AsyncSession, *, channel_account: ChannelAccount, inbound: NormalizedInbound
) -> Message:
    """Persist a normalized inbound message: resolve contact, conversation, store, emit."""
    tenant_id = channel_account.tenant_id
    is_email = inbound.channel_type == "email"
    contact = await get_or_create_contact(
        db,
        tenant_id=tenant_id,
        email=inbound.sender_identifier if is_email else None,
        phone=inbound.sender_identifier if inbound.channel_type in ("whatsapp", "sms") else None,
        full_name=inbound.sender_name,
        channel_type=inbound.channel_type,
        channel_identifier=inbound.sender_identifier,
    )
    conv = await _get_or_open_conversation(
        db, tenant_id=tenant_id, contact_id=contact.id, channel_account_id=channel_account.id
    )

    msg = Message(
        tenant_id=tenant_id,
        conversation_id=conv.id,
        direction=MessageDirection.inbound.value,
        sender_type=SenderType.contact.value,
        sender_id=contact.id,
        content=inbound.content,
        media_urls=inbound.media_urls or None,
        channel_metadata={
            "external_message_id": inbound.external_message_id,
            **(inbound.channel_metadata or {}),
        },
    )
    db.add(msg)
    conv.last_message_at = inbound.timestamp or datetime.now(UTC)
    await db.flush()
    # Commit before emitting the WS event so the frontend's follow-up
    # loadConversations() query sees the new data immediately.
    await db.commit()

    await emit_event(
        str(tenant_id),
        "message_created",
        {"conversation_id": str(conv.id), "message_id": str(msg.id), "direction": "inbound"},
    )
    # Trigger AI auto-response for inbound customer messages (US2).
    if inbound.content:
        _enqueue_ai_response(str(tenant_id), str(conv.id), inbound.content)
    return msg


# ---------------------------------------------------------------------------
# Outbound send (agent reply) + internal notes + assignment
# ---------------------------------------------------------------------------


async def send_outbound(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    conversation_id: uuid.UUID,
    content: str,
    sender_user_id: uuid.UUID,
    media_urls: list[str] | None = None,
) -> Message:
    conv = await get_conversation(db, conversation_id)
    msg = Message(
        tenant_id=tenant_id,
        conversation_id=conv.id,
        direction=MessageDirection.outbound.value,
        sender_type=SenderType.user.value,
        sender_id=sender_user_id,
        content=content,
        media_urls=media_urls,
    )
    db.add(msg)
    conv.last_message_at = datetime.now(UTC)
    await db.flush()

    await emit_event(
        str(tenant_id),
        "message_created",
        {"conversation_id": str(conv.id), "message_id": str(msg.id), "direction": "outbound"},
    )
    # Hand delivery to a worker (API → queue → worker → provider → status update).
    _enqueue_delivery(str(tenant_id), str(msg.id))
    return msg


async def add_internal_note(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    conversation_id: uuid.UUID,
    content: str,
    user_id: uuid.UUID,
) -> Message:
    conv = await get_conversation(db, conversation_id)
    note = Message(
        tenant_id=tenant_id,
        conversation_id=conv.id,
        direction=MessageDirection.outbound.value,
        sender_type=SenderType.user.value,
        sender_id=user_id,
        content=content,
        is_internal_note=True,
    )
    db.add(note)
    await db.flush()
    await emit_event(
        str(tenant_id),
        "message_created",
        {"conversation_id": str(conv.id), "message_id": str(note.id), "internal_note": True},
    )
    return note


async def assign_conversation(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID | None,
    team_id: uuid.UUID | None,
) -> Conversation:
    if user_id is None and team_id is None:
        raise ValidationError("Provide assigned_to_user_id or assigned_to_team_id")
    conv = await get_conversation(db, conversation_id)
    conv.assigned_to_user_id = user_id
    conv.assigned_to_team_id = team_id
    await db.flush()
    await emit_event(
        str(tenant_id),
        "assignment_changed",
        {
            "conversation_id": str(conv.id),
            "assigned_to_user_id": str(user_id) if user_id else None,
            "assigned_to_team_id": str(team_id) if team_id else None,
        },
    )
    return conv


def _enqueue_delivery(tenant_id: str, message_id: str) -> None:
    """Enqueue outbound delivery on the messages queue (best-effort)."""
    try:
        from src.celery_app import celery_app

        celery_app.send_task(
            "src.workers.message_processor.deliver_outbound",
            args=[tenant_id, message_id],
            queue="messages",
        )
    except Exception:  # noqa: BLE001 — broker down shouldn't fail the API write
        pass


def _enqueue_ai_response(tenant_id: str, conversation_id: str, prompt: str) -> None:
    """Enqueue an AI auto-response for an inbound customer message (best-effort)."""
    try:
        from src.celery_app import celery_app

        celery_app.send_task(
            "src.workers.ai_executor.respond_to_message",
            args=[tenant_id, conversation_id, prompt],
            queue="ai",
        )
    except Exception:  # noqa: BLE001
        pass
