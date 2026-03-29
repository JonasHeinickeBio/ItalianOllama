"""Tests for italianollama.api.middleware.timeout module."""
import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from italianollama.api.middleware.timeout import (
    RequestTimeoutError,
    TimeoutConfig,
    TimeoutMiddleware,
    setup_request_timeout,
)


class TestRequestTimeoutError:
    def test_status_code(self):
        exc = RequestTimeoutError(timeout_seconds=30)
        assert exc.status_code == 408

    def test_message(self):
        exc = RequestTimeoutError(timeout_seconds=30)
        assert "30" in str(exc.detail)

    def test_timeout_stored(self):
        exc = RequestTimeoutError(timeout_seconds=60)
        assert exc.timeout_seconds == 60

    def test_detail_is_dict(self):
        exc = RequestTimeoutError(timeout_seconds=30)
        assert isinstance(exc.detail, dict)
        assert exc.detail["error"] == "request_timeout"


class TestTimeoutConfig:
    def test_default_timeout(self):
        config = TimeoutConfig()
        assert config.DEFAULT_TIMEOUT == 30

    def test_llm_endpoint_timeout(self):
        config = TimeoutConfig()
        assert config.ENDPOINT_TIMEOUTS["/v1/chat/completions"] == 300

    def test_health_endpoint_timeout(self):
        config = TimeoutConfig()
        assert config.ENDPOINT_TIMEOUTS["/health"] == 5

    def test_auth_endpoint_timeout(self):
        config = TimeoutConfig()
        assert config.ENDPOINT_TIMEOUTS["/auth/token"] == 10

    def test_chat_endpoint_timeout(self):
        config = TimeoutConfig()
        assert config.ENDPOINT_TIMEOUTS["/chat"] == 300


class TestTimeoutMiddleware:
    def make_app(self, config=None):
        app = FastAPI()
        app.add_middleware(TimeoutMiddleware, config=config)

        @app.get("/fast")
        async def fast_endpoint():
            return {"result": "fast"}

        @app.get("/timeout")
        async def timeout_endpoint():
            await asyncio.sleep(10)
            return {"result": "slow"}

        return app

    def test_fast_request_passes(self):
        app = self.make_app()
        client = TestClient(app)
        resp = client.get("/fast")
        assert resp.status_code == 200

    def test_timeout_returns_408(self):
        config = TimeoutConfig()
        config.ENDPOINT_TIMEOUTS["/timeout"] = 0.001  # Very short timeout
        app = self.make_app(config=config)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/timeout")
        assert resp.status_code == 408

    def test_timeout_response_content(self):
        config = TimeoutConfig()
        config.ENDPOINT_TIMEOUTS["/timeout"] = 0.001
        app = self.make_app(config=config)
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/timeout")
        data = resp.json()
        assert data["error"] == "request_timeout"
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        assert "x-request-timeout" in headers_lower

    def test_default_timeout_used_for_unknown_path(self):
        config = TimeoutConfig()
        config.DEFAULT_TIMEOUT = 60  # High default
        app = self.make_app(config=config)
        client = TestClient(app)
        resp = client.get("/fast")
        assert resp.status_code == 200


class TestSetupRequestTimeout:
    def test_registers_middleware(self):
        app = FastAPI()
        setup_request_timeout(app)

        @app.get("/test")
        async def test_endpoint():
            return {"ok": True}

        client = TestClient(app)
        resp = client.get("/test")
        assert resp.status_code == 200

    def test_with_custom_config(self):
        config = TimeoutConfig()
        app = FastAPI()
        setup_request_timeout(app, config=config)

        @app.get("/test")
        async def test_endpoint():
            return {"ok": True}

        client = TestClient(app)
        resp = client.get("/test")
        assert resp.status_code == 200
