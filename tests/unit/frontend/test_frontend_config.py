"""Unit tests for frontend configuration."""

import pytest
from unittest.mock import patch, MagicMock
from italianollama.frontend.config import (
    Settings,
    get_settings,
)


class TestFrontendSettings:
    """Tests for frontend Settings class."""

    def test_settings_defaults(self):
        """Test Settings default values."""
        import os
        env = os.environ.copy()
        try:
            with patch.dict("os.environ", {
                "backend_url": "http://localhost:8000",
                "backend_timeout": "30.0",
                "default_student_id": "demo",
                "app_name": "Sofia – Italian Tutor",
            }, clear=True):
                settings = Settings()
                assert settings.backend_url == "http://localhost:8000"
                assert settings.backend_timeout == 30.0
                assert settings.default_student_id == "demo"
                assert settings.app_name == "Sofia – Italian Tutor"
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_settings_from_env(self):
        """Test Settings loads from environment variables."""
        env = {
            "backend_url": "http://custom:9000",
            "backend_timeout": "60.0",
            "default_student_id": "test_user",
            "app_name": "Custom App",
            "log_level": "DEBUG",
        }
        with patch.dict("os.environ", env, clear=True):
            settings = Settings()
            assert settings.backend_url == "http://custom:9000"
            assert settings.backend_timeout == 60.0
            assert settings.default_student_id == "test_user"
            assert settings.app_name == "Custom App"

    def test_settings_chat_placeholder(self):
        """Test chat placeholder default."""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()
            assert "Scrivi un messaggio" in settings.chat_placeholder

    def test_settings_log_level_options(self):
        """Test valid log level options."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            with patch.dict("os.environ", {"log_level": level}, clear=True):
                settings = Settings()
                assert settings.log_level == level


class TestGetFrontendSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test get_settings returns cached instance."""
        import italianollama.frontend.config as config_module
        config_module._settings = None  # Reset

        with patch("italianollama.frontend.config.Settings"):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2

    def test_get_settings_caches(self):
        """Test settings are cached after first call."""
        import italianollama.frontend.config as config_module
        config_module._settings = None

        with patch("italianollama.frontend.config.Settings") as mock_settings:
            mock_instance = MagicMock()
            mock_settings.return_value = mock_instance

            result1 = get_settings()
            result2 = get_settings()

            # Should only call Settings() once
            assert mock_settings.call_count == 1
