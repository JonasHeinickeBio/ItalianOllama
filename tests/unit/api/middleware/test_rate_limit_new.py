"""Unit tests for rate limit middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
import asyncio
import time

from italianollama.api.middleware.rate_limit import (
    RateLimitExceeded,
    RateLimitConfig,
    RateLimitStore,
    RateLimitMiddleware,
    setup_rate_limiting,
)


class TestRateLimitExceeded:
    """Tests for RateLimitExceeded exception."""

    def test_rate_limit_exceeded_defaults(self):
        """Test RateLimitExceeded with defaults."""
        exc = RateLimitExceeded()
        assert exc.status_code == 429
        assert exc.retry_after == 60
        assert "Rate limit exceeded" in exc.detail["message"]

    def test_rate_limit_exceeded_custom(self):
        """Test RateLimitExceeded with custom retry time."""
        exc = RateLimitExceeded(retry_after=30)
        assert exc.retry_after == 30
        assert "30" in exc.detail["message"]


class TestRateLimitConfig:
    """Tests for RateLimitConfig class."""

    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig default values."""
        config = RateLimitConfig()
        assert config.DEFAULT_LIMIT == (1000, 60)

    def test_rate_limit_config_endpoint_limits(self):
        """Test RateLimitConfig endpoint limits."""
        config = RateLimitConfig()
        
        # Check LLM endpoints
        assert "/v1/chat/completions" in config.ENDPOINT_LIMITS
        assert config.ENDPOINT_LIMITS["/v1/chat/completions"] == (100, 60)
        
        # Check auth endpoints
        assert "/auth/token" in config.ENDPOINT_LIMITS
        assert config.ENDPOINT_LIMITS["/auth/token"] == (10, 60)
        
        # Check health endpoints
        assert "/health" in config.ENDPOINT_LIMITS

    def test_rate_limit_config_per_student_limits(self):
        """Test RateLimitConfig per-student limits."""
        config = RateLimitConfig()
        
        assert "/v1/chat/completions" in config.PER_STUDENT_LIMITS
        assert config.PER_STUDENT_LIMITS["/v1/chat/completions"] == (50, 3600)


class TestRateLimitStore:
    """Tests for RateLimitStore class."""

    @pytest.mark.asyncio
    async def test_rate_limit_store_allow_first_request(self):
        """Test first request is allowed."""
        store = RateLimitStore()
        allowed, retry_after = await store.check_limit("test-key", 10, 60)
        
        assert allowed is True
        assert retry_after == 0

    @pytest.mark.asyncio
    async def test_rate_limit_store_allow_under_limit(self):
        """Test requests under limit are allowed."""
        store = RateLimitStore()
        
        # Make 5 requests
        for _ in range(5):
            allowed, _ = await store.check_limit("key1", 10, 60)
            assert allowed is True

    @pytest.mark.asyncio
    async def test_rate_limit_store_block_at_limit(self):
        """Test request blocked at limit."""
        store = RateLimitStore()
        
        # Fill up to limit
        for _ in range(10):
            await store.check_limit("key2", 10, 60)
        
        # Next request should be blocked
        allowed, retry_after = await store.check_limit("key2", 10, 60)
        
        assert allowed is False
        assert retry_after > 0

    @pytest.mark.asyncio
    async def test_rate_limit_store_cleanup(self):
        """Test cleanup of old entries."""
        store = RateLimitStore()
        
        # Add some entries
        await store.check_limit("key3", 10, 60)
        
        # Cleanup should work
        await store.cleanup_old_entries(max_age=0)
        
        # Key should be removed
        assert "key3" not in store._store


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware class."""

    @pytest.mark.asyncio
    async def test_middleware_allows_request_under_limit(self):
        """Test middleware allows request under limit."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.query_params = {}
        mock_request.headers = {}
        mock_request.state = MagicMock()
        
        mock_call_next = AsyncMock()
        mock_response = MagicMock()
        mock_call_next.return_value = mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert response == mock_response
        assert mock_call_next.called

    @pytest.mark.asyncio
    async def test_middleware_blocks_rate_limit(self):
        """Test middleware blocks when rate limit exceeded."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.query_params = {}
        mock_request.headers = {}
        mock_request.state = MagicMock()
        
        # Mock call_next to raise rate limit
        async def raise_rate_limit():
            raise RateLimitExceeded(retry_after=30)
        
        mock_call_next = AsyncMock(side_effect=raise_rate_limit)
        
        # Should propagate the exception
        with pytest.raises(RateLimitExceeded):
            await middleware.dispatch(mock_request, mock_call_next)

    @pytest.mark.asyncio
    async def test_middleware_adds_headers(self):
        """Test middleware adds rate limit headers."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.query_params = {}
        mock_request.headers = {}
        mock_request.state = MagicMock()
        
        mock_response = MagicMock()
        mock_response.headers = {}
        
        mock_call_next = AsyncMock(return_value=mock_response)
        
        await middleware.dispatch(mock_request, mock_call_next)
        
        assert "X-RateLimit-Limit" in mock_response.headers
        assert "X-RateLimit-Window" in mock_response.headers


class TestExtractStudentID:
    """Tests for student ID extraction."""

    def test_extract_from_json_body(self):
        """Test extraction from JSON body."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/chat"
        mock_request.query_params = {}
        mock_request.headers = {}
        mock_request.state = MagicMock()
        mock_request.state._json = {"student_id": "student-from-body"}
        
        student_id = middleware._extract_student_id(mock_request)
        
        assert student_id == "student-from-body"

    def test_extract_from_query_param(self):
        """Test extraction from query parameter."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/chat"
        mock_request.query_params = {"student_id": "student-from-query"}
        mock_request.headers = {}
        mock_request.state = MagicMock()
        
        student_id = middleware._extract_student_id(mock_request)
        
        assert student_id == "student-from-query"

    def test_extract_from_header(self):
        """Test extraction from header."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/chat"
        mock_request.query_params = {}
        mock_request.headers = {"x-student-id": "student-from-header"}
        mock_request.state = MagicMock()
        
        student_id = middleware._extract_student_id(mock_request)
        
        assert student_id == "student-from-header"

    def test_extract_returns_none(self):
        """Test extraction returns None when no ID found."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(mock_app, config)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.query_params = {}
        mock_request.headers = {}
        mock_request.state = MagicMock()
        
        student_id = middleware._extract_student_id(mock_request)
        
        assert student_id is None


class TestSetupRateLimiting:
    """Tests for setup_rate_limiting function."""

    def test_setup_rate_limiting(self):
        """Test rate limiting setup."""
        mock_app = MagicMock()
        
        setup_rate_limiting(mock_app)
        
        # Should add middleware
        mock_app.add_middleware.assert_called_once()
        
    def test_setup_rate_limiting_with_config(self):
        """Test rate limiting setup with custom config."""
        mock_app = MagicMock()
        config = RateLimitConfig()
        
        setup_rate_limiting(mock_app, config)
        
        mock_app.add_middleware.assert_called_once()
