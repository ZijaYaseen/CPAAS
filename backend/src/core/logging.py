"""Structured JSON logging with correlation IDs.

A correlation id is generated per request (or taken from the inbound
``X-Correlation-ID`` header) and bound to the structlog context so every log
line emitted while handling that request is traceable.
"""

import logging
from contextvars import ContextVar

import structlog

from src.core.config import settings

correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def _add_correlation_id(_logger, _method, event_dict):
    cid = correlation_id_ctx.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def configure_logging() -> None:
    renderer = (
        structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _add_correlation_id,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.debug else logging.INFO
        ),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None):
    return structlog.get_logger(name)
