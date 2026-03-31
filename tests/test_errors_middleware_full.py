"""Unit tests for errors middleware with mocking."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError


class TestErrorHandlers:
    """Tests for error handling middleware."""

    def test_setup_error_handlers(self):
        """Test setting up error handlers."""
        from italianollama.api.middleware.errors import setup_error_handlers
        from italianollama.api.exceptions import (
            TutorException,
            ValidationError,
            NotFoundError,
            AuthenticationError,
        )

        app = FastAPI()
        setup_error_handlers(app)

        # Check that handlers are registered
        assert 500 in app.exception_handler._handlers
        assert 400 in app.exception_handler._handlers

    @pytest.mark.asyncio
    async def test_tutor_exception_handler(self):
        """Test handling of custom TutorException."""
        from italianollama.api.middleware.errors import setup_error_handlers
        from italianollama.api.exceptions import TutorException

        app = FastAPI()
        setup_error_handlers(app)

        @app.get("/test")
        async def test_endpoint():
            raise TutorException(
                status_code=400,
                detail="Test error",
                error_type="test_error",
            )

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 400
        assert "trace_id" in response.json()

    @pytest.mark.asyncio
    async def test_validation_error_handler(self):
        """Test handling of Pydantic ValidationError."""
        from italianollama.api.middleware.errors import setup_error_handlers

        app = FastAPI()
        setup_error_handlers(app)

        @app.get("/test")
        async def test_endpoint():
            raise ValidationError.from_exception_data(
                "TestModel",
                [{"type": "missing", "loc": ("field",), "msg": "field required", "input": {}}],
            )

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 400
        assert "validation_errors" in response.json()

    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """Test handling of general Exception."""
        from italianollama.api.middleware.errors import setup_error_handlers

        app = FastAPI()
        setup_error_handlers(app)

        @app.get("/test")
        async def test_endpoint():
            raise Exception("Internal error")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 500
        # Should not expose internal error details
        assert "unexpected error" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def test_not_found_error_handler(self):
        """Test handling of NotFoundError."""
        from italianollama.api.middleware.errors import setup_error_handlers
        from italianollama.api.exceptions import NotFoundError

        app = FastAPI()
        setup_error_handlers(app)

        @app.get("/test")
        async def test_endpoint():
            raise NotFoundError("Student", "student123")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 404
        assert "not_found_error" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_authentication_error_handler(self):
        """Test handling of AuthenticationError."""
        from italianollama.api.middleware.errors import setup_error_handlers
        from italianollama.api.exceptions import AuthenticationError

        app = FastAPI()
        setup_error_handlers(app)

        @app.get("/test")
        async def test_endpoint():
            raise AuthenticationError("Invalid credentials")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 401
        assert "authentication_error" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_rate_limit_error_handler(self):
        """Test handling of RateLimitError."""
        from italianollama.api.middleware.errors import setup_error_handlers
        from italianollama.api.exceptions import RateLimitError

        app = FastAPI()
        setup_error_handlers(app)

        @app.get("/test")
        async def test_endpoint():
            raise RateLimitError("Too many requests")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 429
        assert "rate_limit_error" in response.json()["error"]
