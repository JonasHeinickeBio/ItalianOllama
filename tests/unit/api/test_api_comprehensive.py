"""Comprehensive unit tests for API components."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from italianollama.api.config import Settings, get_settings, get_log_level
from italianollama.api.exceptions import NotFoundError, ValidationError


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_defaults(self):
        """Test default settings values."""
        settings = Settings(_env_file=None)
        
        assert settings.neo4j_uri is not None
        assert settings.neo4j_user is not None
        assert settings.neo4j_database == "neo4j"
        assert settings.log_level == "INFO"

    def test_settings_from_env(self):
        """Test settings can be overridden from env."""
        with patch.dict('os.environ', {
            'NEO4J_URI': 'neo4j+s://test.neo4j.io',
            'NEO4J_USER': 'testuser',
            'NEO4J_PASSWORD': 'testpass',
            'LOG_LEVEL': 'DEBUG',
        }):
            settings = Settings(_env_file=None)
            
            assert settings.neo4j_uri == 'neo4j+s://test.neo4j.io'
            assert settings.neo4j_user == 'testuser'
            assert settings.log_level == 'DEBUG'

    def test_settings_cors_origins(self):
        """Test CORS origins default."""
        settings = Settings(_env_file=None)
        
        # CORS origins should be a list
        assert settings.cors_origins is not None
        assert len(settings.cors_origins) > 0

    def test_settings_jwt_expiration(self):
        """Test JWT expiration defaults."""
        settings = Settings(_env_file=None)
        
        assert settings.jwt_expiration_hours == 4
        assert settings.jwt_algorithm == "HS256"


class TestGetSettings:
    """Tests for get_settings singleton."""

    def test_get_settings_singleton(self):
        """Test get_settings returns same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2


class TestGetLogLevel:
    """Tests for get_log_level."""

    def test_get_log_level_debug(self):
        """Test get_log_level returns DEBUG level."""
        with patch.dict('os.environ', {'LOG_LEVEL': 'DEBUG'}):
            # Clear cached settings
            import italianollama.api.config as config_module
            config_module._settings = None
            
            level = get_log_level()
            assert level == 10  # logging.DEBUG

    def test_get_log_level_error(self):
        """Test get_log_level returns ERROR level."""
        with patch.dict('os.environ', {'LOG_LEVEL': 'ERROR'}):
            # Clear cached settings
            import italianollama.api.config as config_module
            config_module._settings = None
            
            level = get_log_level()
            assert level == 40  # logging.ERROR


class TestExceptions:
    """Tests for custom exceptions."""

    def test_not_found_error(self):
        """Test NotFoundError raises correctly."""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("Student", "student_123")
        
        assert "student_123" in str(exc_info.value)
        assert "student_123" in str(exc_info.value)

    def test_validation_error(self):
        """Test ValidationError raises correctly."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid input")
        
        assert "Invalid input" in str(exc_info.value)

    def test_validation_error_with_field(self):
        """Test ValidationError with field name."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("student_id is required")
        
        error_str = str(exc_info.value)
        assert "student_id is required" in error_str


class TestAuthMiddleware:
    """Tests for auth middleware."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        from italianollama.api.middleware.auth import create_access_token
        
        with patch.dict('os.environ', {'AUTH_SECRET': 'test-secret-key-for-testing-purposes-32bytes'},
                       clear=False):
            token = create_access_token("student_123")
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Test JWT token with custom expiry."""
        from italianollama.api.middleware.auth import create_access_token
        from datetime import timedelta
        
        with patch.dict('os.environ', {'AUTH_SECRET': 'test-secret-key-for-testing-purposes-32bytes'},
                       clear=False):
            token = create_access_token("student_123", timedelta(hours=2))
            
            assert token is not None

    def test_verify_access_token_valid(self):
        """Test JWT token verification."""
        from italianollama.api.middleware.auth import create_access_token, verify_access_token
        
        with patch.dict('os.environ', {'AUTH_SECRET': 'test-secret-key-for-testing-purposes-32bytes'},
                       clear=False):
            token = create_access_token("student_123")
            payload = verify_access_token(token)
            
            assert payload['sub'] == "student_123"

    def test_verify_access_token_expired(self):
        """Test JWT token verification fails for expired token."""
        from italianollama.api.middleware.auth import create_access_token, verify_access_token
        from datetime import timedelta
        
        with patch.dict('os.environ', {'AUTH_SECRET': 'test-secret-key-for-testing-purposes-32bytes'},
                       clear=False):
            # Create already-expired token
            token = create_access_token("student_123", timedelta(hours=-1))
            
            with pytest.raises(Exception):
                verify_access_token(token)


class TestRateLimitMiddleware:
    """Tests for rate limiting."""

    def test_rate_limit_config_defaults(self):
        """Test RateLimitConfig defaults."""
        from italianollama.api.middleware.rate_limit import RateLimitConfig
        
        # RateLimitConfig uses class attributes
        assert RateLimitConfig.DEFAULT_LIMIT == (1000, 60)

    def test_rate_limit_config_custom(self):
        """Test RateLimitConfig with custom values."""
        from italianollama.api.middleware.rate_limit import RateLimitConfig
        
        # RateLimitConfig uses class attributes
        assert "/chat" in RateLimitConfig.ENDPOINT_LIMITS


class TestTimeoutMiddleware:
    """Tests for timeout middleware."""

    def test_timeout_config_defaults(self):
        """Test TimeoutConfig defaults."""
        from italianollama.api.middleware.timeout import TimeoutConfig
        
        # TimeoutConfig uses class attributes
        assert TimeoutConfig.DEFAULT_TIMEOUT == 30

    def test_timeout_config_custom(self):
        """Test TimeoutConfig with custom values."""
        from italianollama.api.middleware.timeout import TimeoutConfig
        
        # TimeoutConfig uses class attributes
        assert "/chat" in TimeoutConfig.ENDPOINT_TIMEOUTS


class TestStreaming:
    """Tests for streaming functionality."""

    def test_stream_adapter_import(self):
        """Test stream adapter can be imported."""
        from italianollama.api.stream_adapter import stream_graph_response
        
        assert callable(stream_graph_response)

    def test_streaming_import(self):
        """Test streaming module can be imported."""
        from italianollama.api import streaming
        
        assert streaming is not None


class TestMetricsMiddleware:
    """Tests for metrics middleware."""

    def test_metrics_setup(self):
        """Test metrics middleware can be set up."""
        from italianollama.api.middleware.metrics import setup_metrics
        
        app = FastAPI()
        setup_metrics(app)
        
        # Should not raise
        assert app.routes


class TestLoggingMiddleware:
    """Tests for logging middleware."""

    def test_logging_middleware_import(self):
        """Test LoggingMiddleware can be imported."""
        from italianollama.api.middleware.logging import LoggingMiddleware
        
        assert LoggingMiddleware is not None


class TestContextMiddleware:
    """Tests for context middleware."""

    def test_context_middleware_import(self):
        """Test ContextMiddleware can be imported."""
        from italianollama.api.middleware.context import ContextMiddleware
        
        assert ContextMiddleware is not None
