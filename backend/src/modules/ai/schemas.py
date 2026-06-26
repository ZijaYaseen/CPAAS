"""AI request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AIConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_type: str
    is_enabled: bool
    system_prompt: str | None


class AIConfigUpdateRequest(BaseModel):
    is_enabled: bool | None = None
    system_prompt: str | None = Field(default=None, max_length=8000)


class KillSwitchRequest(BaseModel):
    enabled: bool  # False = disable all AI agents


class AIRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID | None
    agent_type: str
    prompt: str
    response: str | None
    escalated_to_human: bool
    escalation_reason: str | None
    created_at: datetime
    completed_at: datetime | None


class AIToolCallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tool_name: str
    input: dict
    output: dict | None
    error: str | None


class AIRunDetailResponse(AIRunResponse):
    tool_calls: list[AIToolCallResponse]
