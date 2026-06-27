"""AI services: configuration management + run orchestration with full audit logging.

Orchestration runs inside the AI executor worker (sync Celery task → asyncio.run),
so this module performs DB writes WITHOUT emitting realtime events directly; it
returns the events for the worker to publish via the sync publisher. Constitution
IV: the AI only acts through the read-only tools in ``tools.py`` and every run +
tool call is recorded.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.core.logging import get_logger
from src.modules.ai import guardrails
from src.modules.ai.agents.escalation import should_escalate
from src.modules.ai.agents.handoffs import build_agent_graph
from src.modules.ai.context import ToolContext, current_tool_context
from src.modules.ai.models import MVP_AGENTS, AgentType, AIConfiguration, AIRun, AIToolCall
from src.modules.inbox.models import Conversation, Message, MessageDirection, SenderType
from src.modules.knowledge import service as knowledge_service

logger = get_logger("ai")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


async def get_configurations(db: AsyncSession) -> list[AIConfiguration]:
    return list((await db.scalars(select(AIConfiguration))).all())


async def update_configuration(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    agent_type: str,
    is_enabled: bool | None = None,
    system_prompt: str | None = None,
) -> AIConfiguration:
    if AgentType(agent_type) not in MVP_AGENTS:
        raise NotFoundError(f"Agent '{agent_type}' is not available in the MVP")
    cfg = await db.scalar(select(AIConfiguration).where(AIConfiguration.agent_type == agent_type))
    if cfg is None:
        cfg = AIConfiguration(tenant_id=tenant_id, agent_type=agent_type)
        db.add(cfg)
    if is_enabled is not None:
        cfg.is_enabled = is_enabled
    if system_prompt is not None:
        cfg.system_prompt = system_prompt
    await db.flush()
    return cfg


async def set_kill_switch(db: AsyncSession, *, tenant_id: uuid.UUID, enabled: bool) -> None:
    """Kill-switch: enable/disable ALL agents for the tenant instantly."""
    for agent in MVP_AGENTS:
        await update_configuration(
            db, tenant_id=tenant_id, agent_type=agent.value, is_enabled=enabled
        )


async def is_ai_active(db: AsyncSession) -> bool:
    """AI is active unless the router has been explicitly disabled (default-on)."""
    router_cfg = await db.scalar(
        select(AIConfiguration).where(AIConfiguration.agent_type == AgentType.router.value)
    )
    return router_cfg.is_enabled if router_cfg is not None else True


async def _config_map(db: AsyncSession) -> dict[str, dict]:
    configs = await get_configurations(db)
    return {c.agent_type: {"system_prompt": c.system_prompt} for c in configs if c.is_enabled}


# ---------------------------------------------------------------------------
# Run orchestration (called by the executor worker)
# ---------------------------------------------------------------------------


async def run_ai(
    db: AsyncSession, *, tenant_id: uuid.UUID, conversation_id: uuid.UUID, prompt: str
) -> dict:
    """Execute the agent graph for one inbound message. Returns a result dict with
    the events the worker should publish and an optional message id to deliver."""
    from agents import Runner  # imported lazily (heavy SDK)

    run = AIRun(
        tenant_id=tenant_id,
        conversation_id=conversation_id,
        agent_type=AgentType.router.value,
        prompt=prompt,
    )
    db.add(run)
    await db.flush()

    escalated = False
    reason: str | None = None
    response: str | None = None

    ok_in, reason_in = guardrails.check_input(prompt)
    if not ok_in:
        escalated, reason = True, reason_in
    else:
        # Pre-fetch KB context and inject into prompt — avoids tool calls entirely
        try:
            kb_results = await knowledge_service.search(db, query=prompt, top_k=5)
            kb_context = "\n\n---\n\n".join(r["content"] for r in kb_results) if kb_results else ""
        except Exception:  # noqa: BLE001
            kb_context = ""

        ctx = ToolContext(tenant_id=str(tenant_id), session=db)
        token = current_tool_context.set(ctx)
        try:
            result = await Runner.run(
                build_agent_graph(await _config_map(db), kb_context=kb_context),
                input=prompt,
            )
            response = (result.final_output or "").strip() or None
        except Exception as exc:  # noqa: BLE001 — never crash on model/tool failure
            logger.warning("ai_run_failed", error=str(exc))
            escalated, reason = True, "AI run error"
        finally:
            current_tool_context.reset(token)

        # Persist tool-call audit trail.
        for call in ctx.tool_calls:
            db.add(
                AIToolCall(
                    tenant_id=tenant_id,
                    ai_run_id=run.id,
                    tool_name=call["tool_name"],
                    input=call.get("input", {}),
                    output=call.get("output"),
                )
            )

        if not escalated:
            ok_out, reason_out = guardrails.check_output(response or "")
            if not ok_out:
                escalated, reason = True, reason_out
            elif should_escalate(response):
                escalated, reason = True, "Low confidence / handoff requested"

    run.response = response
    run.escalated_to_human = escalated
    run.escalation_reason = reason
    run.completed_at = datetime.now(UTC)

    conv = await db.scalar(select(Conversation).where(Conversation.id == conversation_id))
    events: list[tuple[str, dict]] = []
    deliver_message_id: str | None = None

    if escalated:
        note = Message(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            direction=MessageDirection.outbound.value,
            sender_type=SenderType.ai_agent.value,
            content=f"🤖 AI escalated to a human agent. Reason: {reason or 'uncertain'}",
            is_internal_note=True,
        )
        db.add(note)
        await db.flush()
        events.append(
            (
                "message_created",
                {
                    "conversation_id": str(conversation_id),
                    "message_id": str(note.id),
                    "internal_note": True,
                },
            )
        )
    elif response:
        ai_msg = Message(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            direction=MessageDirection.outbound.value,
            sender_type=SenderType.ai_agent.value,
            sender_id=run.id,
            content=response,
        )
        db.add(ai_msg)
        if conv is not None:
            conv.last_message_at = datetime.now(UTC)
        await db.flush()
        deliver_message_id = str(ai_msg.id)
        events.append(
            (
                "message_created",
                {
                    "conversation_id": str(conversation_id),
                    "message_id": str(ai_msg.id),
                    "direction": "outbound",
                },
            )
        )

    return {
        "run_id": str(run.id),
        "escalated": escalated,
        "response": response,
        "events": events,
        "deliver_message_id": deliver_message_id,
    }


# ---------------------------------------------------------------------------
# Run audit queries
# ---------------------------------------------------------------------------


async def list_runs(db: AsyncSession, *, limit: int = 50, offset: int = 0) -> list[AIRun]:
    stmt = select(AIRun).order_by(AIRun.created_at.desc()).limit(limit).offset(offset)
    return list((await db.scalars(stmt)).all())


async def get_run(db: AsyncSession, run_id: uuid.UUID) -> tuple[AIRun, list[AIToolCall]]:
    run = await db.scalar(select(AIRun).where(AIRun.id == run_id))
    if run is None:
        raise NotFoundError("AI run not found")
    calls = list((await db.scalars(select(AIToolCall).where(AIToolCall.ai_run_id == run_id))).all())
    return run, calls
