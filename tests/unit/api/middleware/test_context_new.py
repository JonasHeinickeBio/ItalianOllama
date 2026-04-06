"""Unit tests for context middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import base64

from italianollama.api.middleware.context import (
    ContextMiddleware,
    decode_jwt_payload,
)


class TestDecodeJWTPayload:
    """Tests for decode_jwt_payload function."""

    def test_decode_jwt_payload_basic(self):
        """Test basic JWT payload decoding."""
        # Create a minimal JWT (header.payload.signature)
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip('=')
        payload = base64.urlsafe_b64encode(b'{"sub":"student123"}').decode().rstrip('=')
        signature = base64.urlsafe_b64encode(b'signature').decode().rstrip('=')
        
        token = f"{header}.{payload}.{signature}"
        
        result = decode_jwt_payload(token)
        
        assert result.get("sub") == "student123"

    def test_decode_jwt_payload_invalid(self):
        """Test invalid JWT returns empty dict."""
        result = decode_jwt_payload("invalid-token")
        assert result == {}

    def test_decode_jwt_payload_empty(self):
        """Test empty string returns empty dict."""
        result = decode_jwt_payload("")
        assert result == {}


class TestContextMiddleware:
    """Tests for ContextMiddleware."""

    @pytest.mark.asyncio
    async def test_context_middleware_basic(self):
        """Test basic context middleware."""
        mock_app = MagicMock()
        middleware = ContextMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.url.path = "/health"
        mock_request.method = "GET"
        mock_request.cookies = {}
        
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert hasattr(mock_request.state, "request_id")
        assert hasattr(mock_request.state, "student_id")
        assert hasattr(mock_request.state, "session_id")
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_context_middleware_with_existing_request_id(self):
        """Test uses existing X-Request-ID header."""
        mock_app = MagicMock()
        middleware = ContextMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.headers = {"X-Request-ID": "existing-request-id"}
        mock_request.url.path = "/health"
        mock_request.method = "GET"
        mock_request.cookies = {}
        
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Should use existing request ID
        assert mock_request.state.request_id == "existing-request-id"

    @pytest.mark.asyncio
    async def test_context_middleware_extracts_student_from_path(self):
        """Test extracts student_id from URL path."""
        mock_app = MagicMock()
        middleware = ContextMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.url.path = "/students/test-student-123"
        mock_request.method = "GET"
        mock_request.cookies = {}
        
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert mock_request.state.student_id == "test-student-123"

    @pytest.mark.asyncio
    async def test_context_middleware_extracts_student_from_analytics(self):
        """Test extracts student_id from analytics path."""
        mock_app = MagicMock()
        middleware = ContextMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.url.path = "/analytics/velocity/student-456"
        mock_request.method = "GET"
        mock_request.cookies = {}
        
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert mock_request.state.student_id == "student-456"

    @pytest.mark.asyncio
    async def test_context_middleware_uses_existing_session(self):
        """Test uses existing session cookie."""
        mock_app = MagicMock()
        middleware = ContextMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.url.path = "/health"
        mock_request.method = "GET"
        mock_request.cookies = {"session_id": "existing-session-id"}
        
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert mock_request.state.session_id == "existing-session-id"

    @pytest.mark.asyncio
    async def test_context_middleware_adds_student_header(self):
        """Test adds student ID to response headers."""
        mock_app = MagicMock()
        middleware = ContextMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.url.path = "/students/student-789"
        mock_request.method = "GET"
        mock_request.cookies = {}
        
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert "X-Student-ID" in response.headers
        assert response.headers["X-Student-ID"] == "student-789"
