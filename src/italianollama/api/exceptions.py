"""Custom exceptions for Italian Tutor API."""

from uuid import uuid4

from fastapi import HTTPException


class TutorException(HTTPException):
    """Base exception for Italian Tutor API.

    All exceptions include a trace_id for debugging.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str | None = None,
        trace_id: str | None = None,
    ):
        self.trace_id = trace_id or str(uuid4())
        self.error_type = error_type or self.__class__.__name__

        # Format detail with trace_id for logging
        detail_with_trace = {
            "error": self.error_type,
            "message": detail,
            "trace_id": self.trace_id,
        }

        super().__init__(status_code=status_code, detail=detail_with_trace)


class ValidationError(TutorException):
    """400 Bad Request - Invalid input data."""

    def __init__(self, detail: str, trace_id: str | None = None):
        super().__init__(
            status_code=400,
            detail=detail,
            error_type="validation_error",
            trace_id=trace_id,
        )


class AuthenticationError(TutorException):
    """401 Unauthorized - Missing or invalid credentials."""

    def __init__(
        self, detail: str = "Invalid or missing credentials", trace_id: str | None = None
    ):
        super().__init__(
            status_code=401,
            detail=detail,
            error_type="authentication_error",
            trace_id=trace_id,
        )


class AuthorizationError(TutorException):
    """403 Forbidden - User lacks permission."""

    def __init__(self, detail: str = "Insufficient permissions", trace_id: str | None = None):
        super().__init__(
            status_code=403,
            detail=detail,
            error_type="authorization_error",
            trace_id=trace_id,
        )


class NotFoundError(TutorException):
    """404 Not Found - Resource doesn't exist."""

    def __init__(self, resource: str, detail: str | None = None, trace_id: str | None = None):
        if detail is None:
            detail = f"{resource} not found"
        super().__init__(
            status_code=404,
            detail=detail,
            error_type="not_found_error",
            trace_id=trace_id,
        )


class ConflictError(TutorException):
    """409 Conflict - Resource already exists."""

    def __init__(self, detail: str, trace_id: str | None = None):
        super().__init__(
            status_code=409,
            detail=detail,
            error_type="conflict_error",
            trace_id=trace_id,
        )


class RateLimitError(TutorException):
    """429 Too Many Requests - Rate limit exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded", trace_id: str | None = None):
        super().__init__(
            status_code=429,
            detail=detail,
            error_type="rate_limit_error",
            trace_id=trace_id,
        )


class ServiceUnavailableError(TutorException):
    """503 Service Unavailable - External service down."""

    def __init__(self, service: str, detail: str | None = None, trace_id: str | None = None):
        if detail is None:
            detail = f"{service} is temporarily unavailable"
        super().__init__(
            status_code=503,
            detail=detail,
            error_type="service_unavailable_error",
            trace_id=trace_id,
        )


class InternalServerError(TutorException):
    """500 Internal Server Error - Unexpected error."""

    def __init__(self, detail: str, trace_id: str | None = None):
        super().__init__(
            status_code=500,
            detail=detail,
            error_type="internal_server_error",
            trace_id=trace_id,
        )
