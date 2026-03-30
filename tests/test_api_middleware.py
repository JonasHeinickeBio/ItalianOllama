"""Unit tests for API middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from italianollama.api.middleware.logging import (
    LoggingMiddleware,
    StructuredLoggingMiddleware,
)
from italianollama.api.middleware.metrics import (
    PrometheusMetrics,
    MetricsMiddleware,
    _metrics,
)
from italianollama.api.middleware.rate_limit import (
    RateLimitExceeded,
    RateLimitConfig,
    RateLimitStore,
    RateLimitMiddleware,
)
from italianollama.api.middleware.auth import (
    create_access_token,
    verify_access_token,
    get_current_student,
    require_api_key,
)


# ============ Logging Middleware Tests ============

class TestLoggingMiddleware:
    """Tests for LoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_logging_middleware_initialization(self):
        """Test LoggingMiddleware initializes correctly."""
        app = MagicMock()
        middleware = LoggingMiddleware(app)
        assert middleware.app is app
        assert middleware.logger is not None

    @pytest.mark.asyncio
    async def test_logging_middleware_dispatch(self):
        """Test LoggingMiddleware processes request."""
        app = MagicMock()
        middleware = LoggingMiddleware(app)
        
        # Mock request
        mock_request = MagicMock(spec=StarletteRequest)
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.client.host = "127.0.0.1"
        mock_request.state = MagicMock()
        
        # Mock response
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        
        call_next = AsyncMock(return_value=mock_response)
        
        result = await middleware.dispatch(mock_request, call_next)
        
        call_next.assert_called_once()
        assert "X-Request-ID" in result.headers


class TestStructuredLoggingMiddleware:
    """Tests for StructuredLoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_structured_logging_initialization(self):
        """Test StructuredLoggingMiddleware initializes."""
        app = MagicMock()
        middleware = StructuredLoggingMiddleware(app)
        assert middleware.app is app


# ============ Metrics Tests ============

class TestPrometheusMetrics:
    """Tests for PrometheusMetrics class."""

    def test_metrics_init(self):
        """Test PrometheusMetrics initializes with empty metrics."""
        metrics = PrometheusMetrics()
        assert metrics.http_request_count == {}
        assert metrics.llm_request_count["total"] == 0
        assert metrics.active_connections == 0

    def test_record_http_request(self):
        """Test recording HTTP request metrics."""
        metrics = PrometheusMetrics()
        metrics.record_http_request("/test", "GET", 200, 50.0)
        
        assert "/test" in metrics.http_request_count
        assert 200 in metrics.http_request_count["/test"]
        assert metrics.http_request_count["/test"][200] == 1

    def test_record_error(self):
        """Test recording error metrics."""
        metrics = PrometheusMetrics()
        metrics.record_error("/test", "ValueError")
        
        assert "/test" in metrics.http_error_count
        assert "ValueError" in metrics.http_error_count["/test"]

    def test_record_llm_request(self):
        """Test recording LLM request metrics."""
        metrics = PrometheusMetrics()
        metrics.record_llm_request(150.0)
        
        assert metrics.llm_request_count["total"] == 1
        assert len(metrics.llm_request_duration) == 1

    def test_record_neo4j_query(self):
        """Test recording Neo4j query metrics."""
        metrics = PrometheusMetrics()
        metrics.record_neo4j_query("create_student", 25.0)
        
        assert metrics.neo4j_query_count["total"] == 1
        assert metrics.neo4j_query_count["create_student"] == 1

    def test_get_metrics_text(self):
        """Test generating Prometheus metrics text."""
        metrics = PrometheusMetrics()
        metrics.record_http_request("/test", "GET", 200, 50.0)
        metrics.record_llm_request(100.0)
        
        metrics_text = metrics.get_metrics_text()
        
        assert "http_request_total" in metrics_text
        assert "llm_request_total" in metrics_text

    def test_normalize_path(self):
        """Test path normalization removes IDs."""
        metrics = PrometheusMetrics()
        
        # UUID - uses full regex pattern
        normalized = metrics._normalize_path("/students/12345678-1234-1234-1234-123456789abc")
        assert "{id}" in normalized
        
        # Numeric ID
        normalized = metrics._normalize_path("/students/123")
        assert "/students/{id}" in normalized


class TestMetricsMiddleware:
    """Tests for MetricsMiddleware."""

    @pytest.mark.asyncio
    async def test_metrics_middleware_initialization(self):
        """Test MetricsMiddleware initializes."""
        app = MagicMock()
        middleware = MetricsMiddleware(app)
        assert middleware.app is app
        assert middleware.metrics is not None

    @pytest.mark.asyncio
    async def test_metrics_middleware_increments_connections(self):
        """Test metrics middleware tracks active connections."""
        app = MagicMock()
        middleware = MetricsMiddleware(app)
        
        mock_request = MagicMock(spec=StarletteRequest)
        mock_request.url.path = "/test"
        mock_request.method = "GET"
        mock_request.state = MagicMock()
        
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        
        call_next = AsyncMock(return_value=mock_response)
        
        await middleware.dispatch(mock_request, call_next)
        
        assert middleware.metrics.active_connections == 0  # Reset after request


# ============ Rate Limit Tests ============

class TestRateLimitConfig:
    """Tests for RateLimitConfig."""

    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig default limits."""
        config = RateLimitConfig()
        assert config.DEFAULT_LIMIT == (1000, 60)
        assert "/v1/chat/completions" in config.ENDPOINT_LIMITS

    def test_endpoint_limits_defined(self):
        """Test endpoint-specific limits are defined."""
        config = RateLimitConfig()
        
        # LLM endpoints have stricter limits
        assert config.ENDPOINT_LIMITS["/v1/chat/completions"] == (100, 60)
        
        # Auth endpoints have strict limits
        assert config.ENDPOINT_LIMITS["/auth/token"] == (10, 60)


