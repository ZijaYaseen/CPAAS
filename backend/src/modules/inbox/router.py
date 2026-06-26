"""Inbox API routes (tenant-scoped, authenticated)."""

import uuid

from fastapi import APIRouter, Query

from src.modules.auth.dependencies import CurrentUser, TenantDB
from src.modules.inbox import service
from src.modules.inbox.schemas import (
    AssignRequest,
    ContactSummary,
    ConversationResponse,
    CreateNoteRequest,
    MessageResponse,
    SendMessageRequest,
)

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    db: TenantDB,
    _user: CurrentUser,
    status: str | None = Query(default=None),
    assigned_to_me: bool = Query(default=False),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows = await service.list_conversations(
        db,
        status=status,
        assigned_to_user_id=_user.id if assigned_to_me else None,
        limit=limit,
        offset=offset,
    )
    return [
        ConversationResponse(
            **{
                k: getattr(row["conversation"], k)
                for k in (
                    "id",
                    "status",
                    "channel_account_id",
                    "assigned_to_user_id",
                    "assigned_to_team_id",
                    "last_message_at",
                    "created_at",
                )
            },
            contact=ContactSummary.model_validate(row["contact"]),
            last_message_preview=row["last_message_preview"],
            channel_type=row.get("channel_type"),
        )
        for row in rows
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: uuid.UUID,
    db: TenantDB,
    _user: CurrentUser,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    messages = await service.list_messages(db, conversation_id, limit=limit, offset=offset)
    return [MessageResponse.model_validate(m) for m in messages]


@router.post(
    "/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=201
)
async def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    db: TenantDB,
    user: CurrentUser,
):
    msg = await service.send_outbound(
        db,
        tenant_id=user.tenant_id,
        conversation_id=conversation_id,
        content=payload.content,
        sender_user_id=user.id,
        media_urls=payload.media_urls,
    )
    return MessageResponse.model_validate(msg)


@router.put("/conversations/{conversation_id}/assign", response_model=ConversationResponse)
async def assign(
    conversation_id: uuid.UUID,
    payload: AssignRequest,
    db: TenantDB,
    user: CurrentUser,
):
    conv = await service.assign_conversation(
        db,
        tenant_id=user.tenant_id,
        conversation_id=conversation_id,
        user_id=payload.assigned_to_user_id,
        team_id=payload.assigned_to_team_id,
    )
    from sqlalchemy import select

    from src.modules.contacts.models import Contact

    contact = await db.scalar(select(Contact).where(Contact.id == conv.contact_id))
    return ConversationResponse(
        id=conv.id,
        status=conv.status,
        channel_account_id=conv.channel_account_id,
        assigned_to_user_id=conv.assigned_to_user_id,
        assigned_to_team_id=conv.assigned_to_team_id,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        contact=ContactSummary.model_validate(contact),
    )


@router.post(
    "/conversations/{conversation_id}/notes", response_model=MessageResponse, status_code=201
)
async def add_note(
    conversation_id: uuid.UUID,
    payload: CreateNoteRequest,
    db: TenantDB,
    user: CurrentUser,
):
    note = await service.add_internal_note(
        db,
        tenant_id=user.tenant_id,
        conversation_id=conversation_id,
        content=payload.content,
        user_id=user.id,
    )
    return MessageResponse.model_validate(note)
