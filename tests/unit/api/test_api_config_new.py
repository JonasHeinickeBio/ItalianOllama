"""Unit tests for API configuration module."""

import pytest
from unittest.mock import patch, MagicMock
import os

from italianollama.api.config import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_settings_defaults(self):
        """Test Settings with default values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.neo4j_uri == "bolt://localhost:7687"
            assert settings.neo4j_user == "neo4j"
            assert settings.neo4j_password == "password"
            assert settings.neo4j_database == "neo4j"

    def test_settings_from_environment(self):
        """Test Settings from environment variables."""
        env = {
            "NEO4J_URI": "neo4j+s://test.databases.neo4j.io",
            "NEO4J_USER": "testuser",
            "NEO4J_PASSWORD": "testpass",
            "NEO4J_DATABASE": "testdb",
            "LITELLM_BASE_URL": "http://test:4000",
            "AUTH_SECRET": "test-secret",
            "JWT_EXPIRATION_HOURS": "8",
            "LOG_LEVEL": "DEBUG",
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:8000",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.neo4j_uri == "neo4j+s://test.databases.neo4j.io"
            assert settings.neo4j_user == "testuser"
            assert settings.neo4j_password == "testpass"
            assert settings.neo4j_database == "testdb"
            assert settings.litellm_base_url == "http://test:4000"
            assert settings.auth_secret == "test-secret"
            assert settings.jwt_expiration_hours == 8
            assert settings.log_level == "DEBUG"

    def test_settings_cors_origins(self):
        """Test CORS origins configuration."""
        env = {
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:8000,http://localhost:8501",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert "http://localhost:3000" in settings.cors_origins
            assert "http://localhost:8000" in settings.cors_origins
            assert "http://localhost:8501" in settings.cors_origins

    def test_settings_litellm_defaults(self):
        """Test LiteLLM default settings."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.litellm_base_url == "http://litellm:4000"
            assert settings.litellm_api_key == "dummy"
            assert settings.litellm_model == "tutor"
            assert settings.litellm_timeout == 120

    def test_settings_auth_defaults(self):
        """Test authentication default settings."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.auth_secret == "dev-secret-key-do-not-use-in-production"
            assert settings.jwt_algorithm == "HS256"
            assert settings.jwt_expiration_hours == 4

    def test_settings_logging_defaults(self):
        """Test logging default settings."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.log_level == "INFO"
            assert settings.log_format == "text"

    def test_settings_runtime_options(self):
        """Test runtime configuration options."""
        env = {
            "USE_AURA": "true",
            "SENTRY_DSN": "https://example.sentry.io/123",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.use_aura is True
            assert settings.sentry_dsn == "https://example.sentry.io/123"

    def test_settings_blablador_config(self):
        """Test Blablador API configuration."""
        env = {
            "BLABLADOR_API_URL": "https://api.blablador.de",
            "BLABLADOR_API_KEY": "test-key",
            "BLABLADOR_MODEL": "alias-fast",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings()
            assert settings.blablador_api_url == "https://api.blablador.de"
            assert settings.blablador_api_key == "test-key"
            assert settings.blablador_model == "alias-fast"


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test get_settings returns same instance."""
        with patch.dict(os.environ, {}, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2

    def test_get_settings_caches(self):
        """Test get_settings caches the instance."""
        with patch.dict(os.environ, {}, clear=True):
            # First call should create settings
            settings1 = get_settings()
            # Second call should return cached
            settings2 = get_settings()
            assert settings1 is settings2


class TestGetLogLevel:
    """Tests for get_log_level function."""

    def test_get_log_level_info(self):
        """Test get_log_level returns correct level."""
        import logging
        with patch.dict(os.environ, {"LOG_LEVEL": "INFO"}, clear=True):
            # Clear cached settings
            import italianollama.api.config as config_module
            config_module._settings = None
            
            from italianollama.api.config import get_log_level
            level = get_log_level()
            assert level == logging.INFO

    def test_get_log_level_debug(self):
        """Test get_log_level returns DEBUG."""
        import logging
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=True):
            import italianollama.api.config as config_module
            config_module._settings = None
            
            from italianollama.api.config import get_log_level
            level = get_log_level()
            assert level == logging.DEBUG
