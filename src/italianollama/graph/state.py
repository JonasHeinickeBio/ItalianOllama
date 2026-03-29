"""Tutor State - TypedDict for LangGraph state management."""

from typing import TypedDict


class TutorState(TypedDict, total=False):
    """State passed through the tutor graph.

    This defines all the data that flows between nodes in the LangGraph.
    """

    # Student identification
    student_id: str  # Unique student identifier
    session_id: str  # Current session ID

    # Conversation
    messages: list[dict]  # Message history [{"role": "user/assistant", "content": "..."}]

    # Student level & progress
    current_level: str | None  # CEFR level: A1, A2, B1, B2, C1, C2
    level_confidence: float  # Confidence in level assessment (0.0-1.0)

    # Exercise state
    exercise_type: str | None  # Current exercise type
    exercise_state: dict  # State for current exercise

    # Response
    response: str  # Generated response to student
    should_continue: bool  # Whether to continue conversation
