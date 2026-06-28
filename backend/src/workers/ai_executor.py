"""AI executor worker.

Triggered when an inbound customer message arrives. Runs the agent graph, persists
the run + tool-call audit trail, posts the AI reply (or an escalation note), and
publishes realtime events via the sync publisher. Outbound delivery is delegated to
the message worker.
"""

import uuid

from src.celery_app import celery_app
from src.core.database import set_tenant_context
from src.core.events import publish_event
from src.core.logging import get_logger
from src.modules.ai import service as ai_service
from src.workers.db import run_async

logger = get_logger("worker.ai")


@celery_app.task(
    name="src.workers.ai_executor.respond_to_message",
    bind=True,
    max_retries=2,
    default_retry_delay=10,
    acks_late=True,
)
def respond_to_message(self, tenant_id: str, conversation_id: str, prompt: str) -> str | None:
    async def _run(db):
        await set_tenant_context(db, tenant_id)
        if not await ai_service.is_ai_active(db, tenant_id=uuid.UUID(tenant_id)):
            return {"skipped": True}
        return await ai_service.run_ai(
            db,
            tenant_id=uuid.UUID(tenant_id),
            conversation_id=uuid.UUID(conversation_id),
            prompt=prompt,
        )

    try:
        result = run_async(_run)
    except Exception as exc:  # noqa: BLE001
        logger.warning("ai_executor_retry", error=str(exc))
        raise self.retry(exc=exc) from exc

    if result.get("skipped"):
        return None

    for event_type, data in result.get("events", []):
        publish_event(tenant_id, event_type, data)

    deliver_id = result.get("deliver_message_id")
    if deliver_id:
        celery_app.send_task(
            "src.workers.message_processor.deliver_outbound",
            args=[tenant_id, deliver_id],
            queue="messages",
        )
    return result.get("run_id")
