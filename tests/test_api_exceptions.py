"""Tests for italianollama.api.exceptions module."""
import pytest

from italianollama.api.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    TutorException,
    ValidationError,
)


class TestTutorException:
    def test_basic_creation(self):
        exc = TutorException(status_code=400, detail="test error")
        assert exc.status_code == 400
        assert isinstance(exc.detail, dict)
        assert exc.detail["message"] == "test error"
        assert "trace_id" in exc.detail
        assert exc.detail["error"] == "TutorException"

    def test_with_error_type(self):
        exc = TutorException(status_code=400, detail="test", error_type="custom_error")
        assert exc.error_type == "custom_error"
        assert exc.detail["error"] == "custom_error"

    def test_with_trace_id(self):
        exc = TutorException(status_code=400, detail="test", trace_id="test-trace-123")
        assert exc.trace_id == "test-trace-123"
        assert exc.detail["trace_id"] == "test-trace-123"

    def test_auto_trace_id(self):
        exc = TutorException(status_code=400, detail="test")
        assert exc.trace_id is not None
        assert len(exc.trace_id) > 0

    def test_trace_ids_are_unique(self):
        exc1 = TutorException(status_code=400, detail="test")
        exc2 = TutorException(status_code=400, detail="test")
        assert exc1.trace_id != exc2.trace_id


class TestValidationError:
    def test_status_code(self):
        exc = ValidationError(detail="invalid input")
        assert exc.status_code == 400

    def test_error_type(self):
        exc = ValidationError(detail="invalid input")
        assert exc.error_type == "validation_error"

    def test_message(self):
        exc = ValidationError(detail="field required")
        assert exc.detail["message"] == "field required"

    def test_with_trace_id(self):
        exc = ValidationError(detail="bad", trace_id="trace-123")
        assert exc.trace_id == "trace-123"


class TestAuthenticationError:
    def test_default_message(self):
        exc = AuthenticationError()
        assert exc.status_code == 401
        detail_msg = exc.detail["message"].lower()
        assert "credentials" in detail_msg or "invalid" in detail_msg or "missing" in detail_msg

    def test_custom_message(self):
        exc = AuthenticationError(detail="Token expired")
        assert exc.detail["message"] == "Token expired"

    def test_error_type(self):
        exc = AuthenticationError()
        assert exc.error_type == "authentication_error"


class TestAuthorizationError:
    def test_status_code(self):
        exc = AuthorizationError()
        assert exc.status_code == 403

    def test_default_message(self):
        exc = AuthorizationError()
        detail_msg = exc.detail["message"].lower()
        assert "permission" in detail_msg or "insufficient" in detail_msg

    def test_error_type(self):
        exc = AuthorizationError()
        assert exc.error_type == "authorization_error"

    def test_custom_message(self):
        exc = AuthorizationError(detail="No access to resource")
        assert exc.detail["message"] == "No access to resource"


class TestNotFoundError:
    def test_auto_message(self):
        exc = NotFoundError(resource="Student")
        assert exc.status_code == 404
        assert "Student" in exc.detail["message"]
        assert "not found" in exc.detail["message"].lower()

    def test_custom_detail(self):
        exc = NotFoundError(resource="Student", detail="Student 123 does not exist")
        assert exc.detail["message"] == "Student 123 does not exist"

    def test_error_type(self):
        exc = NotFoundError(resource="Exercise")
        assert exc.error_type == "not_found_error"


class TestConflictError:
    def test_status_code(self):
        exc = ConflictError(detail="Resource already exists")
        assert exc.status_code == 409

    def test_error_type(self):
        exc = ConflictError(detail="Duplicate")
        assert exc.error_type == "conflict_error"

    def test_message(self):
        exc = ConflictError(detail="already exists")
        assert exc.detail["message"] == "already exists"


class TestRateLimitError:
    def test_status_code(self):
        exc = RateLimitError()
        assert exc.status_code == 429

    def test_default_message(self):
        exc = RateLimitError()
        detail_msg = exc.detail["message"].lower()
        assert "rate" in detail_msg or "limit" in detail_msg

    def test_error_type(self):
        exc = RateLimitError()
        assert exc.error_type == "rate_limit_error"

    def test_custom_message(self):
        exc = RateLimitError(detail="Too many requests")
        assert exc.detail["message"] == "Too many requests"


class TestServiceUnavailableError:
    def test_auto_message(self):
        exc = ServiceUnavailableError(service="Neo4j")
        assert exc.status_code == 503
        assert "Neo4j" in exc.detail["message"]

    def test_custom_detail(self):
        exc = ServiceUnavailableError(service="LLM", detail="LLM is down for maintenance")
        assert exc.detail["message"] == "LLM is down for maintenance"

    def test_error_type(self):
        exc = ServiceUnavailableError(service="DB")
        assert exc.error_type == "service_unavailable_error"


class TestInternalServerError:
    def test_status_code(self):
        exc = InternalServerError(detail="Unexpected error")
        assert exc.status_code == 500

    def test_error_type(self):
        exc = InternalServerError(detail="crash")
        assert exc.error_type == "internal_server_error"

    def test_message(self):
        exc = InternalServerError(detail="Database crashed")
        assert exc.detail["message"] == "Database crashed"
