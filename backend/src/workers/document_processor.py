"""Document processing worker: chunk + embed uploaded knowledge documents."""

import uuid

from src.celery_app import celery_app
from src.core.database import set_tenant_context
from src.core.events import publish_event
from src.core.logging import get_logger
from src.modules.knowledge import service as knowledge_service
from src.workers.db import run_async

logger = get_logger("worker.document")


@celery_app.task(
    name="src.workers.document_processor.process",
    bind=True,
    max_retries=3,
    default_retry_delay=15,
    acks_late=True,
)
def process(self, tenant_id: str, document_id: str) -> int:
    async def _run(db):
        await set_tenant_context(db, tenant_id)
        return await knowledge_service.process_document(db, document_id=uuid.UUID(document_id))

    try:
        count = run_async(_run)
        logger.info("document_processed", document_id=document_id, chunks=count)
        publish_event(tenant_id, "document_updated", {"document_id": document_id, "status": "ready"})
        return count
    except Exception as exc:  # noqa: BLE001
        publish_event(tenant_id, "document_updated", {"document_id": document_id, "status": "error"})
        raise self.retry(exc=exc) from exc
