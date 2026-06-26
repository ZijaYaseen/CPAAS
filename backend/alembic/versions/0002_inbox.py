"""Inbox core: contacts, channel_accounts, conversations, messages, message_status + RLS

Revision ID: 0002_inbox
Revises: 0001_foundation
Create Date: 2026-06-22
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_inbox"
down_revision: str | None = "0001_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TENANT_SCOPED = ["contacts", "channel_accounts", "conversations", "messages", "message_status"]


def _enable_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {table} "
        f"USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)"
    )


def upgrade() -> None:
    # ---- contacts ----
    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("lifecycle_stage", sa.String(50), server_default="lead"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "email", name="uq_contacts_tenant_email"),
    )
    op.create_index("idx_contacts_tenant", "contacts", ["tenant_id"])
    op.create_index("idx_contacts_email", "contacts", ["email"])
    op.create_index("idx_contacts_phone", "contacts", ["phone"])
    op.create_index("idx_contacts_lifecycle", "contacts", ["lifecycle_stage"])

    # ---- channel_accounts ----
    op.create_table(
        "channel_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("credentials", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("configuration", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "channel_type", "name", name="uq_channel_tenant_type_name"),
    )
    op.create_index("idx_channel_accounts_tenant", "channel_accounts", ["tenant_id"])
    op.create_index("idx_channel_accounts_type", "channel_accounts", ["channel_type"])

    # ---- conversations ----
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_account_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("channel_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("assigned_to_user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_to_team_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_conversations_tenant", "conversations", ["tenant_id"])
    op.create_index("idx_conversations_contact", "conversations", ["contact_id"])
    op.create_index("idx_conversations_channel", "conversations", ["channel_account_id"])
    op.create_index("idx_conversations_assigned_user", "conversations", ["assigned_to_user_id"])
    op.create_index("idx_conversations_assigned_team", "conversations", ["assigned_to_team_id"])
    op.create_index("idx_conversations_status", "conversations", ["status"])
    op.create_index("idx_conversations_last_message", "conversations",
                    [sa.text("last_message_at DESC")])

    # ---- messages ----
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("sender_type", sa.String(50), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("media_urls", postgresql.JSONB, nullable=True),
        sa.Column("channel_metadata", postgresql.JSONB, nullable=True),
        sa.Column("is_internal_note", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_messages_tenant", "messages", ["tenant_id"])
    op.create_index("idx_messages_conversation", "messages", ["conversation_id"])
    op.create_index("idx_messages_created", "messages", [sa.text("created_at DESC")])
    op.create_index("idx_messages_sender", "messages", ["sender_id"])

    # ---- message_status ----
    op.create_table(
        "message_status",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("channel_metadata", postgresql.JSONB, nullable=True),
    )
    op.create_index("idx_message_status_message", "message_status", ["message_id"])
    op.create_index("idx_message_status_status", "message_status", ["status"])
    op.create_index("idx_message_status_timestamp", "message_status", [sa.text("timestamp DESC")])

    for table in _TENANT_SCOPED:
        _enable_rls(table)


def downgrade() -> None:
    for table in reversed(_TENANT_SCOPED):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
    op.drop_table("message_status")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("channel_accounts")
    op.drop_table("contacts")
