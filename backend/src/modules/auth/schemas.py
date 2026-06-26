"""Pydantic request/response schemas for auth endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Registers a new organization (tenant) together with its first admin user."""

    organization_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool
    last_login_at: datetime | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    subscription_tier: str


class AuthResponse(BaseModel):
    """Returned on successful register/login (session is set as an HttpOnly cookie)."""

    user: UserResponse
    tenant: TenantResponse
