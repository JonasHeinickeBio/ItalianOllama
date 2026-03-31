"""Message handling for chat responses and error management."""

from collections.abc import AsyncIterator
import logging

from italianollama.frontend.api import (
    BackendConnectionError,
    BackendError,
    StreamingError,
    StudentNotFoundError,
    stream_chat_completions,
)
from italianollama.frontend.ui.session import SessionManager

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handle chat message streaming, collection, and error responses.

    Manages the full lifecycle of backend communication for chat completions,
    including streaming, error handling, and session history management.
    """

    # Error messages in Italian (user-facing)
    ERROR_MESSAGES = {
        "connection": (
            "🔌 Mi dispiace, non riesco a connettermi al server. "
            "Per favore, riprova tra qualche istante."
        ),
        "student_not_found": (
            "👤 Mi dispiace, il tuo profilo non è stato trovato. "
            "Per favore, contatta l'amministratore."
        ),
        "streaming": (
            "📡 Mi dispiace, si è verificato un errore durante la trasmissione della risposta. "
            "Per favore, riprova."
        ),
        "backend": (
            "⚠️ Mi dispiace, il server ha riscontrato un problema. "
            "Per favore, riprova tra qualche istante."
        ),
        "unknown": (
            "❓ Mi dispiace, si è verificato un errore imprevisto. "
            "Per favore, contatta l'amministratore se il problema persiste."
        ),
    }

    @staticmethod
    async def stream_response(
        messages: list[dict[str, str]],
        model: str = "openai-compatible",
    ) -> AsyncIterator[str]:
        """Stream chat response from backend.

        Yields tokens as they arrive from the backend streaming endpoint.
        Automatically adds authentication token if available.

        Args:
            messages: Chat history with 'role' and 'content' keys
            model: Model identifier (default: openai-compatible)

        Yields:
            Response tokens as they arrive

        Example:
            async for token in MessageHandler.stream_response(messages):
                print(token, end="", flush=True)
        """
        logger.debug(
            "Starting streaming response | messages=%d | model=%s",
            len(messages),
            model,
        )

        # Quick availability check/ping to wake up backend
        import httpx
        from italianollama.frontend.config import get_settings
        settings = get_settings()
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.get(f"{settings.backend_url}/")
        except Exception:
            pass # Ignore errors here, let stream_chat_completions handle it

        try:
            async for token in stream_chat_completions(
                messages=messages,
                model=model,
            ):
                yield token

            logger.debug("Streaming response completed")

        except StreamingError as e:
            logger.error("Streaming error: %s", e, exc_info=True)
            yield MessageHandler.ERROR_MESSAGES["streaming"]
        except BackendConnectionError as e:
            logger.error("Backend connection error: %s", e, exc_info=True)
            yield MessageHandler.ERROR_MESSAGES["connection"]
        except StudentNotFoundError as e:
            logger.error("Student not found: %s", e, exc_info=True)
            yield MessageHandler.ERROR_MESSAGES["student_not_found"]
        except BackendError as e:
            logger.error("Backend error: %s", e, exc_info=True)
            yield MessageHandler.ERROR_MESSAGES["backend"]
        except Exception as e:
            logger.error("Unexpected error during streaming: %s", e, exc_info=True)
            yield MessageHandler.ERROR_MESSAGES["unknown"]

    @staticmethod
    async def collect_response(
        messages: list[dict[str, str]],
        model: str = "openai-compatible",
    ) -> str:
        """Collect full chat response from backend (non-streaming).

        Accumulates all streamed tokens into a single response string.
        Useful for scenarios where full response is needed at once.

        Args:
            messages: Chat history with 'role' and 'content' keys
            model: Model identifier (default: openai-compatible)

        Returns:
            Full response string

        Raises:
            BackendError: If backend communication fails
        """
        logger.debug(
            "Collecting full response | messages=%d | model=%s",
            len(messages),
            model,
        )

        response_parts = []
        async for token in MessageHandler.stream_response(messages, model):
            response_parts.append(token)

        full_response = "".join(response_parts)
        logger.debug("Response collected | len=%d", len(full_response))
        return full_response

    @staticmethod
    def handle_error(error: Exception) -> str:
        """Convert exception to user-friendly error message.

        Args:
            error: Exception that occurred

        Returns:
            Italian error message for end user
        """
        logger.error("Handling error: %s", error, exc_info=True)

        if isinstance(error, BackendConnectionError):
            return MessageHandler.ERROR_MESSAGES["connection"]
        elif isinstance(error, StudentNotFoundError):
            return MessageHandler.ERROR_MESSAGES["student_not_found"]
        elif isinstance(error, StreamingError):
            return MessageHandler.ERROR_MESSAGES["streaming"]
        elif isinstance(error, BackendError):
            return MessageHandler.ERROR_MESSAGES["backend"]
        else:
            return MessageHandler.ERROR_MESSAGES["unknown"]

    @staticmethod
    async def send_and_save_response(
        user_message: str,
        messages: list[dict[str, str]],
    ) -> str:
        """Stream response, collect, and save to session history.

        High-level convenience method that:
        1. Streams response (updates UI in real-time)
        2. Collects full response internally
        3. Saves both user message and assistant response to session history

        Args:
            user_message: User's input message
            messages: Full chat history (messages only, excluding current message)

        Returns:
            Full response string
        """
        logger.debug("Sending and saving response | user_len=%d", len(user_message))

        # Append user message to session
        SessionManager.append_to_chat_history("user", user_message)

        # Collect full response
        full_response = await MessageHandler.collect_response(messages)

        # Append assistant response to session
        SessionManager.append_to_chat_history("assistant", full_response)

        logger.debug("Response sent and saved to session history")
        return full_response
