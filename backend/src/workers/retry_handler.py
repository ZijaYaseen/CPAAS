"""Shared retry / dead-letter helpers for workers.

Tasks use Celery's built-in ``self.retry`` with exponential backoff. Permanently
failed tasks are pushed to a Redis dead-letter list for inspection/replay.
"""

import json

from src.celery_app import celery_app
from src.core.events import _sync_redis
from src.core.logging import get_logger

logger = get_logger("worker.retry")

DEAD_LETTER_KEY = "dead_letter:tasks"


@celery_app.task(name="src.workers.retry_handler.record_dead_letter")
def record_dead_letter(task_name: str, args: list, error: str) -> None:
    """Persist a permanently-failed task for later inspection/replay."""
    _sync_redis.lpush(
        DEAD_LETTER_KEY, json.dumps({"task": task_name, "args": args, "error": error})
    )
    logger.error("dead_letter", task=task_name, error=error)
