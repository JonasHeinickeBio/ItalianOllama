"""Chainlit session management for student profiles and state."""

import logging
from typing import Any

import chainlit as cl

from italianollama.frontend.api import StudentNotFoundError, create_student, get_student_profile

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage student session state and profile data.

    Handles initialization of student profiles, caching of level information,
    and session-specific state management through Chainlit's cl.user_session.
    """

    # Session keys
    STUDENT_ID_KEY = "student_id"
    STUDENT_PROFILE_KEY = "student_profile"
    CHAT_HISTORY_KEY = "chat_history"
    CEFR_LEVEL_KEY = "cefr_level"

    @staticmethod
    async def initialize_session(
        student_id: str | None = None,
        use_demo_fallback: bool = True,
    ) -> dict[str, Any]:
        """Initialize session with student profile.

        Fetches student profile from backend and stores in session.
        If student_id is not provided, uses default from config.
        Auto-creates student if not found.
        Falls back to demo profile if backend unreachable and use_demo_fallback=True.

        Args:
            student_id: Student identifier (optional)
            use_demo_fallback: Use demo profile if backend fails (default: True)

        Returns:
            Student profile dictionary

        Raises:
            Exception: If student creation or profile retrieval fails
        """
        from italianollama.frontend.config import get_settings

        if not student_id:
            student_id = get_settings().default_student_id
            logger.debug("Using default student ID: %s", student_id)

        logger.info("Initializing session for student: %s", student_id)

        try:
            # Try to fetch student profile from backend
            profile = await get_student_profile(student_id)

            # Handle student not found - auto-create
            if profile is None:
                logger.info("Student not found, auto-creating: %s", student_id)
                result = await create_student(student_id, f"Student {student_id}")

                if result is None:
                    logger.error("Failed to auto-create student: %s", student_id)
                    if use_demo_fallback:
                        logger.warning("Falling back to demo profile for: %s", student_id)
                        profile = SessionManager._get_demo_profile(student_id)
                    else:
                        raise StudentNotFoundError(f"Failed to create student: {student_id}")
                else:
                    # Fetch the newly created student profile
                    profile = await get_student_profile(student_id)
                    if profile is None:
                        logger.error("Created student but cannot fetch profile: %s", student_id)
                        if use_demo_fallback:
                            logger.warning("Falling back to demo profile for: %s", student_id)
                            profile = SessionManager._get_demo_profile(student_id)
                        else:
                            raise StudentNotFoundError(
                                f"Student created but profile unavailable: {student_id}"
                            )

                    logger.info("Student auto-created successfully: %s", student_id)

            # Store in session
            cl.user_session.set(SessionManager.STUDENT_ID_KEY, student_id)
            cl.user_session.set(SessionManager.STUDENT_PROFILE_KEY, profile)
            cl.user_session.set(
                SessionManager.CEFR_LEVEL_KEY,
                profile.get("cefr_level"),
            )
            cl.user_session.set(SessionManager.CHAT_HISTORY_KEY, [])

            logger.info(
                "Session initialized for %s | Level: %s",
                student_id,
                profile.get("cefr_level", "unknown"),
            )
            return profile

        except StudentNotFoundError:
            logger.error("Student not found or creation failed: %s", student_id, exc_info=True)
            if use_demo_fallback:
                logger.warning("Using demo profile fallback for: %s", student_id)
                profile = SessionManager._get_demo_profile(student_id)
                cl.user_session.set(SessionManager.STUDENT_ID_KEY, student_id)
                cl.user_session.set(SessionManager.STUDENT_PROFILE_KEY, profile)
                cl.user_session.set(SessionManager.CEFR_LEVEL_KEY, "A1")
                cl.user_session.set(SessionManager.CHAT_HISTORY_KEY, [])
                return profile
            raise
        except Exception as e:
            logger.error(
                "Failed to initialize session: %s",
                e,
                exc_info=True,
            )
            raise

    @staticmethod
    def _get_demo_profile(student_id: str) -> dict[str, Any]:
        """Create a demo student profile for offline/fallback mode.

        Args:
            student_id: Student identifier

        Returns:
            Demo profile dictionary
        """
        return {
            "student_id": student_id,
            "name": f"Student {student_id}",
            "cefr_level": "A1",
            "vocabulary_count": 0,
            "exercise_count": 0,
            "is_demo": True,
            "message": "Using demo mode (backend unavailable)",
        }

    @staticmethod
    def get_student_id() -> str | None:
        """Get student ID from session.

        Returns fallback to config default if not in session.

        Returns:
            Student ID or None
        """
        student_id = cl.user_session.get(SessionManager.STUDENT_ID_KEY)
        if student_id:
            return student_id

        # Fallback to config default
        from italianollama.frontend.config import get_settings

        default_id = get_settings().default_student_id
        logger.debug("Falling back to default student ID: %s", default_id)
        return default_id

    @staticmethod
    def get_student_level() -> str | None:
        """Get CEFR level from session.

        Returns:
            CEFR level (A1-C2) or None
        """
        level = cl.user_session.get(SessionManager.CEFR_LEVEL_KEY)
        logger.debug("Retrieved CEFR level from session: %s", level)
        return level

    @staticmethod
    def get_student_profile() -> dict[str, Any] | None:
        """Get full student profile from session.

        Returns:
            Student profile dictionary or None
        """
        profile = cl.user_session.get(SessionManager.STUDENT_PROFILE_KEY)
        if profile:
            logger.debug(
                "Retrieved student profile from session: %s",
                profile.get("student_id"),
            )
        return profile

    @staticmethod
    def append_to_chat_history(role: str, content: str) -> None:
        """Append message to chat history in session.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        history = cl.user_session.get(SessionManager.CHAT_HISTORY_KEY, [])
        history.append({"role": role, "content": content})
        cl.user_session.set(SessionManager.CHAT_HISTORY_KEY, history)
        logger.debug(
            "Appended message to history | role=%s | len(history)=%d",
            role,
            len(history),
        )

    @staticmethod
    def get_chat_history() -> list[dict[str, str]]:
        """Get full chat history from session.

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        history = cl.user_session.get(SessionManager.CHAT_HISTORY_KEY, [])
        logger.debug("Retrieved chat history | len=%d", len(history))
        return history

    @staticmethod
    def clear_chat_history() -> None:
        """Clear chat history from session."""
        cl.user_session.set(SessionManager.CHAT_HISTORY_KEY, [])
        logger.info("Chat history cleared")

    @staticmethod
    def update_cefr_level(level: str) -> None:
        """Update CEFR level in session.

        Args:
            level: CEFR level (A1-C2)
        """
        cl.user_session.set(SessionManager.CEFR_LEVEL_KEY, level)
        logger.info("Updated CEFR level in session: %s", level)
