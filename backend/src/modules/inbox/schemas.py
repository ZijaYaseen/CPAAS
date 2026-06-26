"""Inbox request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    direction: str
    sender_type: str
    sender_id: uuid.UUID | None
    content: str | None
    media_urls: list | None
    is_internal_note: bool
    created_at: datetime
    latest_status: str | None = None


class ContactSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str | None
    email: str | None
    phone: str | None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    channel_account_id: uuid.UUID | None
    assigned_to_user_id: uuid.UUID | None
    assigned_to_team_id: uuid.UUID | None
    last_message_at: datetime | None
    created_at: datetime
    contact: ContactSummary
    last_message_preview: str | None = None


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    media_urls: list[str] | None = None


class CreateNoteRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class AssignRequest(BaseModel):
    assigned_to_user_id: uuid.UUID | None = None
    assigned_to_team_id: uuid.UUID | None = None
