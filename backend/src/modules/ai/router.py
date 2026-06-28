"""AI API routes: configuration, kill-switch, run audit logs (tenant-scoped)."""

import uuid

from fastapi import APIRouter, Depends, Query

from src.modules.ai import service
from src.modules.ai.schemas import (
    AIConfigResponse,
    AIConfigUpdateRequest,
    AIRunDetailResponse,
    AIRunResponse,
    AIToolCallResponse,
    KillSwitchRequest,
)
from src.modules.auth.dependencies import CurrentUser, TenantDB, require_role
from src.modules.auth.models import UserRole

router = APIRouter(prefix="/ai", tags=["ai"])

# Config changes require an admin role.
AdminOnly = Depends(require_role(UserRole.org_admin, UserRole.super_admin))


@router.get("/configurations", response_model=list[AIConfigResponse])
async def get_configurations(db: TenantDB, _user: CurrentUser):
    return [AIConfigResponse.model_validate(c) for c in await service.get_configurations(db, tenant_id=_user.tenant_id)]


@router.put("/configurations/{agent_type}", response_model=AIConfigResponse)
async def update_configuration(
    agent_type: str,
    payload: AIConfigUpdateRequest,
    db: TenantDB,
    user: CurrentUser,
    _admin=AdminOnly,
):
    cfg = await service.update_configuration(
        db,
        tenant_id=user.tenant_id,
        agent_type=agent_type,
        is_enabled=payload.is_enabled,
        system_prompt=payload.system_prompt,
    )
    return AIConfigResponse.model_validate(cfg)


@router.post("/kill-switch", status_code=204)
async def kill_switch(
    payload: KillSwitchRequest, db: TenantDB, user: CurrentUser, _admin=AdminOnly
):
    await service.set_kill_switch(db, tenant_id=user.tenant_id, enabled=payload.enabled)
    from src.modules.audit import service as audit_service

    await audit_service.record(
        db,
        action="ai_kill_switch",
        tenant_id=user.tenant_id,
        user_id=user.id,
        details={"enabled": payload.enabled},
    )


@router.get("/runs", response_model=list[AIRunResponse])
async def list_runs(
    db: TenantDB,
    _user: CurrentUser,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    return [
        AIRunResponse.model_validate(r)
        for r in await service.list_runs(db, tenant_id=_user.tenant_id, limit=limit, offset=offset)
    ]


@router.get("/runs/{run_id}", response_model=AIRunDetailResponse)
async def get_run(run_id: uuid.UUID, db: TenantDB, _user: CurrentUser):
    run, calls = await service.get_run(db, run_id, tenant_id=_user.tenant_id)
    return AIRunDetailResponse(
        **AIRunResponse.model_validate(run).model_dump(),
        tool_calls=[AIToolCallResponse.model_validate(c) for c in calls],
    )
