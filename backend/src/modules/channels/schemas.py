"""Channel request/response schemas."""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class WhatsAppConnectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone_number_id: str
    access_token: str
    app_secret: str | None = None


class EmailConnectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    from_address: str
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    inbound_address: str | None = None


class WebChatCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ChannelAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_type: str
    name: str
    is_active: bool


class WebChatMessageRequest(BaseModel):
    channel_account_id: uuid.UUID
    session_id: str
    content: str = Field(min_length=1, max_length=10000)
    visitor_name: str | None = None
    page_url: str | None = None
    client_message_id: str | None = None
