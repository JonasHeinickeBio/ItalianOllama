"""Unit tests for frontend UI messages with mocking."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestMessageHandler:
    """Tests for MessageHandler."""

    def test_message_handler_error_messages(self):
        """Test error messages are defined."""
        from italianollama.frontend.ui.messages import MessageHandler

        assert "connection" in MessageHandler.ERROR_MESSAGES
        assert "student_not_found" in MessageHandler.ERROR_MESSAGES
        assert "streaming" in MessageHandler.ERROR_MESSAGES
        assert "backend" in MessageHandler.ERROR_MESSAGES
        assert "unknown" in MessageHandler.ERROR_MESSAGES

    @pytest.mark.asyncio
    async def test_stream_response_basic(self):
        """Test streaming response basic flow."""
        from italianollama.frontend.ui.messages import MessageHandler

        async def mock_stream():
            yield "Ciao! "
            yield "Come stai?"

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            return_value=mock_stream(),
        ):
            chunks = []
            async for chunk in MessageHandler.stream_response(
                [{"role": "user", "content": "Ciao"}]
            ):
                chunks.append(chunk)

            assert "Ciao!" in "".join(chunks)

    @pytest.mark.asyncio
    async def test_stream_response_connection_error(self):
        """Test streaming response handles connection error."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import BackendConnectionError

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            side_effect=BackendConnectionError("Connection failed"),
        ):
            chunks = []
            async for chunk in MessageHandler.stream_response(
                [{"role": "user", "content": "Ciao"}]
            ):
                chunks.append(chunk)

            # Should yield error message
            assert any("🔌" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_response_student_not_found(self):
        """Test streaming response handles student not found."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import StudentNotFoundError

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            side_effect=StudentNotFoundError("Student not found"),
        ):
            chunks = []
            async for chunk in MessageHandler.stream_response(
                [{"role": "user", "content": "Ciao"}]
            ):
                chunks.append(chunk)

            assert any("👤" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_response_streaming_error(self):
        """Test streaming response handles streaming error."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import StreamingError

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            side_effect=StreamingError("Streaming failed"),
        ):
            chunks = []
            async for chunk in MessageHandler.stream_response(
                [{"role": "user", "content": "Ciao"}]
            ):
                chunks.append(chunk)

            assert any("📡" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_response_backend_error(self):
        """Test streaming response handles backend error."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import BackendError

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            side_effect=BackendError("Backend error"),
        ):
            chunks = []
            async for chunk in MessageHandler.stream_response(
                [{"role": "user", "content": "Ciao"}]
            ):
                chunks.append(chunk)

            assert any("⚠️" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_response_unknown_error(self):
        """Test streaming response handles unknown error."""
        from italianollama.frontend.ui.messages import MessageHandler

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            side_effect=Exception("Unknown error"),
        ):
            chunks = []
            async for chunk in MessageHandler.stream_response(
                [{"role": "user", "content": "Ciao"}]
            ):
                chunks.append(chunk)

            assert any("❓" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_collect_response(self):
        """Test collecting full response."""
        from italianollama.frontend.ui.messages import MessageHandler

        async def mock_stream():
            yield "Ciao! "
            yield "Come stai?"

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            return_value=mock_stream(),
        ):
            response = await MessageHandler.collect_response(
                [{"role": "user", "content": "Ciao"}]
            )

            assert response == "Ciao! Come stai?"

    def test_handle_error_connection(self):
        """Test error handling for connection error."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import BackendConnectionError

        error = BackendConnectionError("Connection failed")
        message = MessageHandler.handle_error(error)

        assert "🔌" in message

    def test_handle_error_student_not_found(self):
        """Test error handling for student not found."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import StudentNotFoundError

        error = StudentNotFoundError("Student not found")
        message = MessageHandler.handle_error(error)

        assert "👤" in message

    def test_handle_error_streaming(self):
        """Test error handling for streaming error."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import StreamingError

        error = StreamingError("Streaming failed")
        message = MessageHandler.handle_error(error)

        assert "📡" in message

    def test_handle_error_backend(self):
        """Test error handling for backend error."""
        from italianollama.frontend.ui.messages import MessageHandler
        from italianollama.frontend.api import BackendError

        error = BackendError("Backend failed")
        message = MessageHandler.handle_error(error)

        assert "⚠️" in message

    def test_handle_error_unknown(self):
        """Test error handling for unknown error."""
        from italianollama.frontend.ui.messages import MessageHandler

        error = Exception("Unknown error")
        message = MessageHandler.handle_error(error)

        assert "❓" in message

    @pytest.mark.asyncio
    async def test_send_and_save_response(self):
        """Test send and save response."""
        from italianollama.frontend.ui.messages import MessageHandler

        async def mock_stream():
            yield "Ciao!"

        with patch(
            "italianollama.frontend.ui.messages.stream_chat_completions",
            return_value=mock_stream(),
        ):
            with patch(
                "italianollama.frontend.ui.messages.SessionManager.append_to_chat_history"
            ) as mock_append:
                response = await MessageHandler.send_and_save_response(
                    "Ciao", [{"role": "user", "content": "Ciao"}]
                )

                assert response == "Ciao!"
                assert mock_append.call_count == 2
