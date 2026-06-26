"""Audit log API (admin-only, tenant-scoped)."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict

from src.modules.audit import service
from src.modules.auth.dependencies import CurrentUser, TenantDB, require_role
from src.modules.auth.models import UserRole

router = APIRouter(prefix="/audit", tags=["audit"])
AdminOnly = Depends(require_role(UserRole.org_admin, UserRole.super_admin))


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    action: str
    user_id: uuid.UUID | None
    entity_type: str | None
    entity_id: uuid.UUID | None
    details: dict | None
    created_at: datetime


@router.get("/logs", response_model=list[AuditLogResponse])
async def list_logs(
    db: TenantDB,
    _user: CurrentUser,
    _admin=AdminOnly,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    logs = await service.list_logs(db, limit=limit, offset=offset)
    return [AuditLogResponse.model_validate(log) for log in logs]
