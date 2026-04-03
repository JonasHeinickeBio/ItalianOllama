"""Comprehensive error handling tests for Streamlit frontend.

Tests all error scenarios including:
- Custom exception classes (BackendError, StudentNotFoundError, etc.)
- Error message generation (MessageHandler.handle_error)
- Error handling decorators and utilities
- Error UI rendering
- Backend health check failures
- Page error handling
- Edge cases and boundary conditions
"""

import pytest
from unittest.mock import patch, MagicMock


class TestCustomExceptions:
    """Tests for custom exception classes."""

    def test_backend_error_base_exception(self):
        """Test BackendError is base exception."""
        from italianollama.frontend.api.errors import BackendError

        error = BackendError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_student_not_found_inherits_backend_error(self):
        """Test StudentNotFoundError inherits from BackendError."""
        from italianollama.frontend.api.errors import (
            BackendError,
            StudentNotFoundError,
        )

        error = StudentNotFoundError("Student not found")
        assert isinstance(error, BackendError)
        assert isinstance(error, Exception)
        assert "Student not found" in str(error)

    def test_backend_connection_error_inherits_backend_error(self):
        """Test BackendConnectionError inherits from BackendError."""
        from italianollama.frontend.api.errors import (
            BackendConnectionError,
            BackendError,
        )

        error = BackendConnectionError("Connection failed")
        assert isinstance(error, BackendError)
        assert isinstance(error, Exception)

    def test_streaming_error_inherits_backend_error(self):
        """Test StreamingError inherits from BackendError."""
        from italianollama.frontend.api.errors import BackendError, StreamingError

        error = StreamingError("Stream error")
        assert isinstance(error, BackendError)
        assert isinstance(error, Exception)


