"""Channel API routes.

- ``router``: authenticated channel management (connect WhatsApp/Email/Web Chat).
- ``webhooks_router``: PUBLIC provider callbacks + the web chat widget endpoint.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.logging import get_logger
from src.modules.auth.dependencies import CurrentUser, TenantDB
from src.modules.channels import service
from src.modules.channels.models import ChannelAccount, ChannelType
from src.modules.channels.schemas import (
    ChannelAccountResponse,
    EmailConnectRequest,
    WebChatCreateRequest,
    WebChatMessageRequest,
    WhatsAppConnectRequest,
)
from src.modules.contacts.models import Contact
from src.modules.inbox.models import Conversation, Message

logger = get_logger("channels.router")

router = APIRouter(prefix="/channels", tags=["channels"])
webhooks_router = APIRouter(tags=["webhooks"])


# ---------------------------------------------------------------------------
# Authenticated channel management
# ---------------------------------------------------------------------------


@router.get("", response_model=list[ChannelAccountResponse])
async def list_channels(db: TenantDB, _user: CurrentUser):
    accounts = (await db.scalars(select(ChannelAccount))).all()
    return [ChannelAccountResponse.model_validate(a) for a in accounts]


@router.post("/whatsapp/connect", response_model=ChannelAccountResponse, status_code=201)
async def connect_whatsapp(payload: WhatsAppConnectRequest, db: TenantDB, user: CurrentUser):
    account = await service.create_channel_account(
        db,
        tenant_id=user.tenant_id,
        channel_type=ChannelType.whatsapp.value,
        name=payload.name,
        credentials={
            "phone_number_id": payload.phone_number_id,
            "access_token": payload.access_token,
            "app_secret": payload.app_secret,
        },
        configuration={"phone_number_id": payload.phone_number_id},
    )
    return ChannelAccountResponse.model_validate(account)


@router.post("/email/connect", response_model=ChannelAccountResponse, status_code=201)
async def connect_email(payload: EmailConnectRequest, db: TenantDB, user: CurrentUser):
    account = await service.create_channel_account(
        db,
        tenant_id=user.tenant_id,
        channel_type=ChannelType.email.value,
        name=payload.name,
        credentials={
            "from_address": payload.from_address,
            "smtp_host": payload.smtp_host,
            "smtp_port": payload.smtp_port,
            "smtp_user": payload.smtp_user,
            "smtp_password": payload.smtp_password,
        },
        configuration={"inbound_address": payload.inbound_address or payload.from_address},
    )
    return ChannelAccountResponse.model_validate(account)


@router.post("/webchat/create", response_model=ChannelAccountResponse, status_code=201)
async def create_webchat(payload: WebChatCreateRequest, db: TenantDB, user: CurrentUser):
    account = await service.create_channel_account(
        db,
        tenant_id=user.tenant_id,
        channel_type=ChannelType.webchat.value,
        name=payload.name,
        credentials={},
        configuration={},
    )
    return ChannelAccountResponse.model_validate(account)


# ---------------------------------------------------------------------------
# Public webhooks + web chat ingestion
# ---------------------------------------------------------------------------


@webhooks_router.get("/webhooks/whatsapp")
async def whatsapp_verify(request: Request):
    """Meta webhook verification handshake."""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == settings.whatsapp_verify_token
    ):
        return Response(content=params.get("hub.challenge", ""), media_type="text/plain")
    return Response(status_code=403)


@webhooks_router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    body = await request.body()
    adapter = service.get_adapter(ChannelType.whatsapp.value)
    if not adapter.verify_signature(headers=dict(request.headers), body=body):
        return Response(status_code=403)
    payload = await request.json()
    await service.process_inbound(db, channel_type=ChannelType.whatsapp.value, payload=payload)
    return {"status": "received"}


@webhooks_router.post("/webhooks/email")
async def email_webhook(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    # SendGrid Inbound Parse posts multipart form data.
    form = await request.form()
    payload = {k: (v if isinstance(v, str) else None) for k, v in form.items()}
    await service.process_inbound(db, channel_type=ChannelType.email.value, payload=payload)
    return {"status": "received"}


@webhooks_router.post("/api/v1/webchat/messages", status_code=201)
async def webchat_message(
    payload: WebChatMessageRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Public endpoint the embeddable widget posts visitor messages to."""
    msg = await service.process_webchat_inbound(
        db,
        channel_account_id=payload.channel_account_id,
        payload=payload.model_dump(),
    )
    return {"status": "received", "message_id": str(msg.id)}


@webhooks_router.get("/api/v1/webchat/messages")
async def webchat_get_messages(
    channel_account_id: uuid.UUID = Query(...),
    session_id: str = Query(...),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Public endpoint: visitor polls this to receive agent replies."""
    account = await db.scalar(
        select(ChannelAccount).where(ChannelAccount.id == channel_account_id)
    )
    if account is None:
        return {"messages": []}

    from src.core.database import set_tenant_context
    await set_tenant_context(db, str(account.tenant_id))

    contact = await db.scalar(
        select(Contact).where(
            Contact.extra_data["channels"].op("->>")(ChannelType.webchat.value) == session_id
        )
    )
    if contact is None:
        return {"messages": []}

    conv = await db.scalar(
        select(Conversation).where(
            Conversation.contact_id == contact.id,
            Conversation.channel_account_id == channel_account_id,
        )
    )
    if conv is None:
        return {"messages": []}

    msgs = (
        await db.scalars(
            select(Message)
            .where(Message.conversation_id == conv.id, Message.is_internal_note.is_(False))
            .order_by(Message.created_at)
        )
    ).all()

    return {
        "messages": [
            {
                "id": str(m.id),
                "content": m.content,
                "direction": m.direction,
                "sender_type": m.sender_type,
                "created_at": m.created_at.isoformat(),
            }
            for m in msgs
        ]
    }
