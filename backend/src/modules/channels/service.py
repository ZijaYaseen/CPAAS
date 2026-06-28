"""Channel services: adapter registry, credential encryption, inbound/outbound flow.

This module is the bridge between provider-specific adapters and the channel-agnostic
inbox. Inbound payloads are normalized and ingested; outbound messages are delivered
via the right adapter and their delivery status recorded.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.crypto import decrypt_dict, encrypt_dict
from src.core.database import set_tenant_context
from src.core.exceptions import NotFoundError, ValidationError
from src.core.logging import get_logger
from src.modules.channels.base import ChannelAdapter
from src.modules.channels.email import EmailAdapter
from src.modules.channels.models import MVP_CHANNELS, ChannelAccount, ChannelType
from src.modules.channels.webchat import WebChatAdapter
from src.modules.channels.whatsapp import WhatsAppAdapter
from src.modules.contacts.models import Contact
from src.modules.inbox import service as inbox_service
from src.modules.inbox.models import Conversation, DeliveryStatus, Message, MessageStatus

logger = get_logger("channels")

_ADAPTERS: dict[str, ChannelAdapter] = {
    ChannelType.whatsapp.value: WhatsAppAdapter(),
    ChannelType.email.value: EmailAdapter(),
    ChannelType.webchat.value: WebChatAdapter(),
}


def get_adapter(channel_type: str) -> ChannelAdapter:
    adapter = _ADAPTERS.get(channel_type)
    if adapter is None:
        raise ValidationError(f"Unsupported or post-MVP channel: {channel_type}")
    return adapter


# ---- Credential storage (encrypted at rest) ----


async def create_channel_account(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    channel_type: str,
    name: str,
    credentials: dict,
    configuration: dict | None = None,
) -> ChannelAccount:
    if ChannelType(channel_type) not in MVP_CHANNELS:
        raise ValidationError(f"Channel '{channel_type}' is not available in the MVP")
    account = ChannelAccount(
        tenant_id=tenant_id,
        channel_type=channel_type,
        name=name,
        credentials={"_enc": encrypt_dict(credentials)},
        configuration=configuration,
    )
    db.add(account)
    await db.flush()
    return account


def get_credentials(account: ChannelAccount) -> dict:
    enc = (account.credentials or {}).get("_enc")
    return decrypt_dict(enc) if enc else {}


# ---- Inbound ----


async def _resolve_accounts(
    db: AsyncSession, *, channel_type: str, hint: str | None
) -> list[ChannelAccount]:
    """Return ALL active channel accounts that match the inbound hint (cross-tenant).

    No fallback — if no exact match, return empty so the caller logs a warning
    and drops the message rather than routing it to the wrong tenant.
    """
    base_stmt = select(ChannelAccount).where(
        ChannelAccount.channel_type == channel_type, ChannelAccount.is_active.is_(True)
    )
    if channel_type == ChannelType.whatsapp.value and hint:
        return list((await db.scalars(
            base_stmt.where(ChannelAccount.configuration["phone_number_id"].astext == hint)
        )).all())
    if channel_type == ChannelType.email.value and hint:
        # Normalise: strip display name ("Zija <zija@gmail.com>" → "zija@gmail.com")
        addr = hint.split("<")[-1].strip(">").strip().lower() if "<" in hint else hint.strip().lower()
        return list((await db.scalars(
            base_stmt.where(ChannelAccount.configuration["inbound_address"].astext == addr)
        )).all())
    return []


async def process_inbound(db: AsyncSession, *, channel_type: str, payload: dict) -> int:
    """Parse a provider payload and ingest every message it contains. Returns count."""
    adapter = get_adapter(channel_type)
    inbounds = adapter.parse_inbound(payload)
    count = 0
    for inbound in inbounds:
        hint = (
            inbound.channel_metadata.get("phone_number_id")
            if channel_type == ChannelType.whatsapp.value
            else inbound.channel_metadata.get("to")
        )
        accounts = await _resolve_accounts(db, channel_type=channel_type, hint=hint)
        if not accounts:
            logger.warning("inbound_no_channel_account", channel_type=channel_type, hint=hint)
            continue
        for account in accounts:
            await set_tenant_context(db, str(account.tenant_id))
            await inbox_service.ingest_inbound(db, channel_account=account, inbound=inbound)
            count += 1
    return count


async def process_webchat_inbound(
    db: AsyncSession, *, channel_account_id: uuid.UUID, payload: dict
) -> Message:
    """Ingest a web chat widget message (channel account is known from the widget)."""
    account = await db.scalar(select(ChannelAccount).where(ChannelAccount.id == channel_account_id))
    if account is None:
        raise NotFoundError("Web chat channel not found")
    await set_tenant_context(db, str(account.tenant_id))
    adapter = get_adapter(ChannelType.webchat.value)
    inbound = adapter.parse_inbound(payload)[0]
    return await inbox_service.ingest_inbound(db, channel_account=account, inbound=inbound)


# ---- Outbound delivery ----


def _recipient_for(channel_type: str, contact: Contact) -> str | None:
    if channel_type == ChannelType.whatsapp.value:
        return (contact.extra_data or {}).get("channels", {}).get("whatsapp") or contact.phone
    if channel_type == ChannelType.email.value:
        return contact.email
    if channel_type == ChannelType.webchat.value:
        return (contact.extra_data or {}).get("channels", {}).get("webchat")
    return None


async def deliver_message(
    db: AsyncSession, *, tenant_id: uuid.UUID, message_id: uuid.UUID
) -> DeliveryStatus:
    """Send an outbound message via its channel and record the delivery status.

    Returns the final :class:`DeliveryStatus`. The caller (worker) is responsible
    for broadcasting the ``message_updated`` event via the sync publisher, since
    this runs outside the API's async event loop.
    """
    await set_tenant_context(db, str(tenant_id))
    message = await db.scalar(select(Message).where(Message.id == message_id))
    if message is None or message.is_internal_note:
        return DeliveryStatus.failed
    conv = await db.scalar(select(Conversation).where(Conversation.id == message.conversation_id))
    if conv is None or conv.channel_account_id is None:
        return await _record_status(
            db, message, DeliveryStatus.failed, "No channel for conversation"
        )
    account = await db.scalar(
        select(ChannelAccount).where(ChannelAccount.id == conv.channel_account_id)
    )
    contact = await db.scalar(select(Contact).where(Contact.id == conv.contact_id))
    if account is None or contact is None:
        return await _record_status(db, message, DeliveryStatus.failed, "Missing channel/contact")

    adapter = get_adapter(account.channel_type)
    recipient = _recipient_for(account.channel_type, contact)
    if not recipient:
        return await _record_status(db, message, DeliveryStatus.failed, "No recipient address")

    result = await adapter.send(
        credentials=get_credentials(account),
        recipient=recipient,
        content=message.content or "",
        media_urls=message.media_urls,
    )
    if result.success:
        if result.external_message_id:
            meta = dict(message.channel_metadata or {})
            meta["external_message_id"] = result.external_message_id
            message.channel_metadata = meta
        return await _record_status(db, message, DeliveryStatus.sent)
    return await _record_status(db, message, DeliveryStatus.failed, result.error)


async def _record_status(
    db: AsyncSession, message: Message, status: DeliveryStatus, error: str | None = None
) -> DeliveryStatus:
    db.add(
        MessageStatus(
            tenant_id=message.tenant_id,
            message_id=message.id,
            status=status.value,
            error_message=error,
        )
    )
    await db.flush()
    return status
