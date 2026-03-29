"""Prometheus metrics collection middleware for Italian Tutor API.

Collects and exposes metrics for monitoring, alerting, and performance analysis.
"""

import logging
import re
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse, Response

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Prometheus metrics collection.

    Tracks HTTP metrics and application-specific metrics.
    """

    def __init__(self):
        # HTTP metrics: path -> {status -> count}
        self.http_request_count: dict[str, dict[int, int]] = {}
        self.http_request_duration: dict[str, list] = {}  # path -> [durations]
        self.http_error_count: dict[str, dict[str, int]] = {}  # path -> {error_type -> count}

        # Application metrics
        self.llm_request_count: dict[str, int] = {"total": 0}
        self.llm_request_duration: list = []  # [durations]
        self.neo4j_query_count: dict[str, int] = {"total": 0}
        self.neo4j_query_duration: list = []  # [durations]

        # Connection tracking
        self.active_connections = 0

    def record_http_request(
        self,
        path: str,
        method: str,
        status_code: int,
        duration_ms: float,
    ):
        """Record HTTP request metrics."""
        # Normalize path (remove IDs to group endpoints)
        normalized_path = self._normalize_path(path)

        # Request count
        if normalized_path not in self.http_request_count:
            self.http_request_count[normalized_path] = {}

        if status_code not in self.http_request_count[normalized_path]:
            self.http_request_count[normalized_path][status_code] = 0

        self.http_request_count[normalized_path][status_code] += 1

        # Duration tracking
        if normalized_path not in self.http_request_duration:
            self.http_request_duration[normalized_path] = []

        self.http_request_duration[normalized_path].append(duration_ms)

        # Keep only recent durations (last 100)
        if len(self.http_request_duration[normalized_path]) > 100:
            self.http_request_duration[normalized_path] = self.http_request_duration[
                normalized_path
            ][-100:]

    def record_error(
        self,
        path: str,
        error_type: str,
    ):
        """Record error metrics."""
        normalized_path = self._normalize_path(path)

        if normalized_path not in self.http_error_count:
            self.http_error_count[normalized_path] = {}

        if error_type not in self.http_error_count[normalized_path]:
            self.http_error_count[normalized_path][error_type] = 0

        self.http_error_count[normalized_path][error_type] += 1

    def record_llm_request(self, duration_ms: float):
        """Record LLM request metrics."""
        self.llm_request_count["total"] += 1
        self.llm_request_duration.append(duration_ms)

        # Keep only recent
        if len(self.llm_request_duration) > 100:
            self.llm_request_duration = self.llm_request_duration[-100:]

    def record_neo4j_query(self, query_type: str, duration_ms: float):
        """Record Neo4j query metrics."""
        self.neo4j_query_count["total"] += 1

        if query_type not in self.neo4j_query_count:
            self.neo4j_query_count[query_type] = 0

        self.neo4j_query_count[query_type] += 1
        self.neo4j_query_duration.append(duration_ms)

        # Keep only recent
        if len(self.neo4j_query_duration) > 100:
            self.neo4j_query_duration = self.neo4j_query_duration[-100:]

    def get_metrics_text(self) -> str:
        """Generate Prometheus-format metrics text."""
        lines = []

        # Header
        lines.append("# HELP http_request_total Total HTTP requests")
        lines.append("# TYPE http_request_total counter")

        # HTTP request counts
        for path, statuses in self.http_request_count.items():
            for status, count in statuses.items():
                lines.append(f'http_request_total{{path="{path}",status="{status}"}} {count}')

        # HTTP request duration
        lines.append("# HELP http_request_duration_ms HTTP request duration in milliseconds")
        lines.append("# TYPE http_request_duration_ms gauge")

        for path, durations in self.http_request_duration.items():
            if durations:
                avg = sum(durations) / len(durations)
                min_d = min(durations)
                max_d = max(durations)

                lines.append(f'http_request_duration_ms{{path="{path}",quantile="avg"}} {avg:.2f}')
                lines.append(
                    f'http_request_duration_ms{{path="{path}",quantile="min"}} {min_d:.2f}'
                )
                lines.append(
                    f'http_request_duration_ms{{path="{path}",quantile="max"}} {max_d:.2f}'
                )

        # Error counts
        if self.http_error_count:
            lines.append("# HELP http_error_total Total HTTP errors")
            lines.append("# TYPE http_error_total counter")

            for path, errors in self.http_error_count.items():
                for error_type, count in errors.items():
                    lines.append(f'http_error_total{{path="{path}",error="{error_type}"}} {count}')

        # LLM metrics
        lines.append("# HELP llm_request_total Total LLM requests")
        lines.append("# TYPE llm_request_total counter")
        lines.append(f"llm_request_total {self.llm_request_count['total']}")

        if self.llm_request_duration:
            lines.append("# HELP llm_request_duration_ms LLM request duration")
            lines.append("# TYPE llm_request_duration_ms gauge")

            avg = sum(self.llm_request_duration) / len(self.llm_request_duration)
            min_d = min(self.llm_request_duration)
            max_d = max(self.llm_request_duration)

            lines.append(f'llm_request_duration_ms{{quantile="avg"}} {avg:.2f}')
            lines.append(f'llm_request_duration_ms{{quantile="min"}} {min_d:.2f}')
            lines.append(f'llm_request_duration_ms{{quantile="max"}} {max_d:.2f}')

        # Neo4j metrics
        lines.append("# HELP neo4j_query_total Total Neo4j queries")
        lines.append("# TYPE neo4j_query_total counter")

        for query_type, count in self.neo4j_query_count.items():
            lines.append(f'neo4j_query_total{{type="{query_type}"}} {count}')

        if self.neo4j_query_duration:
            lines.append("# HELP neo4j_query_duration_ms Neo4j query duration")
            lines.append("# TYPE neo4j_query_duration_ms gauge")

            avg = sum(self.neo4j_query_duration) / len(self.neo4j_query_duration)
            min_d = min(self.neo4j_query_duration)
            max_d = max(self.neo4j_query_duration)

            lines.append(f'neo4j_query_duration_ms{{quantile="avg"}} {avg:.2f}')
            lines.append(f'neo4j_query_duration_ms{{quantile="min"}} {min_d:.2f}')
            lines.append(f'neo4j_query_duration_ms{{quantile="max"}} {max_d:.2f}')

        # Connection metrics
        lines.append("# HELP active_connections Current active connections")
        lines.append("# TYPE active_connections gauge")
        lines.append(f"active_connections {self.active_connections}")

        return "\n".join(lines) + "\n"

    def _normalize_path(self, path: str) -> str:
        """Normalize path for metrics grouping.

        Removes IDs to group similar endpoints together:
        /students/123 -> /students/{id}
        """
        # Remove UUIDs
        path = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "{id}", path
        )

        # Remove numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)

        return path


# Global metrics instance
_metrics = PrometheusMetrics()


class MetricsMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for Prometheus metrics collection."""

    def __init__(self, app):
        super().__init__(app)
        self.metrics = _metrics

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and collect metrics."""
        path = request.url.path
        method = request.method
        start_time = time.time()

        # Increment active connection counter
        self.metrics.active_connections += 1

        try:
            response = await call_next(request)
            return response

        except Exception as e:
            # Record error
            error_type = type(e).__name__
            self.metrics.record_error(path, error_type)
            raise

        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Record metrics
            try:
                status_code = getattr(response, "status_code", 500)
            except:
                status_code = 500

            self.metrics.record_http_request(path, method, status_code, duration_ms)
            self.metrics.active_connections -= 1

            logger.debug(f"Metrics: {method} {path} -> {status_code} ({duration_ms:.2f}ms)")


def setup_metrics(app):
    """Register metrics middleware and add /metrics endpoint."""
    app.add_middleware(MetricsMiddleware)

    @app.get("/metrics")
    async def metrics():
        """Return Prometheus-format metrics."""
        return PlainTextResponse(_metrics.get_metrics_text())

    logger.info("Metrics collection registered at /metrics")
