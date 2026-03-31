"""Unit tests for API exceptions."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from italianollama.api.exceptions import (
    TutorException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServiceUnavailableError,
    InternalServerError,
)


class TestTutorException:
    """Tests for base TutorException class."""

    def test_tutor_exception_init(self):
        """Test TutorException initializes with trace_id."""
        exc = TutorException(status_code=400, detail="Test error")
        assert exc.status_code == 400
        assert exc.trace_id is not None
        assert exc.error_type == "TutorException"

    def test_tutor_exception_with_custom_trace_id(self):
        """Test TutorException accepts custom trace_id."""
        exc = TutorException(
            status_code=400,
            detail="Test error",
            trace_id="custom-trace-123"
        )
        assert exc.trace_id == "custom-trace-123"

    def test_tutor_exception_detail_format(self):
        """Test TutorException detail includes trace_id."""
        exc = TutorException(status_code=400, detail="Test error")
        detail = exc.detail
        assert isinstance(detail, dict)
        assert "error" in detail
        assert "message" in detail
        assert "trace_id" in detail


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_status_code(self):
        """Test ValidationError has 400 status code."""
        exc = ValidationError(detail="Invalid input")
        assert exc.status_code == 400
        assert exc.error_type == "validation_error"

    def test_validation_error_message(self):
        """Test ValidationError message format."""
        exc = ValidationError(detail="Missing field")
        assert "Missing field" in exc.detail["message"]


class TestAuthenticationError:
    """Tests for AuthenticationError exception."""

    def test_authentication_error_default_message(self):
        """Test AuthenticationError default message."""
        exc = AuthenticationError()
        assert exc.status_code == 401
        assert "credentials" in exc.detail["message"].lower()

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError custom message."""
        exc = AuthenticationError(detail="Token expired")
        assert exc.status_code == 401
        assert "Token expired" in exc.detail["message"]


class TestAuthorizationError:
    """Tests for AuthorizationError exception."""

    def test_authorization_error_default_message(self):
        """Test AuthorizationError default message."""
        exc = AuthorizationError()
        assert exc.status_code == 403
        assert "permission" in exc.detail["message"].lower()


class TestNotFoundError:
    """Tests for NotFoundError exception."""

    def test_not_found_error_resource(self):
        """Test NotFoundError includes resource name."""
        exc = NotFoundError(resource="Student")
        assert exc.status_code == 404
        assert "Student" in exc.detail["message"]
        assert "not found" in exc.detail["message"].lower()

    def test_not_found_error_custom_detail(self):
        """Test NotFoundError with custom detail."""
        exc = NotFoundError(resource="Student", detail="ID does not exist")
        assert exc.detail["message"] == "ID does not exist"


class TestConflictError:
    """Tests for ConflictError exception."""

    def test_conflict_error_status_code(self):
        """Test ConflictError has 409 status code."""
        exc = ConflictError(detail="Resource already exists")
        assert exc.status_code == 409


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_rate_limit_error_default(self):
        """Test RateLimitError default message."""
        exc = RateLimitError()
        assert exc.status_code == 429
        assert "rate limit" in exc.detail["message"].lower()


class TestServiceUnavailableError:
    """Tests for ServiceUnavailableError exception."""

    def test_service_unavailable_default(self):
        """Test ServiceUnavailableError default."""
        exc = ServiceUnavailableError(service="Neo4j")
        assert exc.status_code == 503
        assert "Neo4j" in exc.detail["message"]
        assert "unavailable" in exc.detail["message"].lower()


class TestInternalServerError:
    """Tests for InternalServerError exception."""

    def test_internal_server_error_status_code(self):
        """Test InternalServerError has 500 status code."""
        exc = InternalServerError(detail="Unexpected error")
        assert exc.status_code == 500
        assert exc.error_type == "internal_server_error"
