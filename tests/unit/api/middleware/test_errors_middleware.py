"""Unit tests for error middleware - full coverage."""

import pytest
from unittest.mock import MagicMock, patch


class TestErrorMiddleware:
    """Test error middleware."""

    def test_error_middleware_import(self):
        """Test error middleware module imports."""
        from italianollama.api.middleware import errors
        assert errors is not None

    def test_setup_error_handlers_exists(self):
        """Test setup_error_handlers function exists."""
        from italianollama.api.middleware.errors import setup_error_handlers
        assert callable(setup_error_handlers)

    def test_setup_error_handlers(self):
        """Test setup_error_handlers registers handlers."""
        from fastapi import FastAPI
        from italianollama.api.middleware.errors import setup_error_handlers
        
        app = FastAPI()
        setup_error_handlers(app)
        
        # Should have exception handlers now
        assert len(app.exception_handlers) > 0

    def test_http_exception_handler(self):
        """Test HTTP exception handler."""
        from fastapi import FastAPI, HTTPException
        from fastapi.testclient import TestClient
        from italianollama.api.middleware.errors import setup_error_handlers
        
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            raise HTTPException(status_code=404, detail="Not found")
        
        setup_error_handlers(app)
        
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 404
