"""AI + knowledge base: ai_configurations, ai_runs, ai_tool_calls, knowledge_* + pgvector

Revision ID: 0003_ai_knowledge
Revises: 0002_inbox
Create Date: 2026-06-22
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0003_ai_knowledge"
down_revision: str | None = "0002_inbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TENANT_SCOPED = [
    "ai_configurations",
    "ai_runs",
    "ai_tool_calls",
    "knowledge_documents",
    "knowledge_chunks",
]


def _enable_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {table} "
        f"USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)"
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ---- ai_configurations ----
    op.create_table(
        "ai_configurations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_type", sa.String(50), nullable=False),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("system_prompt", sa.Text, nullable=True),
        sa.Column("guardrails", postgresql.JSONB, nullable=True),
        sa.Column("tools", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "agent_type", name="uq_ai_config_tenant_agent"),
    )
    op.create_index("idx_ai_configurations_tenant", "ai_configurations", ["tenant_id"])

    # ---- ai_runs ----
    op.create_table(
        "ai_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_type", sa.String(50), nullable=False),
        sa.Column("prompt", sa.Text, nullable=False),
        sa.Column("response", sa.Text, nullable=True),
        sa.Column("escalated_to_human", sa.Boolean, server_default=sa.false()),
        sa.Column("escalation_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
    )
    op.create_index("idx_ai_runs_tenant", "ai_runs", ["tenant_id"])
    op.create_index("idx_ai_runs_conversation", "ai_runs", ["conversation_id"])
    op.create_index("idx_ai_runs_created", "ai_runs", [sa.text("created_at DESC")])

    # ---- ai_tool_calls ----
    op.create_table(
        "ai_tool_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ai_run_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("ai_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("input", postgresql.JSONB, nullable=False),
        sa.Column("output", postgresql.JSONB, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_ai_tool_calls_run", "ai_tool_calls", ["ai_run_id"])
    op.create_index("idx_ai_tool_calls_tool", "ai_tool_calls", ["tool_name"])

    # ---- knowledge_documents ----
    op.create_table(
        "knowledge_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_knowledge_documents_tenant", "knowledge_documents", ["tenant_id"])
    op.create_index("idx_knowledge_documents_active", "knowledge_documents", ["is_active"])

    # ---- knowledge_chunks ----
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_chunk_doc_index"),
    )
    op.create_index("idx_knowledge_chunks_document", "knowledge_chunks", ["document_id"])
    op.execute(
        "CREATE INDEX idx_knowledge_chunks_embedding ON knowledge_chunks "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )

    for table in _TENANT_SCOPED:
        _enable_rls(table)


def downgrade() -> None:
    for table in reversed(_TENANT_SCOPED):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_documents")
    op.drop_table("ai_tool_calls")
    op.drop_table("ai_runs")
    op.drop_table("ai_configurations")
