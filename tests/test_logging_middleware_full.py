"""Unit tests for logging middleware with mocking."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response


class TestLoggingMiddleware:
    """Tests for logging middleware."""

    def test_logging_middleware_init(self):
        """Test LoggingMiddleware initialization."""
        from italianollama.api.middleware.logging import LoggingMiddleware

        app = FastAPI()
        middleware = LoggingMiddleware(app)

        assert middleware.app is app
        assert middleware.logger is not None

    def test_logging_middleware_custom_logger(self):
        """Test LoggingMiddleware with custom logger name."""
        from italianollama.api.middleware.logging import LoggingMiddleware

        app = FastAPI()
        middleware = LoggingMiddleware(app, logger_name="custom_logger")

        assert middleware.logger.name == "custom_logger"

    @pytest.mark.asyncio
    async def test_logging_middleware_request_id(self):
        """Test LoggingMiddleware adds request ID."""
        from italianollama.api.middleware.logging import LoggingMiddleware

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"request_id": request.state.request_id}

        app.add_middleware(LoggingMiddleware)

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert "request_id" in response.json()
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_logging_middleware_error_handling(self):
        """Test LoggingMiddleware handles errors."""
        from italianollama.api.middleware.logging import LoggingMiddleware

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            raise Exception("Test error")

        app.add_middleware(LoggingMiddleware)

        client = TestClient(app)
        response = client.get("/test")

        # Should propagate error
        assert response.status_code == 500


class TestStructuredLoggingMiddleware:
    """Tests for structured logging middleware."""

    def test_structured_logging_init(self):
        """Test StructuredLoggingMiddleware initialization."""
        from italianollama.api.middleware.logging import StructuredLoggingMiddleware

        app = FastAPI()
        middleware = StructuredLoggingMiddleware(app)

        assert middleware.app is app
        assert middleware.logger is not None

    @pytest.mark.asyncio
    async def test_structured_logging_request_id(self):
        """Test StructuredLoggingMiddleware adds request ID."""
        from italianollama.api.middleware.logging import StructuredLoggingMiddleware

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"request_id": request.state.request_id}

        app.add_middleware(StructuredLoggingMiddleware)

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
