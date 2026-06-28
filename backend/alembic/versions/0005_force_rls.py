"""Force RLS on all tenant-scoped tables so the table owner cannot bypass isolation.

PostgreSQL enables RLS policies but skips them for the table owner by default.
FORCE ROW LEVEL SECURITY makes policies apply even to the owner role, which is
required when the application connects as the same role that created the tables.

Revision ID: 0005_force_rls
Revises: 0004_audit_and_indexes
Create Date: 2026-06-28
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0005_force_rls"
down_revision: str | None = "0004_audit_and_indexes"
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
]


def upgrade() -> None:
    for table in _TENANT_SCOPED:
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")


def downgrade() -> None:
    for table in _TENANT_SCOPED:
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
