"""HTTP middleware: correlation IDs and global error handling.

Tenant context is applied per-request via the auth dependency (which has access
to the authenticated session) rather than middleware, so unauthenticated routes
(auth, webhooks) are unaffected. See modules/auth/dependencies.py.
"""

import uuid
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import AppError
from src.core.logging import correlation_id_ctx, get_logger

logger = get_logger("http")

_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def register_csrf(app: FastAPI) -> None:
    """Origin-based CSRF protection for authenticated, cookie-bearing requests.

    CSRF only matters when the browser auto-attaches the session cookie, so we
    enforce an Origin/Referer match ONLY when a session cookie is present and the
    method is state-changing. Public (no-cookie) endpoints like webhooks and the
    web chat widget are unaffected.
    """
    if not settings.csrf_protection_enabled:
        return

    allowed_host = urlparse(settings.frontend_origin).netloc

    @app.middleware("http")
    async def csrf_middleware(request: Request, call_next):
        if request.method in _MUTATING_METHODS and request.cookies.get(
            settings.session_cookie_name
        ):
            origin = request.headers.get("origin") or request.headers.get("referer")
            origin_host = urlparse(origin).netloc if origin else ""
            if origin_host != allowed_host:
                return JSONResponse(
                    status_code=403,
                    content={"error": {"code": "csrf_failed", "message": "Origin not allowed"}},
                )
        return await call_next(request)


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next):
        cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        token = correlation_id_ctx.set(cid)
        try:
            response = await call_next(request)
        finally:
            correlation_id_ctx.reset(token)
        response.headers["X-Correlation-ID"] = cid
        return response


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError):
        if exc.status_code >= 500:
            logger.error("app_error", code=exc.code, message=exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception):
        logger.error("unhandled_error", error=str(exc), exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Internal server error"}},
        )
