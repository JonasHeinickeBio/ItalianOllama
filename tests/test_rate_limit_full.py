"""Unit tests for rate limit middleware - full coverage."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestRateLimitMiddlewareFull:
    """Full tests for rate limit middleware."""

    def test_rate_limit_config_endpoint_limits(self):
        """Test endpoint-specific rate limits."""
        from italianollama.api.middleware.rate_limit import RateLimitConfig
        config = RateLimitConfig()

        # Check default limits
        assert "/v1/chat/completions" in config.ENDPOINT_LIMITS
        assert "/auth/token" in config.ENDPOINT_LIMITS

    def test_rate_limit_config_default_limit(self):
        """Test default rate limit configuration."""
        from italianollama.api.middleware.rate_limit import RateLimitConfig
        config = RateLimitConfig()

        assert config.DEFAULT_LIMIT == (1000, 60)

    def test_rate_limit_config_per_student_limits(self):
        """Test per-student rate limits."""
        from italianollama.api.middleware.rate_limit import RateLimitConfig
        config = RateLimitConfig()

        assert "/v1/chat/completions" in config.PER_STUDENT_LIMITS
        assert config.PER_STUDENT_LIMITS["/v1/chat/completions"] == (50, 3600)

    @pytest.mark.asyncio
    async def test_rate_limit_store_check_limit_allowed(self):
        """Test rate limit store allows requests within limit."""
        from italianollama.api.middleware.rate_limit import RateLimitStore
        store = RateLimitStore()

        # First request should be allowed
        allowed, retry_after = await store.check_limit("test_key", 10, 60)
        assert allowed is True
        assert retry_after == 0

    @pytest.mark.asyncio
    async def test_rate_limit_store_check_limit_exceeded(self):
        """Test rate limit store blocks when limit exceeded."""
        from italianollama.api.middleware.rate_limit import RateLimitStore
        store = RateLimitStore()

        # Fill up the limit
        for _ in range(10):
            allowed, _ = await store.check_limit("test_key", 10, 60)

        # 11th request should be denied
        allowed, retry_after = await store.check_limit("test_key", 10, 60)
        assert allowed is False
        assert retry_after > 0

    @pytest.mark.asyncio
    async def test_rate_limit_store_cleanup(self):
        """Test rate limit store cleanup old entries."""
        from italianollama.api.middleware.rate_limit import RateLimitStore
        store = RateLimitStore()

        await store.check_limit("test_key", 10, 60)
        await store.check_limit("old_key", 10, 1)

        # Cleanup should remove old entries
        await store.cleanup_old_entries(max_age=0)

        # old_key should be removed
        assert "old_key" not in store._store

    def test_rate_limit_middleware_init(self):
        """Test RateLimitMiddleware initialization."""
        from italianollama.api.middleware.rate_limit import RateLimitMiddleware
        from fastapi import FastAPI

        app = FastAPI()
        middleware = RateLimitMiddleware(app)

        assert middleware.app is app
        assert middleware.store is not None

    def test_rate_limit_middleware_init_with_config(self):
        """Test RateLimitMiddleware initialization with custom config."""
        from italianollama.api.middleware.rate_limit import RateLimitMiddleware, RateLimitConfig
        from fastapi import FastAPI

        app = FastAPI()
        config = RateLimitConfig()
        middleware = RateLimitMiddleware(app, config)

        assert middleware.config is config

    def test_rate_limit_exceeded_str(self):
        """Test RateLimitExceeded string representation."""
        from italianollama.api.middleware.rate_limit import RateLimitExceeded

        exc = RateLimitExceeded(retry_after=30)
        assert str(exc.status_code) == "429"
        assert exc.retry_after == 30

    def test_rate_limit_exceeded_default(self):
        """Test RateLimitExceeded with default retry_after."""
        from italianollama.api.middleware.rate_limit import RateLimitExceeded

        exc = RateLimitExceeded()
        assert exc.retry_after == 60
