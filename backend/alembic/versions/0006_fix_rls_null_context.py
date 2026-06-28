"""Fix RLS policies to allow NULL tenant context for webhook/worker cross-tenant lookups.

With FORCE ROW LEVEL SECURITY, unauthenticated sessions (webhooks, workers) that have
no tenant context set get no rows visible, breaking inbound webhook routing
(_resolve_account) and AI worker queries.

Fix: extend the USING clause to pass through when no tenant context is set
(IS NULL). Authenticated API requests always set the context via set_tenant_context,
so they remain fully restricted. Unauthenticated paths (webhooks) still get all rows,
but those paths are protected by signature verification and explicit routing logic.

Revision ID: 0006_fix_rls_null_context
Revises: 0005_force_rls
Create Date: 2026-06-28
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0006_fix_rls_null_context"
down_revision: str | None = "0005_force_rls"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TENANT_SCOPED = [
    "users",
    "roles",
    "teams",
    "contacts",
    "channel_accounts",
    "conversations",
    "messages",
    "message_status",
    "audit_logs",
]


def upgrade() -> None:
    for table in _TENANT_SCOPED:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} "
            f"USING ("
            f"  current_setting('app.current_tenant_id', true) IS NULL"
            f"  OR tenant_id = current_setting('app.current_tenant_id', true)::uuid"
            f")"
        )


def downgrade() -> None:
    for table in _TENANT_SCOPED:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} "
            f"USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)"
        )
