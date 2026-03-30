"""Unit tests for API configuration."""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from italianollama.api.config import (
    Settings,
    get_settings,
    get_log_level,
)


class TestSettings:
    """Tests for Settings class."""

    def test_settings_with_explicit_env(self):
        """Test Settings with explicit environment variables."""
        env = {
            "neo4j_uri": "bolt://custom:7687",
            "neo4j_user": "custom_user",
            "neo4j_password": "secret123",
            "litellm_model": "gpt-4",
            "log_level": "DEBUG",
        }
        with patch.dict("os.environ", env, clear=True):
            settings = Settings()
            assert settings.neo4j_uri == "bolt://custom:7687"
            assert settings.neo4j_user == "custom_user"
            assert settings.litellm_model == "gpt-4"

    def test_settings_minimal_env(self):
        """Test Settings with minimal environment."""
        # Only set required vars
        env = {
            "neo4j_password": "test123",
        }
        with patch.dict("os.environ", env, clear=True):
            settings = Settings()
            assert settings.neo4j_user == "neo4j"
            assert settings.litellm_base_url == "http://litellm:4000"
            assert settings.auth_secret == "dev-secret-key-do-not-use-in-production"
            assert settings.jwt_algorithm == "HS256"

    def test_settings_cors_origins(self):
        """Test CORS origins default."""
        env = {"neo4j_password": "test"}
        with patch.dict("os.environ", env, clear=True):
            settings = Settings()
            assert "http://localhost:3000" in settings.cors_origins
            assert "http://localhost:8000" in settings.cors_origins


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test get_settings returns cached instance."""
        import italianollama.api.config as config_module
        config_module._settings = None  # Reset
        
        with patch("italianollama.api.config.Settings"):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2

    def test_get_settings_caches(self):
        """Test settings are cached after first call."""
        import italianollama.api.config as config_module
        config_module._settings = None
        
        with patch("italianollama.api.config.Settings") as mock_settings:
            mock_instance = MagicMock()
            mock_settings.return_value = mock_instance
            
            result1 = get_settings()
            result2 = get_settings()
            
            # Should only call Settings() once
            assert mock_settings.call_count == 1


class TestGetLogLevel:
    """Tests for get_log_level function."""

    def test_get_log_level_returns_int(self):
        """Test get_log_level returns integer logging level."""
        import italianollama.api.config as config_module
        config_module._settings = None
        
        with patch("italianollama.api.config.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.log_level = "INFO"
            mock_get_settings.return_value = mock_settings
            
            level = get_log_level()
            assert level == 20  # logging.INFO
