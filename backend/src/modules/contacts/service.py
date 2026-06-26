"""Contact services. MVP scope: auto-creation from inbound messages + dedup.

Dedup strategy: match on email first, then phone, within the tenant. Channel-native
identifiers (WhatsApp WAID, webchat session id, email address) are kept in
``extra_data['channels']`` so future inbound messages resolve to the same contact.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.contacts.models import Contact


async def get_or_create_contact(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    email: str | None = None,
    phone: str | None = None,
    full_name: str | None = None,
    channel_type: str | None = None,
    channel_identifier: str | None = None,
) -> Contact:
    """Find an existing contact by email/phone/channel-id, or create a new one."""
    contact: Contact | None = None
    email = email.strip().lower() if email else None  # normalize for reliable dedup

    if email:
        contact = await db.scalar(select(Contact).where(Contact.email == email))
    if contact is None and phone:
        contact = await db.scalar(select(Contact).where(Contact.phone == phone))
    if contact is None and channel_identifier:
        # Match on a previously-seen channel identifier stored in metadata.
        contact = await db.scalar(
            select(Contact).where(
                Contact.extra_data["channels"].op("->>")(channel_type) == channel_identifier
            )
        )

    if contact is not None:
        _record_channel_identity(contact, channel_type, channel_identifier)
        if full_name and not contact.full_name:
            contact.full_name = full_name
        if email and not contact.email:
            contact.email = email
        return contact

    channels = {}
    if channel_type and channel_identifier:
        channels[channel_type] = channel_identifier
    contact = Contact(
        tenant_id=tenant_id,
        email=email,
        phone=phone,
        full_name=full_name,
        extra_data={"channels": channels} if channels else None,
    )
    db.add(contact)
    await db.flush()
    return contact


def _record_channel_identity(
    contact: Contact, channel_type: str | None, channel_identifier: str | None
) -> None:
    if not (channel_type and channel_identifier):
        return
    data = dict(contact.extra_data or {})
    channels = dict(data.get("channels", {}))
    channels[channel_type] = channel_identifier
    data["channels"] = channels
    contact.extra_data = data
