"""Unit tests for metrics middleware."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import time

from italianollama.api.middleware.metrics import (
    PrometheusMetrics,
    MetricsMiddleware,
    _metrics,
)


class TestPrometheusMetrics:
    """Tests for PrometheusMetrics class."""

    def test_record_http_request(self):
        """Test recording HTTP requests."""
        metrics = PrometheusMetrics()
        
        metrics.record_http_request("/health", "GET", 200, 10.5)
        
        assert "/health" in metrics.http_request_count
        assert 200 in metrics.http_request_count["/health"]
        assert metrics.http_request_count["/health"][200] == 1

    def test_record_http_request_multiple(self):
        """Test recording multiple HTTP requests."""
        metrics = PrometheusMetrics()
        
        metrics.record_http_request("/health", "GET", 200, 10.0)
        metrics.record_http_request("/health", "GET", 200, 20.0)
        metrics.record_http_request("/health", "GET", 404, 5.0)
        
        assert metrics.http_request_count["/health"][200] == 2
        assert metrics.http_request_count["/health"][404] == 1

    def test_record_error(self):
        """Test recording errors."""
        metrics = PrometheusMetrics()
        
        metrics.record_error("/api/test", "ValueError")
        metrics.record_error("/api/test", "ValueError")
        metrics.record_error("/api/test", "KeyError")
        
        assert metrics.http_error_count["/api/test"]["ValueError"] == 2
        assert metrics.http_error_count["/api/test"]["KeyError"] == 1

    def test_record_llm_request(self):
        """Test recording LLM requests."""
        metrics = PrometheusMetrics()
        
        metrics.record_llm_request(100.0)
        metrics.record_llm_request(150.0)
        
        assert metrics.llm_request_count["total"] == 2
        assert len(metrics.llm_request_duration) == 2

    def test_record_neo4j_query(self):
        """Test recording Neo4j queries."""
        metrics = PrometheusMetrics()
        
        metrics.record_neo4j_query("get_student", 50.0)
        metrics.record_neo4j_query("get_student", 30.0)
        metrics.record_neo4j_query("create_student", 100.0)
        
        assert metrics.neo4j_query_count["total"] == 3
        assert metrics.neo4j_query_count["get_student"] == 2
        assert metrics.neo4j_query_count["create_student"] == 1

    def test_normalize_path_uuid(self):
        """Test path normalization removes UUIDs."""
        metrics = PrometheusMetrics()
        
        path = "/students/123e4567-e89b-12d3-a456-426614174000"
        normalized = metrics._normalize_path(path)
        
        assert "123e4567" not in normalized
        assert "{id}" in normalized

    def test_normalize_path_numeric(self):
        """Test path normalization removes numeric IDs."""
        metrics = PrometheusMetrics()
        
        path = "/students/123/analytics"
        normalized = metrics._normalize_path(path)
        
        assert "/123/" not in normalized
        assert "/{id}/" in normalized

    def test_get_metrics_text(self):
        """Test metrics text generation."""
        metrics = PrometheusMetrics()
        
        metrics.record_http_request("/health", "GET", 200, 10.0)
        
        text = metrics.get_metrics_text()
        
        assert "http_request_total" in text
        assert "/health" in text
        assert "200" in text


class TestMetricsMiddleware:
    """Tests for MetricsMiddleware."""

    @pytest.mark.asyncio
    async def test_metrics_middleware_basic(self):
        """Test basic metrics middleware."""
        mock_app = MagicMock()
        middleware = MetricsMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.method = "GET"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        async def mock_call_next(request):
            return mock_response
        
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_metrics_middleware_records_metrics(self):
        """Test middleware records metrics."""
        mock_app = MagicMock()
        middleware = MetricsMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.url.path = "/api/test"
        mock_request.method = "POST"
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        
        async def mock_call_next(request):
            return mock_response
        
        # Clear any existing metrics
        middleware.metrics.http_request_count = {}
        
        await middleware.dispatch(mock_request, mock_call_next)
        
        # Check metrics were recorded
        assert "/api/test" in middleware.metrics.http_request_count

    @pytest.mark.asyncio
    async def test_metrics_middleware_records_error(self):
        """Test middleware records errors."""
        mock_app = MagicMock()
        middleware = MetricsMiddleware(mock_app)
        
        mock_request = MagicMock()
        mock_request.url.path = "/api/test"
        mock_request.method = "GET"
        
        async def mock_call_next(request):
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await middleware.dispatch(mock_request, mock_call_next)
        
        # Check error was recorded
        assert "/api/test" in middleware.metrics.http_error_count
