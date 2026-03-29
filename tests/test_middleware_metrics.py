"""Tests for italianollama.api.middleware.metrics module."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from italianollama.api.middleware.metrics import (
    MetricsMiddleware,
    PrometheusMetrics,
    setup_metrics,
)


class TestPrometheusMetrics:
    def test_initial_state(self):
        m = PrometheusMetrics()
        assert m.http_request_count == {}
        assert m.http_request_duration == {}
        assert m.active_connections == 0
        assert m.llm_request_count == {"total": 0}

    def test_record_http_request(self):
        m = PrometheusMetrics()
        m.record_http_request("/test", "GET", 200, 50.0)
        assert "/test" in m.http_request_count
        assert 200 in m.http_request_count["/test"]
        assert m.http_request_count["/test"][200] == 1

    def test_record_http_request_multiple(self):
        m = PrometheusMetrics()
        m.record_http_request("/test", "GET", 200, 50.0)
        m.record_http_request("/test", "GET", 200, 60.0)
        assert m.http_request_count["/test"][200] == 2
        assert len(m.http_request_duration["/test"]) == 2

    def test_normalize_path_uuid(self):
        m = PrometheusMetrics()
        path = "/students/123e4567-e89b-12d3-a456-426614174000"
        normalized = m._normalize_path(path)
        assert "{id}" in normalized

    def test_normalize_path_numeric(self):
        m = PrometheusMetrics()
        normalized = m._normalize_path("/students/123")
        assert "{id}" in normalized

    def test_normalize_path_no_id(self):
        m = PrometheusMetrics()
        normalized = m._normalize_path("/health")
        assert normalized == "/health"

    def test_record_error(self):
        m = PrometheusMetrics()
        m.record_error("/test", "ValueError")
        assert "/test" in m.http_error_count
        assert "ValueError" in m.http_error_count["/test"]

    def test_record_llm_request(self):
        m = PrometheusMetrics()
        m.record_llm_request(100.0)
        assert m.llm_request_count["total"] == 1
        assert 100.0 in m.llm_request_duration

    def test_record_neo4j_query(self):
        m = PrometheusMetrics()
        m.record_neo4j_query("read", 25.0)
        assert m.neo4j_query_count["total"] == 1
        assert m.neo4j_query_count["read"] == 1

    def test_get_metrics_text_basic(self):
        m = PrometheusMetrics()
        text = m.get_metrics_text()
        assert "http_request_total" in text
        assert "llm_request_total" in text
        assert "neo4j_query_total" in text
        assert "active_connections" in text

    def test_get_metrics_text_with_data(self):
        m = PrometheusMetrics()
        m.record_http_request("/test", "GET", 200, 50.0)
        m.record_llm_request(100.0)
        m.record_neo4j_query("read", 25.0)
        text = m.get_metrics_text()
        assert "/test" in text
        assert "avg" in text

    def test_duration_trimmed_at_100(self):
        m = PrometheusMetrics()
        for i in range(150):
            m.record_http_request("/test", "GET", 200, float(i))
        assert len(m.http_request_duration["/test"]) == 100

    def test_llm_duration_trimmed_at_100(self):
        m = PrometheusMetrics()
        for i in range(150):
            m.record_llm_request(float(i))
        assert len(m.llm_request_duration) == 100

    def test_neo4j_duration_trimmed_at_100(self):
        m = PrometheusMetrics()
        for i in range(150):
            m.record_neo4j_query("read", float(i))
        assert len(m.neo4j_query_duration) == 100

    def test_get_metrics_text_with_errors(self):
        m = PrometheusMetrics()
        m.record_error("/test", "ValueError")
        text = m.get_metrics_text()
        assert "http_error_total" in text

    def test_get_metrics_text_with_neo4j(self):
        m = PrometheusMetrics()
        m.record_neo4j_query("read", 10.0)
        m.record_neo4j_query("write", 20.0)
        text = m.get_metrics_text()
        assert "neo4j_query_duration_ms" in text

    def test_record_error_multiple_types(self):
        m = PrometheusMetrics()
        m.record_error("/api", "ValueError")
        m.record_error("/api", "TypeError")
        m.record_error("/api", "ValueError")
        assert m.http_error_count["/api"]["ValueError"] == 2
        assert m.http_error_count["/api"]["TypeError"] == 1

    def test_record_neo4j_multiple_types(self):
        m = PrometheusMetrics()
        m.record_neo4j_query("read", 10.0)
        m.record_neo4j_query("write", 20.0)
        m.record_neo4j_query("read", 15.0)
        assert m.neo4j_query_count["total"] == 3
        assert m.neo4j_query_count["read"] == 2
        assert m.neo4j_query_count["write"] == 1


class TestMetricsMiddleware:
    def test_middleware_records_requests(self):
        app = FastAPI()
        app.add_middleware(MetricsMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"ok": True}

        client = TestClient(app)
        resp = client.get("/test")
        assert resp.status_code == 200

    def test_setup_metrics(self):
        app = FastAPI()
        setup_metrics(app)

        client = TestClient(app)
        resp = client.get("/metrics")
        assert resp.status_code == 200
        assert "http_request_total" in resp.text

    def test_setup_metrics_content_type(self):
        app = FastAPI()
        setup_metrics(app)

        client = TestClient(app)
        resp = client.get("/metrics")
        assert "text/plain" in resp.headers.get("content-type", "")
