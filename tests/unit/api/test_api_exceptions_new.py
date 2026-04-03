"""Unit tests for API exceptions module."""

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

    def test_tutor_exception_basic(self):
        """Test basic TutorException initialization."""
        exc = TutorException(status_code=500, detail="Test error")
        assert exc.status_code == 500
        assert "Test error" in exc.detail["message"]
        assert exc.trace_id is not None
        assert exc.error_type == "TutorException"

    def test_tutor_exception_with_trace_id(self):
        """Test TutorException with custom trace_id."""
        exc = TutorException(
            status_code=400,
            detail="Custom error",
            trace_id="test-trace-123"
        )
        assert exc.trace_id == "test-trace-123"

    def test_tutor_exception_with_error_type(self):
        """Test TutorException with custom error type."""
        exc = TutorException(
            status_code=500,
            detail="Error",
            error_type="custom_error"
        )
        assert exc.error_type == "custom_error"


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_defaults(self):
        """Test ValidationError with defaults."""
        exc = ValidationError("Invalid input")
        assert exc.status_code == 400
        assert exc.error_type == "validation_error"
        assert "Invalid input" in exc.detail["message"]

    def test_validation_error_with_trace_id(self):
        """Test ValidationError with custom trace_id."""
        exc = ValidationError("Invalid input", trace_id="val-123")
        assert exc.trace_id == "val-123"

    def test_validation_error_is_http_exception(self):
        """Test ValidationError is HTTPException."""
        exc = ValidationError("Test")
        assert isinstance(exc, HTTPException)


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_authentication_error_defaults(self):
        """Test AuthenticationError with defaults."""
        exc = AuthenticationError()
        assert exc.status_code == 401
        assert exc.error_type == "authentication_error"

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        exc = AuthenticationError("Token expired")
        assert "Token expired" in exc.detail["message"]

    def test_authentication_error_with_trace_id(self):
        """Test AuthenticationError with trace_id."""
        exc = AuthenticationError("Invalid", trace_id="auth-123")
        assert exc.trace_id == "auth-123"


class TestAuthorizationError:
    """Tests for AuthorizationError."""

    def test_authorization_error_defaults(self):
        """Test AuthorizationError with defaults."""
        exc = AuthorizationError()
        assert exc.status_code == 403
        assert exc.error_type == "authorization_error"

    def test_authorization_error_custom_message(self):
        """Test AuthorizationError with custom message."""
        exc = AuthorizationError("Access denied")
        assert "Access denied" in exc.detail["message"]


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_not_found_error_with_resource(self):
        """Test NotFoundError with resource."""
        exc = NotFoundError("Student")
        assert exc.status_code == 404
        assert exc.error_type == "not_found_error"
        assert "Student" in exc.detail["message"]

    def test_not_found_error_with_detail(self):
        """Test NotFoundError with custom detail."""
        exc = NotFoundError("Student", "Student john not found")
        assert "john" in exc.detail["message"]

    def test_not_found_error_auto_generates_detail(self):
        """Test NotFoundError auto-generates detail."""
        exc = NotFoundError("Course")
        assert "Course" in exc.detail["message"]


class TestConflictError:
    """Tests for ConflictError."""

    def test_conflict_error(self):
        """Test ConflictError."""
        exc = ConflictError("Resource already exists")
        assert exc.status_code == 409
        assert "already exists" in exc.detail["message"]


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_rate_limit_error_defaults(self):
        """Test RateLimitError with defaults."""
        exc = RateLimitError()
        assert exc.status_code == 429
        assert exc.error_type == "rate_limit_error"

    def test_rate_limit_error_custom_message(self):
        """Test RateLimitError with custom message."""
        exc = RateLimitError("Too many requests")
        assert "Too many requests" in exc.detail["message"]


class TestServiceUnavailableError:
    """Tests for ServiceUnavailableError."""

    def test_service_unavailable_error_defaults(self):
        """Test ServiceUnavailableError with defaults."""
        exc = ServiceUnavailableError("Neo4j")
        assert exc.status_code == 503
        assert exc.error_type == "service_unavailable_error"
        assert "Neo4j" in exc.detail["message"]

    def test_service_unavailable_error_with_detail(self):
        """Test ServiceUnavailableError with custom detail."""
        exc = ServiceUnavailableError("Neo4j", "Connection failed")
        assert "Connection failed" in exc.detail["message"]


class TestInternalServerError:
    """Tests for InternalServerError."""

    def test_internal_server_error(self):
        """Test InternalServerError."""
        exc = InternalServerError("Unexpected error")
        assert exc.status_code == 500
        assert "Unexpected" in exc.detail["message"]
        assert exc.error_type == "internal_server_error"


class TestExceptionInheritance:
    """Tests for exception inheritance."""

    def test_all_exceptions_inherit_from_http_exception(self):
        """All custom exceptions should inherit from HTTPException."""
        exceptions = [
            ValidationError("test"),
            AuthenticationError(),
            AuthorizationError(),
            NotFoundError("test"),
            ConflictError("test"),
            RateLimitError(),
            ServiceUnavailableError("test"),
            InternalServerError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, HTTPException)

    def test_all_exceptions_have_trace_id(self):
        """All exceptions should have trace_id."""
        exceptions = [
            ValidationError("test"),
            AuthenticationError(),
            AuthorizationError(),
            NotFoundError("test"),
            ConflictError("test"),
            RateLimitError(),
            ServiceUnavailableError("test"),
            InternalServerError("test"),
        ]
        for exc in exceptions:
            assert hasattr(exc, "trace_id")
            assert exc.trace_id is not None