"""Unit tests for logging middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import logging
import json

from italianollama.api.middleware.logging import (
    LoggingMiddleware,
    StructuredLoggingMiddleware,
)


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_logging_middleware_basic(self):
        """Test basic logging middleware."""
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/health"
        mock_request.client.host = "127.0.0.1"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        
        async def mock_call_next(request):
            return mock_response
        
        with patch.object(middleware.logger, 'info') as mock_info:
            response = await middleware.dispatch(mock_request, mock_call_next)
            
            assert response.status_code == 200
            assert "X-Request-ID" in response.headers
            assert mock_info.called

    @pytest.mark.asyncio
    async def test_logging_middleware_exception(self):
        """Test logging middleware handles exceptions."""
        mock_app = MagicMock()
        middleware = LoggingMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"
        mock_request.client.host = "127.0.0.1"
        
        async def mock_call_next(request):
            raise ValueError("Test error")
        
        with patch.object(middleware.logger, 'error') as mock_error:
            with pytest.raises(ValueError):
                await middleware.dispatch(mock_request, mock_call_next)
            
            assert mock_error.called


class TestStructuredLoggingMiddleware:
    """Tests for StructuredLoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_structured_logging_basic(self):
        """Test basic structured logging."""
        mock_app = MagicMock()
        middleware = StructuredLoggingMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/health"
        mock_request.client.host = "127.0.0.1"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        
        async def mock_call_next(request):
            return mock_response
        
        with patch.object(middleware.logger, 'info') as mock_info:
            response = await middleware.dispatch(mock_request, mock_call_next)
            
            assert response.status_code == 200
            # Check that JSON was logged
            assert mock_info.called
            logged_data = mock_info.call_args[0][0]
            parsed = json.loads(logged_data)
            assert parsed["event"] == "http_response"
            assert parsed["path"] == "/health"

    @pytest.mark.asyncio
    async def test_structured_logging_error(self):
        """Test structured logging on errors."""
        mock_app = MagicMock()
        middleware = StructuredLoggingMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/test"
        mock_request.client = None
        
        async def mock_call_next(request):
            raise RuntimeError("Test error")
        
        with patch.object(middleware.logger, 'error') as mock_error:
            with pytest.raises(RuntimeError):
                await middleware.dispatch(mock_request, mock_call_next)
            
            assert mock_error.called
