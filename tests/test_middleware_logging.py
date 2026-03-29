"""Tests for italianollama.api.middleware.logging module."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from italianollama.api.middleware.logging import (
    LoggingMiddleware,
    StructuredLoggingMiddleware,
)


def make_app_with_middleware(middleware_class, **kwargs):
    app = FastAPI()
    app.add_middleware(middleware_class, **kwargs)

    @app.get("/test")
    async def test_endpoint():
        return {"result": "ok"}

    @app.get("/error")
    async def error_endpoint():
        raise RuntimeError("test error")

    return app


class TestLoggingMiddleware:
    def test_adds_request_id_header(self):
        app = make_app_with_middleware(LoggingMiddleware)
        client = TestClient(app)
        resp = client.get("/test")
        assert resp.status_code == 200
        # Header name is case-insensitive
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        assert "x-request-id" in headers_lower

    def test_request_id_is_uuid_like(self):
        app = make_app_with_middleware(LoggingMiddleware)
        client = TestClient(app)
        resp = client.get("/test")
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        req_id = headers_lower.get("x-request-id")
        assert req_id is not None
        assert len(req_id) > 10

    def test_each_request_unique_id(self):
        app = make_app_with_middleware(LoggingMiddleware)
        client = TestClient(app)
        r1 = client.get("/test")
        r2 = client.get("/test")
        h1 = {k.lower(): v for k, v in r1.headers.items()}
        h2 = {k.lower(): v for k, v in r2.headers.items()}
        assert h1["x-request-id"] != h2["x-request-id"]

    def test_logs_request(self, caplog):
        import logging
        app = make_app_with_middleware(LoggingMiddleware)
        client = TestClient(app)
        with caplog.at_level(logging.INFO, logger="italian_tutor"):
            client.get("/test")
        assert any(
            "REQUEST" in r.message or "RESPONSE" in r.message
            for r in caplog.records
        )

    def test_error_raises(self):
        app = make_app_with_middleware(LoggingMiddleware)
        client = TestClient(app, raise_server_exceptions=True)
        with pytest.raises(RuntimeError):
            client.get("/error")

    def test_custom_logger_name(self):
        app = make_app_with_middleware(LoggingMiddleware, logger_name="custom_logger")
        client = TestClient(app)
        resp = client.get("/test")
        assert resp.status_code == 200

    def test_response_status_logged(self, caplog):
        import logging
        app = make_app_with_middleware(LoggingMiddleware)
        client = TestClient(app)
        with caplog.at_level(logging.INFO, logger="italian_tutor"):
            client.get("/test")
        messages = " ".join(r.message for r in caplog.records)
        assert "200" in messages or "RESPONSE" in messages


class TestStructuredLoggingMiddleware:
    def test_adds_request_id_header(self):
        app = make_app_with_middleware(StructuredLoggingMiddleware)
        client = TestClient(app)
        resp = client.get("/test")
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        assert "x-request-id" in headers_lower

    def test_logs_json(self, caplog):
        import logging
        app = make_app_with_middleware(StructuredLoggingMiddleware)
        client = TestClient(app)
        with caplog.at_level(logging.INFO, logger="italian_tutor.structured"):
            client.get("/test")
        json_logs = [r.message for r in caplog.records if r.name == "italian_tutor.structured"]
        if json_logs:
            parsed = json.loads(json_logs[0])
            assert "event" in parsed
            assert "request_id" in parsed

    def test_error_raises(self):
        app = make_app_with_middleware(StructuredLoggingMiddleware)
        client = TestClient(app, raise_server_exceptions=True)
        with pytest.raises(RuntimeError):
            client.get("/error")

    def test_unique_request_ids(self):
        app = make_app_with_middleware(StructuredLoggingMiddleware)
        client = TestClient(app)
        r1 = client.get("/test")
        r2 = client.get("/test")
        h1 = {k.lower(): v for k, v in r1.headers.items()}
        h2 = {k.lower(): v for k, v in r2.headers.items()}
        assert h1["x-request-id"] != h2["x-request-id"]
