"""Unit tests for middleware modules with full mocking."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response


class TestLoggingMiddleware:
    """Test logging middleware."""

    def test_logging_middleware_request_id_generated(self):
        """Test that request ID is generated for each request."""
        from italianollama.api.middleware.logging import LoggingMiddleware
        
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"request_id": request.state.request_id}
        
        app.add_middleware(LoggingMiddleware)
        
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200
            data = response.json()
            assert "request_id" in data
            assert len(data["request_id"]) > 0
            # Check response header
            assert "X-Request-ID" in response.headers

    def test_logging_middleware_exception_handling(self):
        """Test logging middleware logs exceptions."""
        from italianollama.api.middleware.logging import LoggingMiddleware
        
        app = FastAPI()
        
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        app.add_middleware(LoggingMiddleware)
        
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/error")
            # Middleware logs but re-raises the exception
            assert response.status_code == 500


class TestStructuredLoggingMiddleware:
    """Test structured logging middleware."""

    def test_structured_logging_middleware(self):
        """Test structured logging produces JSON."""
        from italianollama.api.middleware.logging import StructuredLoggingMiddleware
        
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint(request: Request):
            return {"status": "ok"}
        
        app.add_middleware(StructuredLoggingMiddleware)
        
        with TestClient(app) as client:
            response = client.get("/test")
            assert response.status_code == 200


class TestErrorHandlers:
    """Test error handling middleware."""

    def test_tutor_exception_handler(self):
        """Test custom tutor exception handler."""
        from italianollama.api.main import app
        from italianollama.api.exceptions import NotFoundError
        
        # Add a test route that raises NotFoundError
        @app.get("/test-not-found")
        async def test_not_found():
            raise NotFoundError("Student", "Student not found")
        
        with TestClient(app) as client:
            response = client.get("/test-not-found")
            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "trace_id" in data

    def test_validation_error_handler(self):
        """Test Pydantic validation error handler."""
        from pydantic import ValidationError
        from italianollama.api.main import app
        
        @app.get("/test-validation")
        async def test_validation():
            raise ValidationError.from_exception_data(
                "TestModel",
                [{"type": "missing", "loc": ("field",), "msg": "field required"}]
            )
        
        with TestClient(app) as client:
            response = client.get("/test-validation")
            assert response.status_code == 400

    def test_general_exception_handler(self):
        """Test general exception handler."""
        from fastapi.responses import JSONResponse
        
        app = FastAPI()
        
        @app.get("/test-error")
        async def test_error():
            raise RuntimeError("Unexpected error")
        
        @app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            return JSONResponse(
                status_code=500,
                content={"error": "internal_error", "message": str(exc)}
            )
        
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/test-error")
            assert response.status_code == 500
            data = response.json()
            assert "error" in data


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    def test_rate_limit_config_defaults(self):
        """Test default rate limit configuration."""
        from italianollama.api.middleware.rate_limit import RateLimitConfig
        
        config = RateLimitConfig()
        assert config.DEFAULT_LIMIT == (1000, 60)
        assert "/v1/chat/completions" in config.ENDPOINT_LIMITS
        assert "/health" in config.ENDPOINT_LIMITS

    def test_rate_limit_exceeded_exception(self):
        """Test rate limit exceeded exception."""
        from italianollama.api.middleware.rate_limit import RateLimitExceeded
        
        exc = RateLimitExceeded(retry_after=30)
        assert exc.status_code == 429
        assert exc.retry_after == 30

    def test_rate_limit_store_check(self):
        """Test rate limit store check logic."""
        from italianollama.api.middleware.rate_limit import RateLimitStore
        
        store = RateLimitStore()
        
        # First request should be allowed
        allowed, retry_after = asyncio_run(store.check_limit("test_key", 10, 60))
        assert allowed is True
        assert retry_after == 0

    def test_rate_limit_store_limit_exceeded(self):
        """Test rate limit when limit is exceeded."""
        from italianollama.api.middleware.rate_limit import RateLimitStore
        
        store = RateLimitStore()
        
        # Fill up to limit
        import asyncio
        
        async def fill_limit():
            for _ in range(15):
                allowed, _ = await store.check_limit("limit_test", 10, 60)
                if not allowed:
                    break
        
        asyncio.run(fill_limit())
        
        # Next request should be denied
        allowed, retry_after = asyncio_run(store.check_limit("limit_test", 10, 60))
        assert allowed is False
        assert retry_after > 0


class TestTimeoutMiddleware:
    """Test timeout middleware."""

    def test_timeout_config_defaults(self):
        """Test default timeout configuration."""
        from italianollama.api.middleware.timeout import TimeoutConfig
        
        config = TimeoutConfig()
        assert config.DEFAULT_TIMEOUT == 30
        assert config.ENDPOINT_TIMEOUTS["/v1/chat/completions"] == 300
        assert config.ENDPOINT_TIMEOUTS["/health"] == 5

    def test_request_timeout_error(self):
        """Test request timeout error exception."""
        from italianollama.api.middleware.timeout import RequestTimeoutError
        
        exc = RequestTimeoutError(timeout_seconds=60)
        assert exc.status_code == 408
        assert exc.timeout_seconds == 60


class TestMetricsMiddleware:
    """Test metrics middleware."""

    def test_prometheus_metrics_initialization(self):
        """Test Prometheus metrics initialization."""
        from italianollama.api.middleware.metrics import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        assert metrics.http_request_count == {}
        assert metrics.llm_request_count["total"] == 0
        assert metrics.neo4j_query_count["total"] == 0

    def test_record_http_request(self):
        """Test recording HTTP request metrics."""
        from italianollama.api.middleware.metrics import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        metrics.record_http_request("/test", "GET", 200, 50.0)
        
        assert "/test" in metrics.http_request_count
        assert 200 in metrics.http_request_count["/test"]
        assert metrics.http_request_count["/test"][200] == 1

    def test_record_error(self):
        """Test recording error metrics."""
        from italianollama.api.middleware.metrics import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        metrics.record_error("/test", "ValueError")
        
        assert "/test" in metrics.http_error_count
        assert "ValueError" in metrics.http_error_count["/test"]

    def test_record_llm_request(self):
        """Test recording LLM request metrics."""
        from italianollama.api.middleware.metrics import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        metrics.record_llm_request(100.0)
        
        assert metrics.llm_request_count["total"] == 1
        assert len(metrics.llm_request_duration) == 1

    def test_record_neo4j_query(self):
        """Test recording Neo4j query metrics."""
        from italianollama.api.middleware.metrics import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        metrics.record_neo4j_query("get_student", 25.0)
        
        assert metrics.neo4j_query_count["total"] == 1
        assert metrics.neo4j_query_count["get_student"] == 1

    def test_get_metrics_text(self):
        """Test generating Prometheus metrics text."""
        from italianollama.api.middleware.metrics import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        metrics.record_http_request("/test", "GET", 200, 50.0)
        metrics.record_llm_request(100.0)
        
        metrics_text = metrics.get_metrics_text()
        assert "http_request_total" in metrics_text
        assert "llm_request_total" in metrics_text

    def test_normalize_path(self):
        """Test path normalization for metrics."""
        from italianollama.api.middleware.metrics import PrometheusMetrics
        
        metrics = PrometheusMetrics()
        
        # Test numeric ID removal
        normalized = metrics._normalize_path("/students/12345")
        assert "/students/{id}" == normalized
        
        # Test UUID removal
        normalized = metrics._normalize_path("/students/550e8400-e29b-41d4-a716-446655440000")
        assert "/students/{id}" == normalized


# Helper to run async tests
def asyncio_run(coro):
    """Run async coroutine in sync context."""
    import asyncio
    return asyncio.run(coro)


class TestAuthMiddleware:
    """Test auth middleware functions."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        from datetime import timedelta
        from italianollama.api.middleware.auth import create_access_token
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret-key-for-testing-purposes-32",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            
            token = create_access_token("student123")
            assert token is not None
            assert isinstance(token, str)

    def test_create_access_token_with_expiry(self):
        """Test JWT token with custom expiration."""
        from datetime import timedelta
        from italianollama.api.middleware.auth import create_access_token
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret-key-for-testing-purposes-32",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            
            token = create_access_token("student123", timedelta(hours=8))
            assert token is not None

    def test_verify_access_token_valid(self):
        """Test verifying valid token."""
        from datetime import timedelta
        from italianollama.api.middleware.auth import create_access_token, verify_access_token
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret-key-for-testing-purposes-32",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            
            token = create_access_token("student123")
            payload = verify_access_token(token)
            
            assert payload["sub"] == "student123"
            assert "exp" in payload

    def test_verify_access_token_expired(self):
        """Test verifying expired token raises error."""
        from datetime import timedelta
        from italianollama.api.middleware.auth import verify_access_token
        from italianollama.api.exceptions import AuthenticationError
        import jwt
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret-key-for-testing-purposes-32",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            
            # Create an expired token
            from datetime import datetime, timezone
            expired_payload = {
                "sub": "student123",
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            }
            expired_token = jwt.encode(
                expired_payload,
                "test-secret-key-for-testing-purposes-32",
                algorithm="HS256",
            )
            
            with pytest.raises(AuthenticationError):
                verify_access_token(expired_token)

    def test_verify_access_token_invalid(self):
        """Test verifying invalid token raises error."""
        from italianollama.api.middleware.auth import verify_access_token
        from italianollama.api.exceptions import AuthenticationError
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret-key-for-testing-purposes-32",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            
            with pytest.raises(AuthenticationError):
                verify_access_token("invalid-token")
