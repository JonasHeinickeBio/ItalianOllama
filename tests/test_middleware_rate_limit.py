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
