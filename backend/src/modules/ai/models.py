"""AI ORM models: AIConfiguration, AIRun, AIToolCall.

Constitution IV: the AI never touches the DB directly — these tables record
configuration and an audit trail of every run and tool call.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import Base, TenantMixin, TimestampMixin, uuid_pk


class AgentType(str, enum.Enum):
    router = "router"
    support = "support"
    # Post-MVP:
    sales = "sales"
    billing = "billing"


MVP_AGENTS = {AgentType.router, AgentType.support}


class AIConfiguration(Base, TenantMixin, TimestampMixin):
    __tablename__ = "ai_configurations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "agent_type", name="uq_ai_config_tenant_agent"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    guardrails: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tools: Mapped[list | None] = mapped_column(JSONB, nullable=True)


class AIRun(Base, TenantMixin):
    __tablename__ = "ai_runs"

    id: Mapped[uuid.UUID] = uuid_pk()
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    escalated_to_human: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)


class AIToolCall(Base, TenantMixin):
    __tablename__ = "ai_tool_calls"

    id: Mapped[uuid.UUID] = uuid_pk()
    ai_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    input: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
