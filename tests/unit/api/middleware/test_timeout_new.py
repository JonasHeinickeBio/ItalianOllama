"""Unit tests for timeout middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from italianollama.api.middleware.timeout import (
    RequestTimeoutError,
    TimeoutConfig,
    TimeoutMiddleware,
    setup_request_timeout,
)


class TestRequestTimeoutError:
    """Tests for RequestTimeoutError exception."""

    def test_request_timeout_error_defaults(self):
        """Test RequestTimeoutError with defaults."""
        exc = RequestTimeoutError(30)
        assert exc.status_code == 408
        assert exc.timeout_seconds == 30
        assert "timeout" in exc.detail["message"]

    def test_request_timeout_error_custom(self):
        """Test RequestTimeoutError with custom timeout."""
        exc = RequestTimeoutError(60)
        assert exc.timeout_seconds == 60
        assert "60" in exc.detail["message"]


class TestTimeoutConfig:
    """Tests for TimeoutConfig class."""

    def test_timeout_config_defaults(self):
        """Test TimeoutConfig default timeout."""
        config = TimeoutConfig()
        assert config.DEFAULT_TIMEOUT == 30

    def test_timeout_config_endpoint_timeouts(self):
        """Test TimeoutConfig endpoint timeouts."""
        config = TimeoutConfig()
        
        # Check LLM endpoints
        assert "/v1/chat/completions" in config.ENDPOINT_TIMEOUTS
        assert config.ENDPOINT_TIMEOUTS["/v1/chat/completions"] == 300
        
        # Check auth endpoints
        assert "/auth/token" in config.ENDPOINT_TIMEOUTS
        assert config.ENDPOINT_TIMEOUTS["/auth/token"] == 10
        
        # Check health endpoint
        assert "/health" in config.ENDPOINT_TIMEOUTS
        assert config.ENDPOINT_TIMEOUTS["/health"] == 5


class TestTimeoutMiddleware:
    """Tests for TimeoutMiddleware class."""

    @pytest.mark.asyncio
    async def test_middleware_allows_request(self):
        """Test middleware allows normal request."""
        mock_app = MagicMock()
        config = TimeoutConfig()
        middleware = TimeoutMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        
        mock_response = MagicMock()
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_middleware_timeout_on_slow_request(self):
        """Test middleware times out slow requests."""
        mock_app = MagicMock()
        config = TimeoutConfig()
        middleware = TimeoutMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        
        async def slow_call_next(request):
            await asyncio.sleep(10)  # Longer than 5s timeout
            return MagicMock()
        
        response = await middleware.dispatch(mock_request, slow_call_next)
        
        # Should return timeout response
        assert response.status_code == 408

    @pytest.mark.asyncio
    async def test_middleware_exception_propagates(self):
        """Test middleware propagates exceptions."""
        mock_app = MagicMock()
        config = TimeoutConfig()
        middleware = TimeoutMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        
        async def error_call_next(request):
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await middleware.dispatch(mock_request, error_call_next)

    @pytest.mark.asyncio
    async def test_middleware_uses_endpoint_timeout(self):
        """Test middleware uses endpoint-specific timeout."""
        mock_app = MagicMock()
        config = TimeoutConfig()
        middleware = TimeoutMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/v1/chat/completions"  # Has 300s timeout
        
        mock_response = MagicMock()
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert response == mock_response


class TestSetupRequestTimeout:
    """Tests for setup_request_timeout function."""

    def test_setup_request_timeout(self):
        """Test request timeout setup."""
        mock_app = MagicMock()
        
        setup_request_timeout(mock_app)
        
        mock_app.add_middleware.assert_called_once()
        
    def test_setup_request_timeout_with_config(self):
        """Test request timeout setup with custom config."""
        mock_app = MagicMock()
        config = TimeoutConfig()
        
        setup_request_timeout(mock_app, config)
        
        mock_app.add_middleware.assert_called_once()
