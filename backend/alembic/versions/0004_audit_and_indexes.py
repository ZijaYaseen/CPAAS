"""Audit logs + performance indexes

Revision ID: 0004_audit_and_indexes
Revises: 0003_ai_knowledge
Create Date: 2026-06-22
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_audit_and_indexes"
down_revision: str | None = "0003_ai_knowledge"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---- audit_logs ----
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("details", postgresql.JSONB, nullable=True),
        sa.Column("ip_address", postgresql.INET, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_audit_logs_tenant", "audit_logs", ["tenant_id"])
    op.create_index("idx_audit_logs_action", "audit_logs", ["action"])
    op.create_index("idx_audit_logs_created", "audit_logs", [sa.text("created_at DESC")])

    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON audit_logs "
        "USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)"
    )

    # ---- Composite performance indexes (hot query paths) ----
    # Inbox list: conversations by tenant + status ordered by recent activity.
    op.create_index(
        "idx_conversations_tenant_status_activity",
        "conversations",
        ["tenant_id", "status", sa.text("last_message_at DESC")],
    )
    # Message thread fetch: messages of a conversation in chronological order.
    op.create_index(
        "idx_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
    )
    # AI run audit listing per tenant.
    op.create_index(
        "idx_ai_runs_tenant_created",
        "ai_runs",
        ["tenant_id", sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("idx_ai_runs_tenant_created", table_name="ai_runs")
    op.drop_index("idx_messages_conversation_created", table_name="messages")
    op.drop_index("idx_conversations_tenant_status_activity", table_name="conversations")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON audit_logs")
    op.drop_table("audit_logs")
