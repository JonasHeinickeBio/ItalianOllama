"""Tests for italianollama.api.middleware.rate_limit module."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from italianollama.api.middleware.rate_limit import (
    RateLimitConfig,
    RateLimitExceeded,
    RateLimitMiddleware,
    RateLimitStore,
    setup_rate_limiting,
)


class TestRateLimitExceeded:
    def test_status_code(self):
        exc = RateLimitExceeded(retry_after=30)
        assert exc.status_code == 429

    def test_retry_after(self):
        exc = RateLimitExceeded(retry_after=45)
        assert exc.retry_after == 45
        assert "45" in str(exc.detail)

    def test_default_retry_after(self):
        exc = RateLimitExceeded()
        assert exc.retry_after == 60


class TestRateLimitStore:
    @pytest.mark.asyncio
    async def test_allows_under_limit(self):
        store = RateLimitStore()
        allowed, retry_after = await store.check_limit("key1", 10, 60)
        assert allowed is True
        assert retry_after == 0

    @pytest.mark.asyncio
    async def test_blocks_over_limit(self):
        store = RateLimitStore()
        for _ in range(5):
            await store.check_limit("key2", 5, 60)
        allowed, retry_after = await store.check_limit("key2", 5, 60)
        assert allowed is False
        assert retry_after > 0

    @pytest.mark.asyncio
    async def test_dry_run_does_not_record(self):
        store = RateLimitStore()
        # Dry run should not consume quota
        for _ in range(5):
            await store.check_limit_dry_run("drykey", 5, 60)
        # Still allowed since dry run didn't record
        allowed, _ = await store.check_limit_dry_run("drykey", 5, 60)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_dry_run_blocks_when_limit_reached(self):
        store = RateLimitStore()
        # Actually consume limit
        for _ in range(5):
            await store.check_limit("fillkey", 5, 60)
        # Dry run should also block
        allowed, retry_after = await store.check_limit_dry_run("fillkey", 5, 60)
        assert allowed is False

    @pytest.mark.asyncio
    async def test_dry_run_empty_key_allowed(self):
        store = RateLimitStore()
        allowed, retry_after = await store.check_limit_dry_run("newkey", 10, 60)
        assert allowed is True
        assert retry_after == 0

    @pytest.mark.asyncio
    async def test_cleanup_old_entries(self):
        store = RateLimitStore()
        await store.check_limit("cleankey", 10, 60)
        # Cleanup with 0 max_age removes everything
        await store.cleanup_old_entries(max_age=0)
        # After cleanup, key should be gone or empty
        assert "cleankey" not in store._store or len(store._store.get("cleankey", [])) == 0

    @pytest.mark.asyncio
    async def test_separate_keys_independent(self):
        store = RateLimitStore()
        for _ in range(5):
            await store.check_limit("key_a", 5, 60)
        # key_b should still be allowed
        allowed, _ = await store.check_limit("key_b", 5, 60)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_multiple_requests_tracked(self):
        store = RateLimitStore()
        for i in range(3):
            allowed, _ = await store.check_limit("trackkey", 10, 60)
            assert allowed is True
        assert len(store._store["trackkey"]) == 3


class TestRateLimitConfig:
    def test_default_limit(self):
        config = RateLimitConfig()
        assert config.DEFAULT_LIMIT == (1000, 60)

    def test_endpoint_limits(self):
        config = RateLimitConfig()
        assert "/v1/chat/completions" in config.ENDPOINT_LIMITS
        assert "/auth/token" in config.ENDPOINT_LIMITS

    def test_per_student_limits(self):
        config = RateLimitConfig()
        assert "/v1/chat/completions" in config.PER_STUDENT_LIMITS

    def test_health_endpoint_unrestricted(self):
        config = RateLimitConfig()
        limit, window = config.ENDPOINT_LIMITS.get("/health", config.DEFAULT_LIMIT)
        assert limit >= 1000


class TestRateLimitMiddleware:
    def make_app(self, config=None):
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, config=config)

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        return app

    def test_allows_normal_request(self):
        app = self.make_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_rate_limit_headers(self):
        app = self.make_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health")
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        assert "x-ratelimit-limit" in headers_lower
        assert "x-ratelimit-window" in headers_lower

    def test_with_student_id_header(self):
        app = self.make_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health", headers={"x-student-id": "student123"})
        assert resp.status_code == 200

    def test_with_query_param_student_id(self):
        app = self.make_app()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health?student_id=student456")
        assert resp.status_code == 200

    def test_with_bearer_token(self):
        from italianollama.api.middleware.auth import create_access_token

        app = self.make_app()
        client = TestClient(app, raise_server_exceptions=False)
        token = create_access_token("student789")
        resp = client.get("/health", headers={"authorization": f"Bearer {token}"})
        assert resp.status_code == 200


class TestSetupRateLimiting:
    def test_setup_registers_middleware(self):
        app = FastAPI()
        setup_rate_limiting(app)

        @app.get("/test")
        async def test_endpoint():
            return {"ok": True}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/test")
        assert resp.status_code == 200


class TestRateLimitMiddlewareExceeded:
    """Tests for rate limit exceeded paths."""

    def make_limited_app(self, limit=1, window=60, student_path=None):
        """Create app with very low rate limits to trigger 429s."""
        from italianollama.api.middleware.rate_limit import _rate_limit_store

        app = FastAPI()

        config = RateLimitConfig()
        # Patch endpoint limit to a very low value
        config.ENDPOINT_LIMITS["/chat"] = (limit, window)
        if student_path:
            config.PER_STUDENT_LIMITS["/chat"] = (limit, window)

        # Use fresh store per test
        store = RateLimitStore()
        middleware = RateLimitMiddleware.__new__(RateLimitMiddleware)
        middleware.config = config
        middleware.store = store

        app.add_middleware(RateLimitMiddleware, config=config)

        # Replace the middleware's store after it's added
        # We'll patch the global store instead
        @app.get("/chat")
        async def chat_endpoint():
            return {"result": "ok"}

        return app, store, config

    def test_global_rate_limit_exceeded(self):
        """Test that exceeding global rate limit returns 429."""
        import asyncio
        from unittest.mock import patch
        from italianollama.api.middleware.rate_limit import RateLimitStore

        store = RateLimitStore()

        # Pre-fill the store to exceed limit
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(store.check_limit("endpoint:/limited2", 1, 60))
            loop.run_until_complete(store.check_limit("endpoint:/limited2", 1, 60))
        finally:
            loop.close()

        app = FastAPI()
        config = RateLimitConfig()
        config.ENDPOINT_LIMITS["/limited2"] = (1, 60)

        app.add_middleware(RateLimitMiddleware, config=config)

        @app.get("/limited2")
        async def limited_endpoint():
            return {"result": "ok"}

        # Patch global store with pre-filled store
        with patch("italianollama.api.middleware.rate_limit._rate_limit_store", store):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get("/limited2")
            assert resp.status_code == 429

    def test_per_student_path_commits_to_store(self):
        """Test that student+path in PER_STUDENT_LIMITS records to store."""
        from italianollama.api.middleware.rate_limit import RateLimitStore
        from unittest.mock import patch

        store = RateLimitStore()
        app = FastAPI()
        config = RateLimitConfig()

        app.add_middleware(RateLimitMiddleware, config=config)

        @app.get("/v1/chat/completions")
        async def chat_endpoint():
            return {"result": "ok"}

        with patch("italianollama.api.middleware.rate_limit._rate_limit_store", store):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/v1/chat/completions",
                headers={"x-student-id": "student-commit-test"},
            )
            assert resp.status_code == 200
            # Student key should be in store
            student_keys = [k for k in store._store if "student-commit-test" in k]
            assert len(student_keys) > 0

    def test_invalid_bearer_token_no_student_id(self):
        """Test that invalid JWT Bearer token returns None student_id gracefully."""
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        client = TestClient(app, raise_server_exceptions=False)
        # Invalid token - should not crash, just return 200 with no student_id
        resp = client.get("/health", headers={"authorization": "Bearer invalid.jwt.token"})
        assert resp.status_code == 200

    def test_extract_student_id_from_state_json(self):
        """Test JSON body extraction path in _extract_student_id."""
        from unittest.mock import MagicMock
        from italianollama.api.middleware.rate_limit import RateLimitMiddleware, RateLimitConfig

        config = RateLimitConfig()
        store = RateLimitStore()
        middleware = RateLimitMiddleware.__new__(RateLimitMiddleware)
        middleware.config = config
        middleware.store = store

        request = MagicMock()
        request.query_params = {}
        request.headers = {}
        # Set up _json in state
        request.state._json = {"student_id": "student-from-json extra"}

        result = middleware._extract_student_id(request)
        assert result == "student-from-json"

    def test_extract_student_id_from_state_json_messages(self):
        """Test JSON body extraction via messages field."""
        from unittest.mock import MagicMock

        config = RateLimitConfig()
        store = RateLimitStore()
        middleware = RateLimitMiddleware.__new__(RateLimitMiddleware)
        middleware.config = config
        middleware.store = store

        request = MagicMock()
        request.query_params = {}
        request.headers = {}
        request.state._json = {"messages": [{"content": "student_id_value extra"}]}

        result = middleware._extract_student_id(request)
        assert result == "student_id_value"

    def test_extract_student_id_exception_returns_none(self):
        """Test that exceptions in _extract_student_id return None."""
        from unittest.mock import MagicMock, PropertyMock

        config = RateLimitConfig()
        store = RateLimitStore()
        middleware = RateLimitMiddleware.__new__(RateLimitMiddleware)
        middleware.config = config
        middleware.store = store

        request = MagicMock()
        # Make query_params raise an exception
        type(request).query_params = PropertyMock(side_effect=RuntimeError("crash"))
        type(request.state).fake = PropertyMock(side_effect=AttributeError)

        result = middleware._extract_student_id(request)
        assert result is None

    def test_extract_student_id_non_bearer_auth(self):
        """Test that non-Bearer auth header doesn't extract student_id."""
        from unittest.mock import MagicMock

        config = RateLimitConfig()
        store = RateLimitStore()
        middleware = RateLimitMiddleware.__new__(RateLimitMiddleware)
        middleware.config = config
        middleware.store = store

        request = MagicMock()
        request.query_params = {}
        # Auth header present but not Bearer format
        request.headers = {"authorization": "Basic dXNlcjpwYXNz"}
        # No state._json
        del request.state._json

        result = middleware._extract_student_id(request)
        assert result is None

    def test_extract_student_id_json_empty_student_id(self):
        """Test JSON body extraction when student_id is empty."""
        from unittest.mock import MagicMock

        config = RateLimitConfig()
        store = RateLimitStore()
        middleware = RateLimitMiddleware.__new__(RateLimitMiddleware)
        middleware.config = config
        middleware.store = store

        request = MagicMock()
        request.query_params = {}
        request.headers = {}
        # JSON body with no student_id and empty messages
        request.state._json = {"messages": []}

        result = middleware._extract_student_id(request)
        # Falls through to query params / headers, which are empty
        assert result is None

    def test_per_student_limit_exceeded(self):
        """Test per-student rate limit exceeded returns 429."""
        import asyncio
        from unittest.mock import patch
        from italianollama.api.middleware.rate_limit import RateLimitStore

        store = RateLimitStore()

        # Pre-fill the per-student store to exceed limit (50 requests/hour)
        loop = asyncio.new_event_loop()
        try:
            for _ in range(51):
                loop.run_until_complete(
                    store.check_limit("student:testuser:/v1/chat/completions", 50, 3600)
                )
        finally:
            loop.close()

        app = FastAPI()
        config = RateLimitConfig()
        app.add_middleware(RateLimitMiddleware, config=config)

        @app.get("/v1/chat/completions")
        async def chat_endpoint():
            return {"result": "ok"}

        with patch("italianollama.api.middleware.rate_limit._rate_limit_store", store):
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.get(
                "/v1/chat/completions",
                headers={"x-student-id": "testuser"},
            )
            assert resp.status_code == 429
