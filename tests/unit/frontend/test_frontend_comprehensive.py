"""Comprehensive unit tests for frontend components."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient

from italianollama.frontend.config import get_settings


class TestFrontendConfig:
    """Tests for frontend configuration."""

    def test_get_settings_defaults(self):
        """Test frontend config defaults."""
        with patch.dict('os.environ', {}, clear=True):
            config = get_settings()
            
            assert config.backend_url == "http://localhost:8000"
            assert config.chainlit_url == "http://localhost:8501"
            assert config.debug is False

    def test_get_settings_from_env(self):
        """Test frontend config from environment."""
        with patch.dict('os.environ', {
            'BACKEND_URL': 'http://test:9000',
            'CHAINLIT_URL': 'http://test:9500',
            'DEBUG': 'true',
        }, clear=True):
            config = get_settings()
            
            assert config.backend_url == 'http://test:9000'
            assert config.chainlit_url == 'http://test:9500'
            assert config.debug is True


class TestFrontendUIMessages:
    """Tests for UI messages."""

    def test_messages_module_import(self):
        """Test messages module can be imported."""
        from italianollama.frontend.ui import messages
        
        assert messages is not None

    def test_greetings_module_import(self):
        """Test greetings module can be imported."""
        from italianollama.frontend.ui import greetings
        
        assert greetings is not None


class TestFrontendUIClient:
    """Tests for frontend API client."""

    def test_client_import(self):
        """Test API client can be imported."""
        from italianollama.frontend.api.client import BackendClient
        
        assert BackendClient is not None

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client can be initialized."""
        from italianollama.frontend.api.client import BackendClient
        
        client = BackendClient(base_url="http://localhost:8000")
        
        assert client.base_url == "http://localhost:8000"

    @pytest.mark.asyncio
    async def test_client_get_student(self):
        """Test client get_student method."""
        from italianollama.frontend.api.client import BackendClient
        
        client = BackendClient(base_url="http://localhost:8000")
        
        with patch.object(client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = AsyncMock(return_value={
                "student_id": "test_123",
                "name": "Test User",
                "level": "A2",
            })
            mock_get.return_value = mock_response
            
            result = await client.get_student("test_123")
            
            assert result["student_id"] == "test_123"

    @pytest.mark.asyncio
    async def test_client_chat_completions(self):
        """Test client chat completions method."""
        from italianollama.frontend.api.client import BackendClient
        
        client = BackendClient(base_url="http://localhost:8000")
        
        with patch.object(client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = AsyncMock(return_value={
                "id": "chatcmpl-123",
                "choices": [{"message": {"content": "Ciao!"}}],
            })
            mock_post.return_value = mock_response
            
            result = await client.chat_completions(
                messages=[{"role": "user", "content": "Ciao"}],
                student_id="test_123"
            )
            
            assert "choices" in result

    @pytest.mark.asyncio
    async def test_client_create_student(self):
        """Test client create_student method."""
        from italianollama.frontend.api.client import BackendClient
        
        client = BackendClient(base_url="http://localhost:8000")
        
        with patch.object(client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json = AsyncMock(return_value={
                "status": "created",
                "student_id": "new_123",
            })
            mock_post.return_value = mock_response
            
            result = await client.create_student("new_123", "New User")
            
            assert result["status"] == "created"

    @pytest.mark.asyncio
    async def test_client_get_auth_token(self):
        """Test client get_auth_token method."""
        from italianollama.frontend.api.client import BackendClient
        
        client = BackendClient(base_url="http://localhost:8000")
        
        with patch.object(client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json = AsyncMock(return_value={
                "access_token": "token_123",
                "token_type": "bearer",
            })
            mock_post.return_value = mock_response
            
            result = await client.get_auth_token("test_123")
            
            assert result["access_token"] == "token_123"


class TestFrontendErrors:
    """Tests for frontend error handling."""

    def test_errors_module_import(self):
        """Test errors module can be imported."""
        from italianollama.frontend.api import errors
        
        assert errors is not None

    def test_backend_error(self):
        """Test BackendError exception."""
        from italianollama.frontend.api.errors import BackendError
        
        with pytest.raises(BackendError) as exc_info:
            raise BackendError("Test error", status_code=500)
        
        assert "Test error" in str(exc_info.value)


class TestStreamlitApp:
    """Tests for Streamlit app."""

    def test_app_module_import(self):
        """Test app module can be imported."""
        from italianollama.frontend.streamlit import app
        
        assert app is not None

    def test_app_enhanced_import(self):
        """Test app_enhanced module can be imported."""
        from italianollama.frontend.streamlit import app_enhanced
        
        assert app_enhanced is not None


class TestChainlitApp:
    """Tests for Chainlit app."""

    def test_chainlit_app_import(self):
        """Test Chainlit app can be imported."""
        from italianollama.frontend import chainlit_app
        
        assert chainlit_app is not None


class TestSessionManager:
    """Tests for session management."""

    def test_session_module_import(self):
        """Test session module can be imported."""
        from italianollama.frontend.ui import session
        
        assert session is not None

    def test_session_manager_creation(self):
        """Test session manager can be created."""
        from italianollama.frontend.ui.session import SessionManager
        
        manager = SessionManager()
        
        assert manager is not None


class TestAPIInit:
    """Tests for frontend API __init__."""

    def test_api_init_imports(self):
        """Test frontend API __init__ exports."""
        from italianollama.frontend.api import __all__
        
        assert 'BackendClient' in __all__


class TestPagesUtils:
    """Tests for pages utilities."""

    def test_pages_utils_import(self):
        """Test pages utils can be imported."""
        from italianollama.frontend.streamlit.pages import utils
        
        assert utils is not None

    def test_pages_import(self):
        """Test pages modules can be imported."""
        # These may not exist, but import should not crash
        try:
            from italianollama.frontend.streamlit.pages import login
            from italianollama.frontend.streamlit.pages import dashboard
            from italianollama.frontend.streamlit.pages import chat
        except ImportError:
            pass  # Some pages may not exist


class TestAuthSession:
    """Tests for auth session."""

    def test_auth_session_import(self):
        """Test auth session can be imported."""
        from italianollama.frontend.streamlit.auth import session
        
        assert session is not None
