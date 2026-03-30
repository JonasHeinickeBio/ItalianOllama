"""Sofia – Chainlit-based Italian Tutor chat interface.

Entry-point for the Chainlit frontend.  On session start the app:

1. Retrieves (or falls back gracefully for) the student profile from the
   FastAPI backend.
2. Stores the profile in the Chainlit user session.
3. Greets the student with a CEFR-level–appropriate welcome message.

Subsequent user messages are forwarded to the backend's
``POST /v1/chat/completions`` endpoint via SSE streaming and the tokens are
streamed back into the Chainlit UI in real time.

Run locally (without Docker)::

    poetry install
    chainlit run src/italianollama/frontend/chainlit_app.py --port 8501

Environment variables (all optional, defaults shown):

- ``BACKEND_URL`` – ``http://localhost:8000``
- ``BACKEND_TIMEOUT`` – ``240``
- ``DEFAULT_STUDENT_ID`` – ``demo``
- ``CHAT_PLACEHOLDER`` – ``Scrivi il tuo messaggio qui...`` (Italian)
- ``LOG_LEVEL`` – ``INFO``

## Architecture

Uses modular components from italianollama.frontend.ui:

- **CEFRGreeter**: CEFR level-aware greetings
- **SessionManager**: Student profile and chat history management
- **MessageHandler**: Backend communication, streaming, and error handling
"""

import logging

import chainlit as cl

from italianollama.frontend.config import get_settings
from italianollama.frontend.ui import (
    CEFRGreeter,
    MessageHandler,
    SessionManager,
)

# ---------------------------------------------------------------------------
# Module setup
# ---------------------------------------------------------------------------

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

logger.info("Sofia initialized | version=%s", "1.0.0")


# ---------------------------------------------------------------------------
# Chainlit lifecycle hooks
# ---------------------------------------------------------------------------


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize a new student session.

    1. Load student profile from backend (with fallback to defaults)
    2. Store profile in Chainlit user session
    3. Send CEFR-level appropriate greeting
    """
    logger.info("Starting new chat session")

    try:
        # Initialize session - fetches profile, stores in session
        profile = await SessionManager.initialize_session()

        logger.info(
            "Session initialized | student=%s | level=%s",
            profile.get("student_id"),
            profile.get("cefr_level"),
        )

        # Generate and send greeting
        level = SessionManager.get_student_level()
        greeting = CEFRGreeter.get_greeting(level)

        await cl.Message(content=greeting).send()
        logger.debug("Greeting sent | level=%s", level)

    except Exception as e:
        logger.error("Failed to initialize session: %s", e, exc_info=True)
        error_msg = (
            "🔌 Mi dispiace, non riesco a connettermi al server. "
            "Per favore, riprova tra qualche istante."
        )
        await cl.Message(content=error_msg).send()


# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Forward user message to backend and stream response.

    1. Append user message to chat history
    2. Stream response tokens from backend to UI
    3. Append full response to chat history

    Args:
        message: Incoming Chainlit message from the student
    """
    user_content = message.content
    student_id = SessionManager.get_student_id()

    logger.debug(
        "Received message | student=%s | len=%d",
        student_id,
        len(user_content),
    )

    # Get current history (excluding this message)
    history = SessionManager.get_chat_history()

    # Append user message to session history
    SessionManager.append_to_chat_history("user", user_content)

    # Add to history for API call
    api_history = history + [{"role": "user", "content": user_content}]

    # Stream response to UI
    response_msg = cl.Message(content="")
    await response_msg.send()

    collected_tokens = []
    try:
        # Stream tokens from backend
        async for token in MessageHandler.stream_response(api_history):
            collected_tokens.append(token)
            await response_msg.stream_token(token)

        # Append full response to session history
        full_response = "".join(collected_tokens)
        SessionManager.append_to_chat_history("assistant", full_response)

        logger.debug(
            "Message completed | student=%s | response_len=%d",
            student_id,
            len(full_response),
        )

    except Exception as e:
        logger.error(
            "Error streaming message for %s: %s",
            student_id,
            e,
            exc_info=True,
        )
        error_response = MessageHandler.handle_error(e)
        await response_msg.stream_token(f"\n\n{error_response}")

    finally:
        await response_msg.update()


# ---------------------------------------------------------------------------
# Optional: Chat configuration
# ---------------------------------------------------------------------------


@cl.on_settings_update
async def setup_agent(settings_dict):
    """Handle settings updates from Chainlit UI."""
    logger.info("Settings updated: %s", settings_dict)


# Chainlit UI customization (optional)
chat_settings = [
    cl.Slider(
        id="temperature",
        label="Temperature",
        value=0.7,
        min=0,
        max=1,
        step=0.1,
        tooltip="Controls response randomness (lower = more predictable)",
    ),
]
