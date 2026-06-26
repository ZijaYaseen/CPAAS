"""Webhook worker.

Inbound webhooks are processed inline in the API for low latency, but this task
provides the async/queued path (used for replay or heavy payloads) by delegating
to the message processor's ingestion task.
"""

from src.celery_app import celery_app
from src.core.logging import get_logger
from src.modules.channels import service as channel_service
from src.workers.db import run_async

logger = get_logger("worker.webhook")


@celery_app.task(name="src.workers.webhook_processor.process_webhook", acks_late=True)
def process_webhook(channel_type: str, payload: dict) -> int:
    count = run_async(
        lambda db: channel_service.process_inbound(db, channel_type=channel_type, payload=payload)
    )
    logger.info("webhook_processed", channel_type=channel_type, count=count)
    return count
