"""Unit tests for graph state module."""

import pytest
from italianollama.graph.state import TutorState, CEFR_LEVELS


class TestTutorState:
    """Tests for TutorState."""

    def test_cef_levels(self):
        """Test CEFR levels are defined."""
        assert CEFR_LEVELS == ["A1", "A2", "B1", "B2", "C1", "C2"]
        assert len(CEFR_LEVELS) == 6

    def test_tutor_state_minimal(self):
        """Test TutorState with minimal required fields."""
        state: TutorState = {
            "student_id": "student123",
            "session_id": "session456",
            "messages": [],
            "level_confidence": 0.0,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        assert state["student_id"] == "student123"
        assert state["level_confidence"] == 0.0

    def test_tutor_state_full(self):
        """Test TutorState with all fields."""
        state: TutorState = {
            "student_id": "student123",
            "session_id": "session456",
            "messages": [
                {"role": "user", "content": "Ciao!"},
                {"role": "assistant", "content": "Ciao! Come stai?"},
            ],
            "current_level": "B1",
            "level_confidence": 0.85,
            "exercise_type": "vocabulary",
            "exercise_state": {"current_word": "ciao"},
            "response": "Bene, grazie!",
            "should_continue": True,
        }
        
        assert state["current_level"] == "B1"
        assert state["level_confidence"] == 0.85
        assert state["exercise_type"] == "vocabulary"
        assert len(state["messages"]) == 2

    def test_tutor_state_optional_fields(self):
        """Test TutorState optional fields can be None."""
        state: TutorState = {
            "student_id": "student123",
            "session_id": "session456",
            "messages": [],
            "current_level": None,
            "level_confidence": 0.0,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        assert state["current_level"] is None
        assert state["exercise_type"] is None

    def test_cef_level_ordering(self):
        """Test CEFR levels are in correct order."""
        # A1 is beginner, C2 is advanced
        assert CEFR_LEVELS.index("A1") < CEFR_LEVELS.index("A2")
        assert CEFR_LEVELS.index("A2") < CEFR_LEVELS.index("B1")
        assert CEFR_LEVELS.index("B1") < CEFR_LEVELS.index("B2")
        assert CEFR_LEVELS.index("B2") < CEFR_LEVELS.index("C1")
        assert CEFR_LEVELS.index("C1") < CEFR_LEVELS.index("C2")
