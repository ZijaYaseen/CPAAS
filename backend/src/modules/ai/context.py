"""Per-run tool execution context.

The OpenAI Agents SDK invokes tool functions during a run; they need access to the
tenant-scoped DB session and a place to record tool calls for the audit log. We
expose this via a contextvar set by the AI executor before ``Runner.run``.
"""

from contextvars import ContextVar
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ToolContext:
    tenant_id: str
    session: AsyncSession
    tool_calls: list[dict] = field(default_factory=list)


current_tool_context: ContextVar[ToolContext | None] = ContextVar(
    "current_tool_context", default=None
)


def get_tool_context() -> ToolContext:
    ctx = current_tool_context.get()
    if ctx is None:
        raise RuntimeError("Tool invoked outside of an AI run context")
    return ctx
