"""Context middleware for request enrichment.

Injects request-scoped context (request_id, student_id, trace info) into request.state
for logging, metrics, and authorization checks.
"""

import logging
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ContextMiddleware(BaseHTTPMiddleware):
    """Inject context into request state.

    Adds:
    - request_id: Unique identifier for request tracing
    - student_id: Extracted from Authorization header or URL
    - trace_id: For distributed tracing
    - start_time: For performance tracking
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and inject context."""
        # Generate request ID
        request_id = (
            request.headers.get("X-Request-ID")
            or request.headers.get("X-Trace-ID")
            or str(uuid4())
        )
        request.state.request_id = request_id

        # Extract student_id from Authorization header (JWT subject) or URL
        student_id = None

        # Try to parse Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from italianollama.api.middleware.auth import decode_jwt_payload

                token = auth_header[7:]
                payload = decode_jwt_payload(token)
                student_id = payload.get("sub")
            except Exception:
                pass  # Silent fail, student_id remains None

        # Fall back to URL path (for /students/{student_id})
        if not student_id:
            path_parts = request.url.path.split("/")
            if len(path_parts) > 2:
                if path_parts[1] == "students" and len(path_parts) > 2:
                    student_id = path_parts[2]
                elif path_parts[1] == "analytics" and len(path_parts) > 3:
                    student_id = path_parts[3]

        request.state.student_id = student_id

        # Log context
        logger.debug(
            f"Context | request_id={request_id} | "
            f"student_id={student_id or 'anonymous'} | "
            f"method={request.method} | path={request.url.path}"
        )

        # Process request
        response = await call_next(request)

        # Add context headers to response
        response.headers["X-Request-ID"] = request_id
        if student_id:
            response.headers["X-Student-ID"] = student_id

        return response


def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification (for context extraction).

    Note: This is for context extraction only. Full verification happens in auth routes.
    """
    import base64
    import json

    try:
        # JWT format: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            return {}

        # Decode payload (add padding if needed)
        payload_b64 = parts[1]
        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += "=" * padding

        payload_json = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_json)
    except Exception as e:
        logger.debug(f"Could not decode JWT payload: {e}")
        return {}