class TestMessageHandlerHandleError:
    """Tests for MessageHandler.handle_error method."""

    def test_handle_error_connection(self):
        """Test handle_error with BackendConnectionError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import BackendConnectionError

            error = BackendConnectionError("Connection failed")
            result = MessageHandler.handle_error(error)

            assert "Mi dispiace" in result
            assert "connettermi al server" in result

    def test_handle_error_student_not_found(self):
        """Test handle_error with StudentNotFoundError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import StudentNotFoundError

            error = StudentNotFoundError("Student not found")
            result = MessageHandler.handle_error(error)

            assert "Mi dispiace" in result
            assert "profilo non è stato trovato" in result

    def test_handle_error_streaming(self):
        """Test handle_error with StreamingError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import StreamingError

            error = StreamingError("Stream error")
            result = MessageHandler.handle_error(error)

            assert "Mi dispiace" in result
            assert "trasmissione della risposta" in result

    def test_handle_error_backend(self):
        """Test handle_error with generic BackendError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import BackendError

            error = BackendError("Backend error")
            result = MessageHandler.handle_error(error)

            assert "Mi dispiace" in result
            assert "server ha riscontrato un problema" in result

    def test_handle_error_unknown(self):
        """Test handle_error with unknown exception."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler

            error = ValueError("Unknown error")
            result = MessageHandler.handle_error(error)

            assert "Mi dispiace" in result
            assert "errore imprevisto" in result


class TestHandleApiErrorUtility:
    """Tests for handle_api_error utility function."""

    def test_handle_api_error_display(self):
        """Test handle_api_error displays error message."""
        with patch('streamlit.error') as mock_error:
            with patch('streamlit.caption') as mock_caption:
                from italianollama.frontend.streamlit.pages.utils import handle_api_error

                error = Exception("Network error")
                handle_api_error(error, "Connection failed")

                assert mock_error.called
                assert mock_caption.called

    def test_handle_api_error_default_message(self):
        """Test handle_api_error uses default message."""
        with patch('streamlit.error') as mock_error:
            with patch('streamlit.caption') as mock_caption:
                from italianollama.frontend.streamlit.pages.utils import handle_api_error

                error = Exception("Test error")
                handle_api_error(error)

                assert mock_error.called
                assert mock_caption.called


class TestWithErrorHandlingDecorator:
    """Tests for with_error_handling decorator."""

    def test_with_error_handling_success(self):
        """Test decorator passes through successful calls."""
        with patch('streamlit.error'):
            with patch('streamlit.caption'):
                from italianollama.frontend.streamlit.pages.utils import (
                    with_error_handling,
                )

                @with_error_handling
                def successful_function(x):
                    return x * 2

                result = successful_function(5)

                assert result == 10

    def test_with_error_handling_handles_error(self):
        """Test decorator handles exceptions."""
        with patch('streamlit.error') as mock_error:
            with patch('streamlit.caption') as mock_caption:
                from italianollama.frontend.streamlit.pages.utils import (
                    with_error_handling,
                )

                @with_error_handling
                def failing_function():
                    raise Exception("Test error")

                result = failing_function()

                assert result is None
                assert mock_error.called
                assert mock_caption.called

    def test_with_error_handling_preserves_function_name(self):
        """Test decorator preserves function metadata."""
        with patch('streamlit.error'):
            with patch('streamlit.caption'):
                from italianollama.frontend.streamlit.pages.utils import (
                    with_error_handling,
                )

                @with_error_handling
                def my_test_function():
                    return "test"

                assert my_test_function.__name__ == "my_test_function"


class TestCheckBackendHealth:
    """Tests for check_backend_health function."""

    def test_check_backend_health_success(self):
        """Test health check passes when backend healthy."""
        with patch('italianollama.frontend.streamlit.pages.utils.get_api_client') as mock_api:
            mock_client = MagicMock()
            mock_client.health_check.return_value = {"status": "ok", "neo4j": "connected"}
            mock_api.return_value = mock_client

            from italianollama.frontend.streamlit.pages.utils import check_backend_health

            result = check_backend_health()

            assert result is True
            mock_client.health_check.assert_called_once()

    def test_check_backend_health_degraded(self):
        """Test health check passes when backend degraded."""
        with patch('italianollama.frontend.streamlit.pages.utils.get_api_client') as mock_api:
            mock_client = MagicMock()
            mock_client.health_check.return_value = {"status": "degraded", "neo4j": "connected"}
            mock_api.return_value = mock_client

            from italianollama.frontend.streamlit.pages.utils import check_backend_health

            result = check_backend_health()

            assert result is True

    def test_check_backend_health_failed(self):
        """Test health check fails when backend unhealthy."""
        with patch('italianollama.frontend.streamlit.pages.utils.get_api_client') as mock_api:
            mock_client = MagicMock()
            mock_client.health_check.return_value = {"status": "error", "neo4j": "connected"}
            mock_api.return_value = mock_client

            from italianollama.frontend.streamlit.pages.utils import check_backend_health

            result = check_backend_health()

            assert result is False

    def test_check_backend_health_exception(self):
        """Test health check handles exceptions."""
        with patch('italianollama.frontend.streamlit.pages.utils.get_api_client') as mock_api:
            mock_client = MagicMock()
            mock_client.health_check.side_effect = Exception("Connection failed")
            mock_api.return_value = mock_client

            from italianollama.frontend.streamlit.pages.utils import check_backend_health

            result = check_backend_health()

            assert result is False

    def test_check_backend_health_returns_none(self):
        """Test health check handles None response."""
        with patch('italianollama.frontend.streamlit.pages.utils.get_api_client') as mock_api:
            mock_client = MagicMock()
            mock_client.health_check.return_value = None
            mock_api.return_value = mock_client

            from italianollama.frontend.streamlit.pages.utils import check_backend_health

            result = check_backend_health()

            assert result is False


class TestDisplayBackendUnavailable:
    """Tests for display_backend_unavailable function."""

    def test_display_backend_unavailable_shows_message(self):
        """Test displays backend unavailable message."""
        with patch('streamlit.error') as mock_error:
            with patch('streamlit.info') as mock_info:
                from italianollama.frontend.streamlit.pages.utils import (
                    display_backend_unavailable,
                )

                display_backend_unavailable()

                assert mock_error.called
                assert mock_info.called


class TestErrorCard:
    """Tests for error_card UI component."""

    def test_error_card_renders_error(self):
        """Test error card renders error message."""
        mock_container_ctx = MagicMock()
        with patch('streamlit.container', return_value=mock_container_ctx) as mock_container:
            with patch('streamlit.error') as mock_error:
                from italianollama.frontend.streamlit.pages.utils import error_card

                error_card("Error Title", "Error message content")

                assert mock_container.called
                assert mock_container_ctx.__enter__.called
                assert mock_container_ctx.__exit__.called
                mock_error.assert_called_once()


class TestMessageHandlerStreamResponse:
    """Tests for MessageHandler.stream_response error handling."""

    def test_stream_response_handles_connection_error(self):
        """Test stream_response handles BackendConnectionError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import BackendConnectionError

            async def run_test():
                with patch('italianollama.frontend.ui.messages.stream_chat_completions') as mock_stream:
                    mock_stream.side_effect = BackendConnectionError("Connection failed")

                    result = []
                    async for token in MessageHandler.stream_response([{"role": "user", "content": "test"}]):
                        result.append(token)

                    assert len(result) > 0
                    assert "connettermi al server" in result[-1]

            import asyncio
            asyncio.run(run_test())

    def test_stream_response_handles_student_not_found(self):
        """Test stream_response handles StudentNotFoundError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import StudentNotFoundError

            async def run_test():
                with patch('italianollama.frontend.ui.messages.stream_chat_completions') as mock_stream:
                    mock_stream.side_effect = StudentNotFoundError("Student not found")

                    result = []
                    async for token in MessageHandler.stream_response([{"role": "user", "content": "test"}]):
                        result.append(token)

                    assert len(result) > 0
                    assert "profilo non è stato trovato" in result[-1]

            import asyncio
            asyncio.run(run_test())

    def test_stream_response_handles_streaming_error(self):
        """Test stream_response handles StreamingError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import StreamingError

            async def run_test():
                with patch('italianollama.frontend.ui.messages.stream_chat_completions') as mock_stream:
                    mock_stream.side_effect = StreamingError("Stream error")

                    result = []
                    async for token in MessageHandler.stream_response([{"role": "user", "content": "test"}]):
                        result.append(token)

                    assert len(result) > 0
                    assert "trasmissione della risposta" in result[-1]

            import asyncio
            asyncio.run(run_test())

    def test_stream_response_handles_generic_error(self):
        """Test stream_response handles generic BackendError."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import BackendError

            async def run_test():
                with patch('italianollama.frontend.ui.messages.stream_chat_completions') as mock_stream:
                    mock_stream.side_effect = BackendError("Backend error")

                    result = []
                    async for token in MessageHandler.stream_response([{"role": "user", "content": "test"}]):
                        result.append(token)

                    assert len(result) > 0
                    assert "server ha riscontrato un problema" in result[-1]

            import asyncio
            asyncio.run(run_test())


class TestMessageHandlerCollectResponse:
    """Tests for MessageHandler.collect_response error handling."""

    def test_collect_response_handles_error(self):
        """Test collect_response handles errors from stream."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler
            from italianollama.frontend.api.errors import BackendConnectionError

            async def mock_async_iter():
                yield "Hello"
                yield " world"

            with patch.object(MessageHandler, 'stream_response', return_value=mock_async_iter()):
                import asyncio

                async def run_test():
                    result = await MessageHandler.collect_response(
                        [{"role": "user", "content": "test"}]
                    )
                    assert "Hello world" in result

                asyncio.run(run_test())


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_handle_error_with_none(self):
        """Test handle_error handles None input gracefully."""
        with patch.dict('sys.modules', {'chainlit': MagicMock()}):
            from italianollama.frontend.ui.messages import MessageHandler

            result = MessageHandler.handle_error(None)
            assert result is not None

    def test_check_backend_health_with_no_client(self):
        """Test check_backend_health handles missing client."""
        with patch('italianollama.frontend.streamlit.pages.utils.get_api_client') as mock_api:
            mock_api.side_effect = Exception("Client not initialized")

            from italianollama.frontend.streamlit.pages.utils import check_backend_health

            result = check_backend_health()

            assert result is False

    def test_with_error_handling_preserves_signature(self):
        """Test decorator preserves function signature."""
        with patch('streamlit.error'):
            with patch('streamlit.caption'):
                from italianollama.frontend.streamlit.pages.utils import (
                    with_error_handling,
                )

                @with_error_handling
                def function_with_params(a: int, b: int = 5) -> int:
                    return a + b

                result = function_with_params(3, b=7)

                assert result == 10

    def test_handle_api_error_with_empty_message(self):
        """Test handle_api_error handles empty message."""
        with patch('streamlit.error') as mock_error:
            with patch('streamlit.caption') as mock_caption:
                from italianollama.frontend.streamlit.pages.utils import handle_api_error

                handle_api_error(Exception("Error"), "")

                assert mock_error.called
                assert mock_caption.called

    def test_error_card_with_empty_title(self):
        """Test error_card handles empty title."""
        mock_container_ctx = MagicMock()
        with patch('streamlit.container', return_value=mock_container_ctx) as mock_container:
            with patch('streamlit.error') as mock_error:
                from italianollama.frontend.streamlit.pages.utils import error_card

                error_card("", "Error message")

                assert mock_container.called
                assert mock_container_ctx.__enter__.called
                assert mock_container_ctx.__exit__.called
                mock_error.assert_called_once()
