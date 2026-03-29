"""Logging middleware for request/response tracking."""

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Add request ID and log all requests with timing.

    Adds X-Request-ID header to response for tracing.
    Logs: method, path, status, duration, request_id
    """

    def __init__(self, app, logger_name: str = "italian_tutor"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid4())

        # Store in state for access in route handlers
        request.state.request_id = request_id

        start_time = time.time()

        # Log incoming request
        self.logger.info(
            f"REQUEST | {request.method} {request.url.path} | "
            f"request_id={request_id} | "
            f"client={request.client.host if request.client else 'unknown'}"
        )

        try:
            # Call the endpoint
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log outgoing response
            self.logger.info(
                f"RESPONSE | {request.method} {request.url.path} | "
                f"status={response.status_code} | "
                f"duration={duration_ms:.1f}ms | "
                f"request_id={request_id}"
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            self.logger.error(
                f"ERROR | {request.method} {request.url.path} | "
                f"duration={duration_ms:.1f}ms | "
                f"error={type(e).__name__}: {str(e)} | "
                f"request_id={request_id}",
                exc_info=True,
            )

            raise


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """JSON-structured logging for production.

    Outputs JSON logs for easy parsing and log aggregation.
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("italian_tutor.structured")

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log as JSON."""
        import json

        request_id = str(uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            log_entry = {
                "event": "http_response",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 1),
                "client_ip": request.client.host if request.client else None,
            }

            self.logger.info(json.dumps(log_entry))
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_entry = {
                "event": "http_error",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "duration_ms": round(duration_ms, 1),
            }

            self.logger.error(json.dumps(log_entry), exc_info=True)
            raise
