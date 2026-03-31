"""Unit tests for API config module using pytest mock and magic mock."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestSettings:
    """Unit tests for Settings class."""

    def setup_method(self):
        """Reset global settings before each test."""
        import italianollama.api.config as config_module
        config_module._settings = None

    def test_settings_defaults(self):
        """Test default settings values when env vars are not set."""
        from italianollama.api.config import Settings
        
        with patch.dict('os.environ', {}, clear=True):
            settings = Settings()
            
            assert settings.neo4j_uri == "bolt://localhost:7687"
            assert settings.neo4j_user == "neo4j"
            assert settings.neo4j_database == "neo4j"
            assert settings.litellm_base_url == "http://litellm:4000"

    def test_settings_cors_defaults(self):
        """Test CORS default origins."""
        from italianollama.api.config import Settings
        
        with patch.dict('os.environ', {}, clear=True):
            settings = Settings()
            
            assert "http://localhost:3000" in settings.cors_origins
            assert "http://localhost:8501" in settings.cors_origins

    def test_settings_auth_defaults(self):
        """Test authentication defaults."""
        from italianollama.api.config import Settings
        
        with patch.dict('os.environ', {}, clear=True):
            settings = Settings()
            
            assert settings.jwt_algorithm == "HS256"
            assert settings.jwt_expiration_hours == 4

    def test_settings_log_level(self):
        """Test log level setting."""
        from italianollama.api.config import Settings
        
        with patch.dict('os.environ', {}, clear=True):
            settings = Settings()
            
            assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_settings_custom_neo4j_uri(self):
        """Test custom Neo4j URI from env."""
        from italianollama.api.config import Settings
        
        with patch.dict('os.environ', {'NEO4J_URI': 'neo4j+s://custom.db'}):
            settings = Settings()
            
            assert settings.neo4j_uri == "neo4j+s://custom.db"

    def test_settings_use_aura(self):
        """Test use_aura setting."""
        from italianollama.api.config import Settings
        
        with patch.dict('os.environ', {'USE_AURA': 'true'}):
            settings = Settings()
            
            assert settings.use_aura is True


class TestGetSettings:
    """Tests for get_settings function."""

    def setup_method(self):
        """Reset global settings before each test."""
        import italianollama.api.config as config_module
        config_module._settings = None

    @patch('italianollama.api.config.Settings')
    def test_get_settings_creates_instance(self, mock_settings):
        """Test that get_settings creates a Settings instance."""
        from italianollama.api.config import get_settings
        
        mock_instance = MagicMock()
        mock_settings.return_value = mock_instance
        
        result = get_settings()
        
        assert result == mock_instance

    @patch('italianollama.api.config.Settings')
    def test_get_settings_returns_cached(self, mock_settings):
        """Test that get_settings returns cached instance."""
        from italianollama.api.config import get_settings
        
        mock_instance = MagicMock()
        mock_settings.return_value = mock_instance
        
        # First call
        result1 = get_settings()
        # Second call
        result2 = get_settings()
        
        # Settings should only be created once due to caching
        assert mock_settings.call_count == 1


class TestGetLogLevel:
    """Tests for get_log_level function."""

    @patch('italianollama.api.config.get_settings')
    def test_get_log_level_info(self, mock_settings):
        """Test get_log_level returns correct level."""
        from italianollama.api.config import get_log_level
        
        mock_settings.return_value.log_level = "INFO"
        
        result = get_log_level()
        
        assert result == 20  # logging.INFO

    @patch('italianollama.api.config.get_settings')
    def test_get_log_level_debug(self, mock_settings):
        """Test get_log_level returns DEBUG."""
        from italianollama.api.config import get_log_level
        
        mock_settings.return_value.log_level = "DEBUG"
        
        result = get_log_level()
        
        assert result == 10  # logging.DEBUG

    @patch('italianollama.api.config.get_settings')
    def test_get_log_level_error(self, mock_settings):
        """Test get_log_level returns ERROR."""
        from italianollama.api.config import get_log_level
        
        mock_settings.return_value.log_level = "ERROR"
        
        result = get_log_level()
        
        assert result == 40  # logging.ERROR
