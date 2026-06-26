"""Celery application (Redis broker + result backend).

Task modules under ``src.workers`` are auto-discovered. MVP workers: message
ingestion, webhook processing, AI execution, email sync. Queues are split per
worker type so they can scale independently.
"""

from celery import Celery

from src.core.config import settings


def _celery_redis_url(url: str) -> str:
    """Append ssl_cert_reqs=CERT_NONE to rediss:// URLs.

    Upstash (and other managed TLS Redis providers) use rediss:// but Celery
    requires the ssl_cert_reqs query param to be explicit — without it the
    worker crashes on startup before processing any tasks.
    """
    if url.startswith("rediss://") and "ssl_cert_reqs" not in url:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}ssl_cert_reqs=CERT_NONE"
    return url


_redis_url = _celery_redis_url(settings.redis_url)

celery_app = Celery(
    "ucaas",
    broker=_redis_url,
    backend=_redis_url,
    include=[
        "src.workers.message_processor",
        "src.workers.webhook_processor",
        "src.workers.email_sync",
        "src.workers.retry_handler",
        "src.workers.ai_executor",
        "src.workers.document_processor",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    task_routes={
        "src.workers.message_processor.*": {"queue": "messages"},
        "src.workers.webhook_processor.*": {"queue": "webhooks"},
        "src.workers.ai_executor.*": {"queue": "ai"},
        "src.workers.email_sync.*": {"queue": "email"},
    },
    beat_schedule={
        "email-imap-sync": {
            "task": "src.workers.email_sync.sync_inboxes",
            "schedule": 30.0,  # seconds
        },
    },
)
