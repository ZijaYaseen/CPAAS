"""Message worker: outbound delivery + inbound ingestion (Celery).

Flow (constitution III): API persists message + emits created event → enqueues
``deliver_outbound`` → worker calls the channel adapter → records status →
publishes ``message_updated`` via the sync Redis publisher.
"""

import uuid

from src.celery_app import celery_app
from src.core.events import publish_event
from src.core.logging import get_logger
from src.modules.channels import service as channel_service
from src.workers.db import run_async

logger = get_logger("worker.message")


@celery_app.task(
    name="src.workers.message_processor.deliver_outbound",
    bind=True,
    max_retries=5,
    default_retry_delay=10,
    acks_late=True,
)
def deliver_outbound(self, tenant_id: str, message_id: str) -> str:
    """Deliver one outbound message via its channel adapter."""
    try:
        status = run_async(
            lambda db: channel_service.deliver_message(
                db, tenant_id=uuid.UUID(tenant_id), message_id=uuid.UUID(message_id)
            )
        )
        publish_event(
            tenant_id, "message_updated", {"message_id": message_id, "status": status.value}
        )
        return status.value
    except Exception as exc:  # noqa: BLE001
        logger.warning("deliver_retry", message_id=message_id, error=str(exc))
        raise self.retry(exc=exc) from exc


@celery_app.task(
    name="src.workers.message_processor.ingest_inbound_payload",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    acks_late=True,
)
def ingest_inbound_payload(self, channel_type: str, payload: dict) -> int:
    """Parse + ingest a provider payload asynchronously (used by the webhook worker)."""
    try:
        count = run_async(
            lambda db: channel_service.process_inbound(
                db, channel_type=channel_type, payload=payload
            )
        )
        return count
    except Exception as exc:  # noqa: BLE001
        logger.warning("ingest_retry", channel_type=channel_type, error=str(exc))
        raise self.retry(exc=exc) from exc
