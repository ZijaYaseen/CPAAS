"""Knowledge base request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    source_type: str = Field(pattern="^(text|url)$")
    content: str | None = None
    source_url: str | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    source_type: str
    status: str
    is_active: bool
    created_at: datetime


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    content: str
    score: float
