"""Sentry error tracking (config-gated, optional).

Initialized only when SENTRY_DSN is set. Import is guarded so the app runs even
if sentry-sdk isn't installed.
"""

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger("sentry")


def init_sentry() -> None:
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
    except ImportError:
        logger.warning("sentry_sdk_not_installed")
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
    logger.info("sentry_initialized")
