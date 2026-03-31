"""Unit tests for frontend session module using proper mocking."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestSessionManagerUnit:
    """Unit tests for SessionManager."""

    def test_student_id_key_constant(self):
        """Test student ID key constant."""
        from italianollama.frontend.ui.session import SessionManager
        assert SessionManager.STUDENT_ID_KEY == "student_id"

    def test_student_profile_key_constant(self):
        """Test student profile key constant."""
        from italianollama.frontend.ui.session import SessionManager
        assert SessionManager.STUDENT_PROFILE_KEY == "student_profile"

    def test_chat_history_key_constant(self):
        """Test chat history key constant."""
        from italianollama.frontend.ui.session import SessionManager
        assert SessionManager.CHAT_HISTORY_KEY == "chat_history"

    def test_cefr_level_key_constant(self):
        """Test CEFR level key constant."""
        from italianollama.frontend.ui.session import SessionManager
        assert SessionManager.CEFR_LEVEL_KEY == "cefr_level"

    def test_session_manager_class_exists(self):
        """Test SessionManager class exists."""
        from italianollama.frontend.ui.session import SessionManager
        assert SessionManager is not None

    @patch('italianollama.frontend.ui.session.cl')
    def test_get_student_id_from_session(self, mock_cl):
        """Test getting student ID from session."""
        from italianollama.frontend.ui.session import SessionManager
        
        # Create a proper mock for user_session that returns value for first call (student_id key)
        mock_user_session = MagicMock()
        mock_user_session.get.return_value = "test_student_123"
        mock_cl.user_session = mock_user_session
        
        result = SessionManager.get_student_id()
        
        assert result == "test_student_123"
        mock_user_session.get.assert_called_with("student_id")

    @patch('italianollama.frontend.ui.session.cl')
    @patch('italianollama.frontend.ui.session.get_settings')
    def test_get_student_id_fallback_to_default(self, mock_settings, mock_cl):
        """Test falling back to default student ID when session is empty."""
        from italianollama.frontend.ui.session import SessionManager
        
        # First call returns None (student_id not set), second call returns default
        mock_user_session = MagicMock()
        mock_user_session.get.side_effect = [None, "fallback_student"]
        mock_cl.user_session = mock_user_session
        
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_student_id = "fallback_student"
        mock_settings.return_value = mock_settings_instance
        
        result = SessionManager.get_student_id()
        
        assert result == "fallback_student"

    @patch('italianollama.frontend.ui.session.cl')
    def test_get_student_level(self, mock_cl):
        """Test getting CEFR level from session."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_user_session = MagicMock()
        mock_user_session.get.return_value = "B2"
        mock_cl.user_session = mock_user_session
        
        result = SessionManager.get_student_level()
        
        assert result == "B2"
        mock_user_session.get.assert_called_with("cefr_level")

    @patch('italianollama.frontend.ui.session.cl')
    def test_get_student_level_none(self, mock_cl):
        """Test getting CEFR level when not set."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_user_session = MagicMock()
        mock_user_session.get.return_value = None
        mock_cl.user_session = mock_user_session
        
        result = SessionManager.get_student_level()
        
        assert result is None

    @patch('italianollama.frontend.ui.session.cl')
    def test_get_student_profile(self, mock_cl):
        """Test getting full student profile."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_profile = {"student_id": "test", "cefr_level": "A2"}
        mock_user_session = MagicMock()
        mock_user_session.get.return_value = mock_profile
        mock_cl.user_session = mock_user_session
        
        result = SessionManager.get_student_profile()
        
        assert result == mock_profile

    @patch('italianollama.frontend.ui.session.cl')
    def test_append_to_chat_history(self, mock_cl):
        """Test appending message to chat history."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_user_session = MagicMock()
        mock_user_session.get.return_value = []
        mock_cl.user_session = mock_user_session
        
        SessionManager.append_to_chat_history("user", "Hello")
        
        # Verify set was called with updated history
        mock_user_session.set.assert_called()

    @patch('italianollama.frontend.ui.session.cl')
    def test_get_chat_history(self, mock_cl):
        """Test getting chat history."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Ciao!"}
        ]
        mock_user_session = MagicMock()
        mock_user_session.get.return_value = mock_history
        mock_cl.user_session = mock_user_session
        
        result = SessionManager.get_chat_history()
        
        assert len(result) == 2

    @patch('italianollama.frontend.ui.session.cl')
    def test_clear_chat_history(self, mock_cl):
        """Test clearing chat history."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_user_session = MagicMock()
        mock_cl.user_session = mock_user_session
        
        SessionManager.clear_chat_history()
        
        mock_user_session.set.assert_called_with("chat_history", [])

    @patch('italianollama.frontend.ui.session.cl')
    def test_update_cefr_level(self, mock_cl):
        """Test updating CEFR level in session."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_user_session = MagicMock()
        mock_cl.user_session = mock_user_session
        
        SessionManager.update_cefr_level("C1")
        
        mock_user_session.set.assert_called_with("cefr_level", "C1")

    @pytest.mark.asyncio
    @patch('italianollama.frontend.ui.session.cl')
    @patch('italianollama.frontend.ui.session.get_student_profile', new_callable=AsyncMock)
    @patch('italianollama.frontend.ui.session.get_settings')
    async def test_initialize_session_with_existing_student(
        self, mock_settings, mock_get_profile, mock_cl
    ):
        """Test session initialization with existing student."""
        from italianollama.frontend.ui.session import SessionManager
        
        mock_user_session = MagicMock()
        mock_cl.user_session = mock_user_session
        
        mock_settings_instance = MagicMock()
        mock_settings_instance.default_student_id = "default_student"
        mock_settings.return_value = mock_settings_instance
        
        mock_get_profile.return_value = {
            "student_id": "default_student",
            "cefr_level": "B1",
            "name": "Test Student"
        }
        
        result = await SessionManager.initialize_session()
        
        assert result["student_id"] == "default_student"
        assert result["cefr_level"] == "B1"
        # Verify session was set
        assert mock_user_session.set.called
