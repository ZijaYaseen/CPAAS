"""Auth API routes: register, login, logout, current user.

Sessions are delivered as HttpOnly cookies. Register/login use an unscoped DB
session (no tenant context needed); /me and /logout use the authenticated user.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.modules.audit import service as audit_service
from src.modules.auth import service
from src.modules.auth.dependencies import CurrentUser
from src.modules.auth.models import Tenant
from src.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TenantResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        path="/",
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user, tenant = await service.register(
        db,
        organization_name=payload.organization_name,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    token = await service.create_session(
        db,
        user=user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    _set_session_cookie(response, token)
    await audit_service.record(
        db,
        action="user_registered",
        tenant_id=tenant.id,
        user_id=user.id,
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tenant=TenantResponse.model_validate(tenant),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await service.authenticate(db, email=payload.email, password=payload.password)
    token = await service.create_session(
        db,
        user=user,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    _set_session_cookie(response, token)
    await audit_service.record(
        db,
        action="user_login",
        tenant_id=user.tenant_id,
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    tenant = await db.scalar(select(Tenant).where(Tenant.id == user.tenant_id))
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tenant=TenantResponse.model_validate(tenant),
    )


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        await service.logout(db, token)
    response.delete_cookie(settings.session_cookie_name, path="/")


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser):
    return UserResponse.model_validate(user)
