"""Rate limiting middleware for Italian Tutor API.

Provides global and per-student rate limiting to prevent abuse and ensure
fair resource allocation across all users.
"""

import asyncio
import logging
import time

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Rate limit exceeded exception."""

    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Retry after {retry_after} seconds.",
                "retry_after": retry_after,
            },
        )


class RateLimitConfig:
    """Configuration for rate limiting.

    Defines limits for different endpoints and user categories.
    Format: (requests, window_seconds)
    """

    # Default limits (per-minute)
    DEFAULT_LIMIT = (1000, 60)

    # Per-endpoint limits (high-cost operations)
    ENDPOINT_LIMITS = {
        # LLM endpoints - expensive
        "/v1/chat/completions": (100, 60),  # 100 req/min
        "/chat": (100, 60),
        # Auth endpoints - brute force protection
        "/auth/token": (10, 60),  # 10 req/min
        "/auth/verify": (50, 60),
        # Student endpoints - moderate
        "/students": (50, 60),
        # Health checks - unrestricted
        "/health": (1000, 60),
        "/": (1000, 60),
    }

    # Per-student limits (concurrent usage protection)
    PER_STUDENT_LIMITS = {
        "/v1/chat/completions": (50, 3600),  # 50 req/hour per student
        "/chat": (50, 3600),
        "/students": (100, 3600),
    }


class RateLimitStore:
    """In-memory rate limit storage.

    Tracks request counts per endpoint and per student.
    Uses sliding window algorithm.
    """

    def __init__(self):
        # Format: {key: [(timestamp, count), ...]}
        self._store: dict[str, list] = {}
        self._lock = asyncio.Lock()

    async def check_limit(
        self,
        key: str,
        limit: int,
        window: int,
    ) -> tuple[bool, int]:
        """Check if key is under rate limit.

        Args:
            key: Rate limit key (endpoint, student_id, etc.)
            limit: Max requests in window
            window: Time window in seconds

        Returns:
            (is_allowed, retry_after) tuple
        """
        async with self._lock:
            now = time.time()
            window_start = now - window

            # Get existing entries
            if key not in self._store:
                self._store[key] = []

            # Remove old entries outside window
            self._store[key] = [(ts, cnt) for ts, cnt in self._store[key] if ts > window_start]

            # Count requests in window
            current_count = sum(cnt for ts, cnt in self._store[key])

            if current_count >= limit:
                # Calculate when we can retry
                oldest = min((ts for ts, _ in self._store[key]), default=now)
                retry_after = int(oldest + window - now) + 1
                return False, retry_after

            # Record this request
            self._store[key].append((now, 1))
            return True, 0

    async def cleanup_old_entries(self, max_age: int = 3600):
        """Remove entries older than max_age seconds."""
        async with self._lock:
            now = time.time()
            cutoff = now - max_age

            for key in list(self._store.keys()):
                self._store[key] = [(ts, cnt) for ts, cnt in self._store[key] if ts > cutoff]

                if not self._store[key]:
                    del self._store[key]

            logger.debug(f"Cleaned up rate limit store: {len(self._store)} keys remaining")


# Global rate limit store
_rate_limit_store = RateLimitStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting.

    Implements:
    1. Global per-endpoint rate limits
    2. Per-student rate limits
    """

    def __init__(self, app, config: RateLimitConfig | None = None):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.store = _rate_limit_store

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through rate limiting."""
        # Extract path and student_id
        path = request.url.path
        student_id = self._extract_student_id(request)

        logger.debug(f"Rate limit check: {path} (student: {student_id or 'unknown'})")

        # Check global endpoint limit
        endpoint_limit = self.config.ENDPOINT_LIMITS.get(path, self.config.DEFAULT_LIMIT)
        limit, window = endpoint_limit

        global_key = f"endpoint:{path}"
        allowed, retry_after = await self.store.check_limit(global_key, limit, window)

        if not allowed:
            logger.warning(
                f"Global rate limit exceeded for {path}: {limit} requests per {window}s"
            )
            raise RateLimitExceeded(retry_after)

        # Check per-student limit if student is identified
        if student_id and path in self.config.PER_STUDENT_LIMITS:
            student_limit, student_window = self.config.PER_STUDENT_LIMITS[path]
            student_key = f"student:{student_id}:{path}"

            allowed, retry_after = await self.store.check_limit(
                student_key, student_limit, student_window
            )

            if not allowed:
                logger.warning(
                    f"Per-student rate limit exceeded for {student_id} on {path}: "
                    f"{student_limit} requests per {student_window}s"
                )
                raise RateLimitExceeded(retry_after)

        # Proceed with request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Window"] = str(window)

        # Cleanup old entries periodically
        if int(time.time()) % 100 == 0:  # Every ~100th request
            asyncio.create_task(self.store.cleanup_old_entries())

        return response

    def _extract_student_id(self, request: Request) -> str | None:
        """Extract student_id from request.

        Tries multiple sources:
        1. JSON body (for POST requests)
        2. Query parameter
        3. Header X-Student-ID
        4. JWT token (sub claim)

        Returns:
            Student ID or None
        """
        try:
            # Try JSON body
            if hasattr(request.state, "_json"):
                json_data = request.state._json
                if isinstance(json_data, dict):
                    student_id = json_data.get("student_id") or json_data.get("messages", [{}])[
                        0
                    ].get("content", "")

                    if student_id and isinstance(student_id, str):
                        return student_id.split()[0]  # Get first word

            # Try query parameter
            if "student_id" in request.query_params:
                return request.query_params["student_id"]

            # Try header
            if "x-student-id" in request.headers:
                return request.headers["x-student-id"]

            # Try JWT token
            if "authorization" in request.headers:
                auth = request.headers["authorization"]
                if auth.startswith("Bearer "):
                    token = auth[7:]
                    from italianollama.api.middleware.auth import verify_access_token

                    try:
                        payload = verify_access_token(token)
                        return payload.get("sub")
                    except:
                        pass

        except Exception as e:
            logger.debug(f"Error extracting student_id: {e}")

        return None


def setup_rate_limiting(app, config: RateLimitConfig | None = None):
    """Register rate limiting middleware with FastAPI app."""
    app.add_middleware(RateLimitMiddleware, config=config)
    logger.info("Rate limiting middleware registered")
