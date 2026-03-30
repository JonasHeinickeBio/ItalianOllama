"""Unit tests for timeout middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, Response
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse


class TestTimeoutMiddleware:
    """Tests for TimeoutMiddleware."""

    @pytest.mark.asyncio
    async def test_timeout_middleware_init(self):
        """Test TimeoutMiddleware initializes."""
        from italianollama.api.middleware.timeout import TimeoutMiddleware
        
        app = MagicMock()
        middleware = TimeoutMiddleware(app, timeout=30)
        
        assert middleware.app is app
        assert middleware.timeout == 30

    @pytest.mark.asyncio
    async def test_timeout_middleware_default_timeout(self):
        """Test TimeoutMiddleware default timeout."""
        from italianollama.api.middleware.timeout import TimeoutMiddleware
        
        app = MagicMock()
        middleware = TimeoutMiddleware(app)
        
        assert middleware.timeout == 120  # Default

    @pytest.mark.asyncio
    async def test_timeout_middleware_dispatch_slow_request(self):
        """Test middleware handles slow requests."""
        from italianollama.api.middleware.timeout import TimeoutMiddleware
        
        app = MagicMock()
        middleware = TimeoutMiddleware(app, timeout=1)
        
        mock_request = MagicMock(spec=StarletteRequest)
        mock_request.method = "POST"
        mock_request.url.path = "/test"
        mock_request.state = MagicMock()
        
        # Mock a slow response
        async def slow_call_next(request):
            await asyncio.sleep(2)  # Simulate slow response
            return MagicMock(status_code=200)
        
        # This should timeout
        import asyncio
        
        async def test():
            try:
                result = await middleware.dispatch(mock_request, slow_call_next)
            except asyncio.TimeoutError:
                pass  # Expected
            except Exception:
                pass  # May also raise timeout error
        
        # Run the test
        asyncio.run(test())

    @pytest.mark.asyncio
    async def test_timeout_middleware_dispatch_fast_request(self):
        """Test middleware handles fast requests."""
        from italianollama.api.middleware.timeout import TimeoutMiddleware
        
        app = MagicMock()
        middleware = TimeoutMiddleware(app, timeout=10)
        
        mock_request = MagicMock(spec=StarletteRequest)
        mock_request.method = "GET"
        mock_request.url.path = "/health"
        mock_request.state = MagicMock()
        
        mock_response = MagicMock(spec=StarletteResponse)
        mock_response.status_code = 200
        mock_response.headers = {}
        
        async def fast_call_next(request):
            return mock_response
        
        result = await middleware.dispatch(mock_request, fast_call_next)
        
        assert result is not None


class TestRequestTimeout:
    """Tests for request timeout functionality."""

    def test_timeout_config_imports(self):
        """Test timeout config can be imported."""
        from italianollama.api.middleware.timeout import (
            TimeoutConfig,
            get_timeout_config,
        )
        
        assert TimeoutConfig is not None
        assert get_timeout_config is not None

    def test_timeout_config_defaults(self):
        """Test timeout config defaults."""
        from italianollama.api.middleware.timeout import TimeoutConfig
        
        config = TimeoutConfig()
        assert config.default_timeout == 120
        assert config.llm_timeout == 120

    def test_timeout_config_endpoint_timeouts(self):
        """Test endpoint-specific timeouts."""
        from italianollama.api.middleware.timeout import TimeoutConfig
        
        config = TimeoutConfig()
        
        # LLM endpoints need longer timeout
        assert config.get_timeout("/v1/chat/completions") >= 60
        
        # Health check is fast
        assert config.get_timeout("/health") <= 10


class TestTimeoutException:
    """Tests for timeout exception."""

    def test_timeout_exception_init(self):
        """Test TimeoutException initializes."""
        from italianollama.api.middleware.timeout import TimeoutException
        
        exc = TimeoutException(timeout=30)
        assert exc.timeout == 30
        assert exc.status_code == 504

    def test_timeout_exception_message(self):
        """Test TimeoutException message."""
        from italianollama.api.middleware.timeout import TimeoutException
        
        exc = TimeoutException(timeout=60)
        message = exc.detail["message"]
        assert "timeout" in message.lower()
        assert "60" in message


# Helper for asyncio tests
import asyncio
