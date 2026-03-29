"""Request timeout middleware for Italian Tutor API.

Ensures requests don't hang indefinitely by enforcing per-endpoint timeouts.
"""

import asyncio
import logging

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class RequestTimeoutError(HTTPException):
    """Request timeout exception."""

    def __init__(self, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            status_code=408,
            detail={
                "error": "request_timeout",
                "message": f"Request exceeded timeout of {timeout_seconds} seconds",
                "timeout": timeout_seconds,
            },
        )


class TimeoutConfig:
    """Configuration for request timeouts.

    Format: {endpoint: timeout_seconds}
    Default: 30 seconds for all endpoints
    """

    # Default timeout for all endpoints
    DEFAULT_TIMEOUT = 30

    # Per-endpoint timeouts (high-cost operations need more time)
    ENDPOINT_TIMEOUTS = {
        # LLM endpoints - expensive, can take longer
        "/v1/chat/completions": 300,  # 5 minutes
        "/chat": 300,
        # Auth endpoints - should be fast
        "/auth/token": 10,
        "/auth/verify": 10,
        # Student endpoints - moderate
        "/students": 30,
        # Health checks - fast
        "/health": 5,
        "/": 5,
    }


class TimeoutMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for request timeouts.

    Enforces per-endpoint timeout limits to prevent hanging requests.
    """

    def __init__(self, app, config: TimeoutConfig | None = None):
        super().__init__(app)
        self.config = config or TimeoutConfig()

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with timeout enforcement."""
        path = request.url.path

        # Get timeout for this endpoint
        timeout = self.config.ENDPOINT_TIMEOUTS.get(path, self.config.DEFAULT_TIMEOUT)

        logger.debug(f"Request timeout: {path} = {timeout}s")

        try:
            # Wrap call_next in timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout,
            )
            return response

        except asyncio.TimeoutError:
            logger.warning(f"Request timeout on {path} after {timeout}s")

            # Return 408 timeout response
            return JSONResponse(
                status_code=408,
                content={
                    "error": "request_timeout",
                    "message": f"Request exceeded timeout of {timeout} seconds",
                    "timeout": timeout,
                    "path": path,
                },
                headers={
                    "X-Request-Timeout": str(timeout),
                },
            )

        except Exception as e:
            logger.error(f"Timeout middleware error on {path}: {e}")
            raise


def setup_request_timeout(app, config: TimeoutConfig | None = None):
    """Register request timeout middleware with FastAPI app."""
    app.add_middleware(TimeoutMiddleware, config=config)
    logger.info("Request timeout middleware registered")
