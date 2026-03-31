"""Unit tests for messages UI module."""

import pytest


class TestMessagesModule:
    """Test messages module imports and functions."""

    def test_messages_module_imports(self):
        """Test messages module can be imported."""
        from italianollama.frontend.ui import messages
        assert messages is not None

    def test_message_handler_exists(self):
        """Test MessageHandler class exists."""
        from italianollama.frontend.ui.messages import MessageHandler
        assert MessageHandler is not None

    def test_message_handler_error_messages(self):
        """Test MessageHandler has error messages."""
        from italianollama.frontend.ui.messages import MessageHandler
        assert hasattr(MessageHandler, 'ERROR_MESSAGES')
        assert "connection" in MessageHandler.ERROR_MESSAGES
        assert "student_not_found" in MessageHandler.ERROR_MESSAGES

    def test_message_handler_handle_error(self):
        """Test MessageHandler.handle_error method."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api.errors import BackendConnectionError

        error = BackendConnectionError("Connection failed")
        result = MessageHandler.handle_error(error)
        assert result is not None
        assert "Mi dispiace" in result

    def test_message_handler_stream_response(self):
        """Test MessageHandler.stream_response exists."""
        from italianollama.frontend.ui.messages import MessageHandler
        assert hasattr(MessageHandler, 'stream_response')

    def test_message_handler_collect_response(self):
        """Test MessageHandler.collect_response exists."""
        from italianollama.frontend.ui.messages import MessageHandler
        assert hasattr(MessageHandler, 'collect_response')
