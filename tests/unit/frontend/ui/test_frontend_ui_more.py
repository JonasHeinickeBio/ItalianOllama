"""Unit tests for frontend UI modules - greetings and messages."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestCEFRGreeter:
    """Tests for CEFRGreeter class (from greetings module)."""

    def test_cefr_greeter_class_exists(self):
        """Test CEFRGreeter class can be imported."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        assert CEFRGreeter is not None

    def test_greeting_unknown_level(self):
        """Test greeting for unknown CEFR level."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting(None)
        
        assert "Ciao" in result
        assert "CEFR level" in result or "level" in result.lower()

    def test_greeting_a1_level(self):
        """Test greeting for A1 level."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting("A1")
        
        assert "A1" in result
        assert "Beginner" in result or "Ciao" in result

    def test_greeting_a2_level(self):
        """Test greeting for A2 level."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting("A2")
        
        assert "A2" in result

    def test_greeting_b1_level(self):
        """Test greeting for B1 level."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting("B1")
        
        assert "B1" in result

    def test_greeting_b2_level(self):
        """Test greeting for B2 level."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting("B2")
        
        assert "B2" in result

    def test_greeting_c1_level(self):
        """Test greeting for C1 level."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting("C1")
        
        assert "C1" in result

    def test_greeting_c2_level(self):
        """Test greeting for C2 level."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting("C2")
        
        assert "C2" in result

    def test_greeting_case_insensitive(self):
        """Test greeting is case insensitive."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result_lower = CEFRGreeter.get_greeting("b1")
        result_upper = CEFRGreeter.get_greeting("B1")
        
        assert "B1" in result_lower
        assert "B1" in result_upper

    def test_greeting_invalid_level(self):
        """Test greeting for invalid level returns unknown."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        result = CEFRGreeter.get_greeting("INVALID")
        
        # Should return unknown greeting
        assert "Ciao" in result

    def test_available_levels(self):
        """Test getting available CEFR levels."""
        from italianollama.frontend.ui.greetings import CEFRGreeter
        
        levels = CEFRGreeter.get_available_levels()
        
        assert "A1" in levels
        assert "A2" in levels
        assert "B1" in levels
        assert "B2" in levels
        assert "C1" in levels
        assert "C2" in levels
        assert len(levels) == 6


class TestMessageHandler:
    """Tests for MessageHandler class (from messages module)."""

    def test_message_handler_class_exists(self):
        """Test MessageHandler class can be imported."""
        from italianollama.frontend.ui.messages import MessageHandler
        assert MessageHandler is not None

    def test_error_messages_defined(self):
        """Test error messages are defined."""
        from italianollama.frontend.ui.messages import MessageHandler
        
        assert hasattr(MessageHandler, 'ERROR_MESSAGES')
        assert "connection" in MessageHandler.ERROR_MESSAGES
        assert "student_not_found" in MessageHandler.ERROR_MESSAGES
        assert "streaming" in MessageHandler.ERROR_MESSAGES
        assert "backend" in MessageHandler.ERROR_MESSAGES
        assert "unknown" in MessageHandler.ERROR_MESSAGES

    def test_error_messages_are_italian(self):
        """Test error messages are in Italian."""
        from italianollama.frontend.ui.messages import MessageHandler
        
        for key, msg in MessageHandler.ERROR_MESSAGES.items():
            assert isinstance(msg, str)
            assert len(msg) > 0

    def test_handle_error_connection(self):
        """Test error handling for connection errors."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import BackendConnectionError
        
        error = BackendConnectionError("Connection failed")
        result = MessageHandler.handle_error(error)
        
        assert "Mi dispiace" in result

    def test_handle_error_student_not_found(self):
        """Test error handling for student not found."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import StudentNotFoundError
        
        error = StudentNotFoundError("Student not found")
        result = MessageHandler.handle_error(error)
        
        assert "profilo" in result or "Mi dispiace" in result

    def test_handle_error_streaming(self):
        """Test error handling for streaming errors."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import StreamingError
        
        error = StreamingError("Streaming failed")
        result = MessageHandler.handle_error(error)
        
        assert "Mi dispiace" in result

    def test_handle_error_backend(self):
        """Test error handling for backend errors."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import BackendError
        
        error = BackendError("Backend error")
        result = MessageHandler.handle_error(error)
        
        assert "Mi dispiace" in result or "server" in result

    def test_handle_error_unknown(self):
        """Test error handling for unknown errors."""
        from italianollama.frontend.ui.messages import MessageHandler
        
        error = Exception("Unknown error")
        result = MessageHandler.handle_error(error)
        
        assert "Mi dispiace" in result or "errore" in result
