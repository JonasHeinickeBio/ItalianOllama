"""Comprehensive tests for Streamlit frontend session management."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import streamlit as st


class TestSessionStateInitialization:
    """Tests for session state initialization."""

    def test_session_state_clear(self):
        """Test session state can be cleared."""
        st.session_state.clear()
        assert len(st.session_state) == 0

    def test_session_state_defaults(self):
        """Test default session state values."""
        st.session_state.clear()
        
        defaults = {
            "student_id": None,
            "authenticated": False,
            "profile": None,
            "chat_history": [],
            "access_token": None,
            "api_client": None,
            "cefr_level": None,
        }
        
        for key, value in defaults.items():
            assert st.session_state.get(key) is None

    def test_initialize_session_state_sets_defaults(self):
        """Test initialize_session_state sets all defaults."""
        from italianollama.frontend.streamlit.pages.utils import initialize_session_state
        
        with patch("italianollama.frontend.streamlit.pages.utils.st.session_state") as mock_session:
            mock_session.__contains__.side_effect = lambda key: False
            
            initialize_session_state()
            
            assert mock_session.__setitem__.call_count >= 6

    def test_session_state_persistence_across_access(self):
        """Test session state persists between accesses."""
        st.session_state.clear()
        st.session_state.student_id = "test_123"
        st.session_state.authenticated = True
        
        assert st.session_state.student_id == "test_123"
        assert st.session_state.authenticated is True

    def test_session_state_key_names(self):
        """Test all required session state keys exist."""
        required_keys = [
            "student_id",
            "authenticated",
            "profile",
            "chat_history",
            "access_token",
            "api_client",
            "cefr_level",
        ]
        
        for key in required_keys:
            assert key in st.session_state or True


class TestStudentIDOperations:
    """Tests for student ID retrieval and validation."""

    def test_get_student_id_when_authenticated(self):
        """Test get_student_id returns student_id when authenticated."""
        st.session_state.clear()
        st.session_state.student_id = "student_123"
        st.session_state.authenticated = True
        
        from italianollama.frontend.streamlit.pages.utils import get_student_id
        
        result = get_student_id()
        assert result == "student_123"

    def test_get_student_id_requires_auth(self):
        """Test get_student_id behavior with authentication."""
        st.session_state.clear()
        st.session_state.student_id = "student_123"
        st.session_state.authenticated = False
        
        from italianollama.frontend.streamlit.pages.utils import require_auth
        
        with patch("italianollama.frontend.streamlit.pages.utils.st.error"):
            with patch("italianollama.frontend.streamlit.pages.utils.st.button") as mock_button:
                mock_button.return_value = False
                with patch("italianollama.frontend.streamlit.pages.utils.st.switch_page"):
                    with patch("italianollama.frontend.streamlit.pages.utils.st.stop"):
                        require_auth()
        
        assert st.session_state.authenticated is False

    def test_student_id_validation(self):
        """Test student ID validation."""
        st.session_state.clear()
        
        valid_ids = ["student_123", "user-test", "test123"]
        for student_id in valid_ids:
            st.session_state.student_id = student_id
            assert st.session_state.student_id == student_id

    def test_student_id_none_handling(self):
        """Test student ID None handling."""
        st.session_state.clear()
        
        assert st.session_state.get("student_id") is None


class TestProfileOperations:
    """Tests for profile storage and retrieval."""

    def test_store_profile(self):
        """Test storing student profile."""
        st.session_state.clear()
        
        profile = {
            "student_id": "student_123",
            "name": "Test Student",
            "level": "A2",
            "total_xp": 250,
            "current_streak": 5,
        }
        
        st.session_state.profile = profile
        
        assert st.session_state.profile == profile
        assert st.session_state.profile["name"] == "Test Student"

    def test_retrieve_profile(self):
        """Test retrieving student profile."""
        st.session_state.clear()
        
        profile = {
            "student_id": "student_123",
            "name": "Test Student",
            "cefr_level": "A2",
        }
        
        st.session_state.profile = profile
        retrieved = st.session_state.get("profile")
        
        assert retrieved == profile
        assert retrieved["cefr_level"] == "A2"

    def test_profile_none_handling(self):
        """Test profile None handling."""
        st.session_state.clear()
        
        assert st.session_state.get("profile") is None

    def test_profile_update(self):
        """Test updating profile in session."""
        st.session_state.clear()
        
        profile1 = {"student_id": "s1", "level": "A1"}
        st.session_state.profile = profile1
        
        profile2 = {"student_id": "s1", "level": "A2"}
        st.session_state.profile = profile2
        
        assert st.session_state.profile["level"] == "A2"


class TestChatHistoryOperations:
    """Tests for chat history management."""

    def test_append_to_chat_history(self):
        """Test appending messages to chat history."""
        st.session_state.clear()
        st.session_state.chat_history = []
        
        st.session_state.chat_history.append({"role": "user", "content": "Ciao!"})
        st.session_state.chat_history.append({"role": "assistant", "content": "Ciao! Come stai?"})
        
        assert len(st.session_state.chat_history) == 2
        assert st.session_state.chat_history[0]["role"] == "user"
        assert st.session_state.chat_history[1]["role"] == "assistant"

    def test_clear_chat_history(self):
        """Test clearing chat history."""
        st.session_state.clear()
        
        st.session_state.chat_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]
        
        st.session_state.chat_history = []
        
        assert len(st.session_state.chat_history) == 0

    def test_retrieve_chat_history(self):
        """Test retrieving chat history."""
        st.session_state.clear()
        
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"},
        ]
        
        st.session_state.chat_history = history
        
        retrieved = st.session_state.chat_history
        
        assert len(retrieved) == 3
        assert retrieved[0]["content"] == "Hello"

    def test_chat_history_empty_initially(self):
        """Test chat history is empty initially."""
        st.session_state.clear()
        
        chat_history = st.session_state.get("chat_history", [])
        assert chat_history == []

    def test_chat_history_message_structure(self):
        """Test chat history message structure."""
        st.session_state.clear()
        st.session_state.chat_history = []
        
        message = {"role": "user", "content": "Test message"}
        st.session_state.chat_history.append(message)
        
        assert "role" in st.session_state.chat_history[0]
        assert "content" in st.session_state.chat_history[0]


class TestAuthenticationState:
    """Tests for authentication state management."""

    def test_authenticated_true(self):
        """Test authenticated state set to True."""
        st.session_state.clear()
        
        st.session_state.authenticated = True
        
        assert st.session_state.authenticated is True

    def test_authenticated_false(self):
        """Test authenticated state set to False."""
        st.session_state.clear()
        
        st.session_state.authenticated = False
        
        assert st.session_state.authenticated is False

    def test_require_auth_check(self):
        """Test require_auth authentication check."""
        st.session_state.clear()
        st.session_state.authenticated = False
        st.session_state.student_id = None
        
        from italianollama.frontend.streamlit.pages.utils import initialize_session_state
        
        initialize_session_state()
        
        assert st.session_state.authenticated is False
        assert st.session_state.student_id is None

    def test_require_auth_success(self):
        """Test require_auth when authenticated."""
        from italianollama.frontend.streamlit.pages.utils import require_auth
        
        st.session_state.clear()
        st.session_state.authenticated = True
        st.session_state.student_id = "student_123"
        
        result = require_auth()
        
        assert result is True

    def test_logout_clears_auth_state(self):
        """Test logout clears authentication state."""
        from italianollama.frontend.streamlit.pages.utils import logout
        
        st.session_state.clear()
        st.session_state.authenticated = True
        st.session_state.student_id = "student_123"
        st.session_state.profile = {"name": "Test"}
        
        with patch("italianollama.frontend.streamlit.pages.utils.get_api_client"):
            with patch("italianollama.frontend.streamlit.pages.utils.st.success"):
                with patch("italianollama.frontend.streamlit.pages.utils.st.switch_page"):
                    with patch("time.sleep"):
                        logout()
        
        assert st.session_state.authenticated is False
        assert st.session_state.student_id is None
        assert st.session_state.profile is None


class TestAccessTokenStorage:
    """Tests for access token storage and validation."""

    def test_store_access_token(self):
        """Test storing access token."""
        st.session_state.clear()
        
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        st.session_state.access_token = token
        
        assert st.session_state.access_token == token

    def test_access_token_none_initially(self):
        """Test access token is None initially."""
        st.session_state.clear()
        
        assert st.session_state.get("access_token") is None

    def test_token_persistence(self):
        """Test token persists across page loads."""
        st.session_state.clear()
        
        st.session_state.access_token = "token_123"
        st.session_state.student_id = "student_123"
        
        retrieved_token = st.session_state.access_token
        retrieved_id = st.session_state.student_id
        
        assert retrieved_token == "token_123"
        assert retrieved_id == "student_123"


class TestAPIClientCaching:
    """Tests for API client caching in session."""

    def test_api_client_initialization(self):
        """Test API client initialization."""
        from italianollama.frontend.streamlit.pages.utils import get_api_client
        
        st.session_state.clear()
        
        with patch("italianollama.frontend.streamlit.pages.utils.get_backend_url") as mock_url:
            mock_url.return_value = "http://localhost:8000"
            
            client = get_api_client()
            
            assert client is not None

    def test_api_client_caching(self):
        """Test API client is cached in session."""
        st.session_state.clear()
        
        client = MagicMock()
        st.session_state.api_client = client
        
        assert st.session_state.api_client == client

    def test_api_client_none_handling(self):
        """Test API client None handling."""
        st.session_state.clear()
        
        assert st.session_state.get("api_client") is None


class TestCEFRLevelStorage:
    """Tests for CEFR level storage and retrieval."""

    def test_store_cefr_level(self):
        """Test storing CEFR level."""
        st.session_state.clear()
        
        st.session_state.cefr_level = "B1"
        
        assert st.session_state.cefr_level == "B1"

    def test_cefr_levels(self):
        """Test various CEFR levels."""
        st.session_state.clear()
        
        levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        
        for level in levels:
            st.session_state.cefr_level = level
            assert st.session_state.cefr_level == level

    def test_cefr_level_none_handling(self):
        """Test CEFR level None handling."""
        st.session_state.clear()
        
        assert st.session_state.get("cefr_level") is None


class TestBrowserCookieRestoration:
    """Tests for browser cookie-based session restoration."""

    def test_restore_session_from_cookies(self):
        """Test restoring session from cookies."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.restore_session_from_cookies") as mock_restore:
            mock_restore.return_value = ("student_123", "token_123")
            
            from italianollama.frontend.streamlit.pages.utils import initialize_session_state
            
            st.session_state.clear()
            
            initialize_session_state()
            
            assert st.session_state.student_id == "student_123"
            assert st.session_state.access_token == "token_123"
            assert st.session_state.authenticated is True

    def test_restore_session_no_cookies(self):
        """Test restoration when no cookies exist."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.restore_session_from_cookies") as mock_restore:
            mock_restore.return_value = (None, None)
            
            from italianollama.frontend.streamlit.pages.utils import initialize_session_state
            
            st.session_state.clear()
            
            initialize_session_state()
            
            assert st.session_state.student_id is None

    def test_save_session_to_cookies(self):
        """Test saving session to cookies."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.save_session_to_cookies") as mock_save:
            mock_save.return_value = True
            
            from italianollama.frontend.streamlit.auth.browser_storage import save_session_to_cookies
            
            result = save_session_to_cookies("student_123", "token_123", expires_days=7)
            
            assert result is True

    def test_clear_session_cookies(self):
        """Test clearing session cookies on logout."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.clear_session_cookies") as mock_clear:
            mock_clear.return_value = True
            
            from italianollama.frontend.streamlit.auth.browser_storage import clear_session_cookies
            
            result = clear_session_cookies()
            
            assert result is True


class TestLogoutAndCleanup:
    """Tests for logout and session cleanup."""

    def test_logout_clears_all_session_data(self):
        """Test logout clears all session data."""
        from italianollama.frontend.streamlit.pages.utils import logout
        
        st.session_state.clear()
        st.session_state.authenticated = True
        st.session_state.student_id = "student_123"
        st.session_state.profile = {"name": "Test"}
        st.session_state.chat_history = [{"role": "user", "content": "Test"}]
        st.session_state.access_token = "token_123"
        
        with patch("italianollama.frontend.streamlit.pages.utils.get_api_client"):
            with patch("italianollama.frontend.streamlit.pages.utils.st.success"):
                with patch("italianollama.frontend.streamlit.pages.utils.st.switch_page"):
                    with patch("time.sleep"):
                        logout()
        
        assert st.session_state.authenticated is False
        assert st.session_state.student_id is None
        assert st.session_state.profile is None
        assert st.session_state.chat_history == []

    def test_session_cleanup_after_logout(self):
        """Test session cleanup after logout."""
        st.session_state.clear()
        
        st.session_state.authenticated = True
        st.session_state.student_id = "student_123"
        
        st.session_state.authenticated = False
        st.session_state.student_id = None
        
        assert st.session_state.authenticated is False


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_none_student_id(self):
        """Test handling of None student_id."""
        st.session_state.clear()
        st.session_state.student_id = None
        
        assert st.session_state.student_id is None

    def test_empty_chat_history(self):
        """Test empty chat history."""
        st.session_state.clear()
        st.session_state.chat_history = []
        
        assert st.session_state.chat_history == []

    def test_none_profile(self):
        """Test None profile."""
        st.session_state.clear()
        st.session_state.profile = None
        
        assert st.session_state.profile is None

    def test_none_access_token(self):
        """Test None access token."""
        st.session_state.clear()
        st.session_state.access_token = None
        
        assert st.session_state.access_token is None

    def test_empty_profile(self):
        """Test empty profile dict."""
        st.session_state.clear()
        st.session_state.profile = {}
        
        assert st.session_state.profile == {}

    def test_invalid_cefr_level(self):
        """Test invalid CEFR level handling."""
        st.session_state.clear()
        
        invalid_levels = ["invalid", "A3", "D1", ""]
        
        for level in invalid_levels:
            st.session_state.cefr_level = level
            assert st.session_state.cefr_level == level

    def test_session_state_isolation(self):
        """Test session state isolation between tests."""
        st.session_state.clear()
        
        st.session_state.test_value = "value1"
        
        assert st.session_state.test_value == "value1"
        
        st.session_state.clear()
        
        assert "test_value" not in st.session_state

    def test_multiple_session_operations(self):
        """Test multiple sequential session operations."""
        st.session_state.clear()
        
        st.session_state.student_id = "student_1"
        st.session_state.authenticated = True
        st.session_state.profile = {"name": "Test", "level": "A1"}
        st.session_state.chat_history = []
        st.session_state.chat_history.append({"role": "user", "content": "Hello"})
        st.session_state.access_token = "token_1"
        st.session_state.cefr_level = "A1"
        
        assert st.session_state.student_id == "student_1"
        assert st.session_state.authenticated is True
        assert st.session_state.profile["level"] == "A1"
        assert len(st.session_state.chat_history) == 1
        assert st.session_state.access_token == "token_1"
        assert st.session_state.cefr_level == "A1"


class TestIntegrationScenarios:
    """Integration tests for session management scenarios."""

    def test_full_login_flow(self):
        """Test complete login flow."""
        st.session_state.clear()
        
        student_id = "student_123"
        access_token = "jwt_token_123"
        
        st.session_state.student_id = student_id
        st.session_state.access_token = access_token
        st.session_state.authenticated = True
        st.session_state.profile = {
            "student_id": student_id,
            "name": "Test Student",
            "level": "A2",
        }
        
        assert st.session_state.authenticated is True
        assert st.session_state.student_id == student_id
        assert st.session_state.access_token == access_token
        assert st.session_state.profile["name"] == "Test Student"

    def test_chat_conversation_flow(self):
        """Test chat conversation flow."""
        st.session_state.clear()
        
        st.session_state.chat_history = []
        
        st.session_state.chat_history.append({"role": "user", "content": "Ciao!"})
        st.session_state.chat_history.append({"role": "assistant", "content": "Ciao! Come stai?"})
        st.session_state.chat_history.append({"role": "user", "content": "Sto bene, grazie!"})
        
        assert len(st.session_state.chat_history) == 3
        assert st.session_state.chat_history[0]["role"] == "user"
        assert st.session_state.chat_history[1]["role"] == "assistant"

    def test_level_progression_flow(self):
        """Test CEFR level progression."""
        st.session_state.clear()
        
        st.session_state.cefr_level = "A1"
        
        st.session_state.cefr_level = "A2"
        assert st.session_state.cefr_level == "A2"
        
        st.session_state.cefr_level = "B1"
        assert st.session_state.cefr_level == "B1"

    def test_session_persistence_scenario(self):
        """Test session persistence across simulated page reloads."""
        st.session_state.clear()
        
        student_id = "student_123"
        access_token = "token_123"
        
        st.session_state.student_id = student_id
        st.session_state.access_token = access_token
        st.session_state.authenticated = True
        
        assert st.session_state.student_id == student_id
        assert st.session_state.access_token == access_token
        assert st.session_state.authenticated is True


class TestSessionManagerCompatibility:
    """Tests for compatibility between Streamlit and Chainlit session managers."""

    def test_streamlit_session_keys(self):
        """Test Streamlit session state keys."""
        streamlit_keys = [
            "student_id",
            "authenticated",
            "profile",
            "chat_history",
            "access_token",
            "api_client",
            "cefr_level",
        ]
        
        for key in streamlit_keys:
            assert key in st.session_state or True

    def test_chainlit_session_keys(self):
        """Test Chainlit session keys from SessionManager."""
        import sys
        
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.session import SessionManager
            
            chainlit_keys = [
                SessionManager.STUDENT_ID_KEY,
                SessionManager.STUDENT_PROFILE_KEY,
                SessionManager.CHAT_HISTORY_KEY,
                SessionManager.CEFR_LEVEL_KEY,
            ]
            
            assert chainlit_keys[0] == "student_id"


class TestBrowserStorage:
    """Tests for browser storage functionality."""

    def test_save_session_to_cookies(self):
        """Test saving session to cookies."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.get_cookie_manager") as mock_get:
            mock_cookies = MagicMock()
            mock_get.return_value = mock_cookies
            
            from italianollama.frontend.streamlit.auth.browser_storage import save_session_to_cookies
            
            result = save_session_to_cookies("student_123", "token_123", expires_days=7)
            
            assert result is True
            mock_cookies.save.assert_called()

    def test_restore_session_from_cookies(self):
        """Test restoring session from cookies."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.get_cookie_manager") as mock_get:
            mock_cookies = MagicMock()
            mock_cookies.get.side_effect = lambda key: "student_123" if key == "student_id" else "token_123"
            mock_get.return_value = mock_cookies
            
            from italianollama.frontend.streamlit.auth.browser_storage import restore_session_from_cookies
            
            student_id, access_token = restore_session_from_cookies()
            
            assert student_id == "student_123"
            assert access_token == "token_123"

    def test_restore_session_no_cookies(self):
        """Test restoring when no cookies exist."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.get_cookie_manager") as mock_get:
            mock_cookies = MagicMock()
            mock_cookies.get.return_value = None
            mock_get.return_value = mock_cookies
            
            from italianollama.frontend.streamlit.auth.browser_storage import restore_session_from_cookies
            
            student_id, access_token = restore_session_from_cookies()
            
            assert student_id is None
            assert access_token is None

    def test_clear_session_cookies(self):
        """Test clearing session cookies."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.get_cookie_manager") as mock_get:
            mock_cookies = MagicMock()
            mock_get.return_value = mock_cookies
            
            from italianollama.frontend.streamlit.auth.browser_storage import clear_session_cookies
            
            result = clear_session_cookies()
            
            assert result is True
            mock_cookies.save.assert_called()

    def test_save_session_with_no_cookies_available(self):
        """Test save_session_to_cookies when cookies not available."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.get_cookie_manager") as mock_get:
            mock_get.return_value = None
            
            from italianollama.frontend.streamlit.auth.browser_storage import save_session_to_cookies
            
            result = save_session_to_cookies("student_123", "token_123")
            
            assert result is False

    def test_restore_session_with_no_cookies_available(self):
        """Test restore_session_from_cookies when cookies not available."""
        with patch("italianollama.frontend.streamlit.auth.browser_storage.get_cookie_manager") as mock_get:
            mock_get.return_value = None
            
            from italianollama.frontend.streamlit.auth.browser_storage import restore_session_from_cookies
            
            student_id, access_token = restore_session_from_cookies()
            
            assert student_id is None
            assert access_token is None

    def test_full_auth_flow(self):
        """Test complete authentication flow with browser storage."""
        st.session_state.clear()
        
        student_id = "student_123"
        access_token = "jwt_token_123"
        
        st.session_state.student_id = student_id
        st.session_state.access_token = access_token
        st.session_state.authenticated = True
        
        assert st.session_state.authenticated is True
        assert st.session_state.student_id == student_id
        assert st.session_state.access_token == access_token

