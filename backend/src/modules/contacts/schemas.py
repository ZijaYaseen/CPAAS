"""Contact response schemas (MVP)."""

import uuid

from pydantic import BaseModel, ConfigDict


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str | None
    email: str | None
    phone: str | None
    lifecycle_stage: str
