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

    chainlit run frontend/chainlit_app.py --port 8501

Environment variables (all optional, defaults shown):

- ``BACKEND_URL`` – ``http://localhost:8000``
- ``DEFAULT_STUDENT_ID`` – ``demo``
- ``LOG_LEVEL`` – ``INFO``
"""

import logging

import chainlit as cl

from frontend.api.client import get_student_profile, stream_chat_completions
from frontend.config import get_settings

# ---------------------------------------------------------------------------
# Module setup
# ---------------------------------------------------------------------------

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CEFR level greeting messages
# ---------------------------------------------------------------------------

_CEFR_GREETINGS: dict[str, str] = {
    "A1": (
        "🇮🇹 **Ciao!** Welcome to Sofia, your Italian tutor.\n\n"
        "You are at **A1 (Beginner)** level. We will start with simple words and phrases. "
        "Don't worry – every expert was once a beginner! 😊"
    ),
    "A2": (
        "🇮🇹 **Ciao!** Welcome back to Sofia.\n\n"
        "You are at **A2 (Elementary)** level. You already know the basics – let's build "
        "on that foundation with everyday conversations and vocabulary. 📚"
    ),
    "B1": (
        "🇮🇹 **Buongiorno!** Great to see you on Sofia.\n\n"
        "You are at **B1 (Intermediate)** level. You can handle most everyday situations – "
        "time to refine your grammar and expand your vocabulary! 💪"
    ),
    "B2": (
        "🇮🇹 **Buongiorno!** Welcome to your Sofia session.\n\n"
        "You are at **B2 (Upper-Intermediate)** level. You can communicate fluently – "
        "let's push towards near-native precision and idiomatic expression. 🎯"
    ),
    "C1": (
        "🇮🇹 **Buonasera!** Benvenuto su Sofia.\n\n"
        "You are at **C1 (Advanced)** level. Your Italian is very strong – we will focus "
        "on nuance, style, and complex structures. 🏆"
    ),
    "C2": (
        "🇮🇹 **Buonasera!** Benvenuto su Sofia.\n\n"
        "You are at **C2 (Mastery)** level. You have near-native command of Italian – "
        "let's explore literature, culture, and the subtleties of the language. 🌟"
    ),
}

_GREETING_UNKNOWN = (
    "🇮🇹 **Ciao!** Welcome to Sofia, your personal Italian tutor.\n\n"
    "Your CEFR level has not been determined yet. "
    "Let's start with a quick placement check to tailor the lessons for you! 🎓"
)


def _cefr_greeting(level: str | None) -> str:
    """Return a greeting string matching the student's CEFR *level*."""
    if level:
        return _CEFR_GREETINGS.get(level.upper(), _GREETING_UNKNOWN)
    return _GREETING_UNKNOWN


# ---------------------------------------------------------------------------
# Chainlit lifecycle hooks
# ---------------------------------------------------------------------------


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialise a new student session.

    1. Determine the student ID (from Chainlit session env or default).
    2. Fetch the student profile from the backend.
    3. Store the profile in the Chainlit user session.
    4. Send a CEFR-level greeting.
    """
    # Resolve student ID – Chainlit passes metadata via cl.user_session
    student_id: str = (
        cl.user_session.get("student_id") or settings.default_student_id
    )
    logger.info("Session started for student: %s", student_id)

    # Fetch student profile
    profile = await get_student_profile(student_id)

    if profile is None:
        logger.warning("No profile found for student %s – using defaults", student_id)
        profile = {"student_id": student_id, "name": student_id, "level": None}

    # Store in session for downstream handlers
    cl.user_session.set("student_id", profile.get("student_id", student_id))
    cl.user_session.set("student_name", profile.get("name", student_id))
    cl.user_session.set("student_level", profile.get("level"))
    cl.user_session.set("chat_history", [])

    logger.info(
        "Profile loaded – student=%s level=%s vocab=%s",
        profile.get("student_id"),
        profile.get("level"),
        profile.get("vocab_count", 0),
    )

    # Greet the student
    greeting = _cefr_greeting(profile.get("level"))
    await cl.Message(content=greeting).send()


# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Forward the user's message to the backend and stream the response.

    Args:
        message: Incoming :class:`chainlit.Message` from the student.
    """
    student_id: str = cl.user_session.get("student_id") or settings.default_student_id
    history: list[dict[str, str]] = cl.user_session.get("chat_history") or []

    # Append the new user turn to the running history
    history.append({"role": "user", "content": message.content})

    logger.debug("Sending message to backend – student=%s turns=%d", student_id, len(history))

    # Stream response from the backend
    response_msg = cl.Message(content="")
    await response_msg.send()

    collected: list[str] = []
    try:
        async for token in stream_chat_completions(history):
            collected.append(token)
            await response_msg.stream_token(token)
    except Exception as exc:
        logger.error("Streaming error for student %s: %s", student_id, exc, exc_info=True)
        await response_msg.stream_token(
            "\n\n⚠️ Sorry, I encountered an error. Please try again."
        )
    finally:
        await response_msg.update()

    # Append assistant turn to history
    history.append({"role": "assistant", "content": "".join(collected)})
    cl.user_session.set("chat_history", history)
