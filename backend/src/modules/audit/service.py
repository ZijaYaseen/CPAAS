"""Audit logging service — record critical actions for compliance/forensics."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.audit.models import AuditLog


async def record(
    db: AsyncSession,
    *,
    action: str,
    tenant_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Append an audit entry. Best-effort: never raises into the caller's flow."""
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
    )
    await db.flush()


async def list_logs(db: AsyncSession, *, limit: int = 100, offset: int = 0) -> list[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    return list((await db.scalars(stmt)).all())
