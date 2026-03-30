"""Custom exceptions for backend communication."""


class BackendError(Exception):
    """Base exception for backend-related errors."""

    pass


class StudentNotFoundError(BackendError):
    """Student profile not found (404) on backend."""

    pass


class BackendConnectionError(BackendError):
    """Cannot connect to backend server."""

    pass


class StreamingError(BackendError):
    """Error during SSE stream processing."""

    pass
