"""Application error taxonomy.

A small hierarchy of typed exceptions mapped to HTTP status codes by the global
error handler. Keeps business logic free of HTTP concerns.
"""


class AppError(Exception):
    """Base application error."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str | None = None, *, code: str | None = None):
        self.message = message or self.__class__.__name__
        if code:
            self.code = code
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class AuthenticationError(AppError):
    status_code = 401
    code = "unauthenticated"


class AuthorizationError(AppError):
    status_code = 403
    code = "forbidden"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class RateLimitError(AppError):
    status_code = 429
    code = "rate_limited"