class TestRateLimitStore:
    """Tests for RateLimitStore."""

    @pytest.mark.asyncio
    async def test_rate_limit_store_allows_first_request(self):
        """Test first request is always allowed."""
        store = RateLimitStore()
        allowed, retry_after = await store.check_limit("test", 10, 60)
        
        assert allowed is True
        assert retry_after == 0

    @pytest.mark.asyncio
    async def test_rate_limit_store_blocks_over_limit(self):
        """Test store blocks requests over limit."""
        store = RateLimitStore()
        
        # Make 5 requests (limit is 5)
        for _ in range(5):
            allowed, _ = await store.check_limit("test2", 5, 60)
            assert allowed is True
        
        # 6th request should be blocked
        allowed, retry_after = await store.check_limit("test2", 5, 60)
        assert allowed is False
        assert retry_after > 0

    @pytest.mark.asyncio
    async def test_rate_limit_store_cleanup(self):
        """Test store cleanup removes old entries."""
        store = RateLimitStore()
        
        await store.check_limit("test3", 5, 60)
        await store.cleanup_old_entries(max_age=0)
        
        # Key should be removed
        assert "test3" not in store._store


class TestRateLimitExceeded:
    """Tests for RateLimitExceeded exception."""

    def test_rate_limit_exceeded_init(self):
        """Test RateLimitExceeded initializes correctly."""
        exc = RateLimitExceeded(retry_after=30)
        assert exc.status_code == 429
        assert exc.retry_after == 30


# ============ Auth Tests ============

class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_returns_string(self):
        """Test token is created as string."""
        from datetime import timedelta
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value.jwt_algorithm = "HS256"
            mock_settings.return_value.auth_secret = "test-secret-key-that-is-long-enough-32"
            mock_settings.return_value.jwt_expiration_hours = 4
            
            token = create_access_token("student123")
            
            assert isinstance(token, str)
            assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Test token with custom expiration."""
        from datetime import timedelta
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value.jwt_algorithm = "HS256"
            mock_settings.return_value.auth_secret = "test-secret-key-that-is-long-enough-32"
            mock_settings.return_value.jwt_expiration_hours = 4
            
            token = create_access_token("student123", expires_delta=timedelta(hours=1))
            
            assert isinstance(token, str)


class TestVerifyAccessToken:
    """Tests for verify_access_token function."""

    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        from datetime import timedelta
        
        secret = "test-secret-key-that-is-long-enough-32"
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value.jwt_algorithm = "HS256"
            mock_settings.return_value.auth_secret = secret
            mock_settings.return_value.jwt_expiration_hours = 4
            
            # Create token
            token = create_access_token("student123")
            
            # Verify it
            payload = verify_access_token(token)
            
            assert payload["sub"] == "student123"

    def test_verify_invalid_token(self):
        """Test verifying invalid token raises error."""
        from italianollama.api.exceptions import AuthenticationError
        
        with pytest.raises(AuthenticationError):
            verify_access_token("invalid-token")

    def test_verify_expired_token(self):
        """Test verifying expired token raises error."""
        from datetime import timedelta
        from italianollama.api.exceptions import AuthenticationError
        
        secret = "test-secret-key-that-is-long-enough-32"
        
        with patch("italianollama.api.middleware.auth.get_settings") as mock_settings:
            mock_settings.return_value.jwt_algorithm = "HS256"
            mock_settings.return_value.auth_secret = secret
            
            # Create already-expired token
            token = create_access_token("student123", expires_delta=timedelta(hours=-1))
            
            with pytest.raises(AuthenticationError) as exc_info:
                verify_access_token(token)
            
            assert "expired" in str(exc_info.value.detail).lower()
