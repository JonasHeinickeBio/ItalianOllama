"""Unit tests for graph state."""

import pytest
from italianollama.graph.state import CEFR_LEVELS, TutorState


class TestTutorState:
    """Tests for TutorState TypedDict."""

    def test_tutor_state_empty(self):
        """Test TutorState can be empty (all fields optional)."""
        state: TutorState = {}
        assert state == {}

    def test_tutor_state_full(self):
        """Test TutorState with all fields."""
        state: TutorState = {
            "student_id": "student_123",
            "session_id": "session_456",
            "messages": [
                {"role": "user", "content": "Ciao"},
                {"role": "assistant", "content": "Ciao! Come stai?"},
            ],
            "current_level": "B1",
            "level_confidence": 0.9,
            "exercise_type": "vocabulary",
            "exercise_state": {"started": True, "current_card": 0},
            "response": "Test response",
            "should_continue": True,
        }
        assert state["student_id"] == "student_123"
        assert state["current_level"] == "B1"

    def test_tutor_state_partial(self):
        """Test TutorState with partial fields."""
        state: TutorState = {
            "student_id": "student_123",
            "messages": [{"role": "user", "content": "Hello"}],
        }
        assert state["student_id"] == "student_123"
        assert "current_level" not in state or state.get("current_level") is None


class TestCEFRLevels:
    """Tests for CEFR level constants."""

    def test_cef_levels_count(self):
        """Test there are exactly 6 CEFR levels."""
        assert len(CEFR_LEVELS) == 6

    def test_cef_levels_order(self):
        """Test CEFR levels are in correct order (progression)."""
        assert CEFR_LEVELS == ["A1", "A2", "B1", "B2", "C1", "C2"]

    def test_cef_levels_are_strings(self):
        """Test all CEFR levels are strings."""
        assert all(isinstance(level, str) for level in CEFR_LEVELS)

    def test_cef_levels_are_uppercase(self):
        """Test all CEFR levels are uppercase."""
        assert all(level.isupper() for level in CEFR_LEVELS)

    def test_cef_levels_start_with_letter(self):
        """Test all CEFR levels start with correct letter."""
        assert all(level[0] in "ABC" for level in CEFR_LEVELS)

    def test_cef_levels_have_number(self):
        """Test all CEFR levels have a numeric suffix."""
        assert all(len(level) == 2 for level in CEFR_LEVELS)
        assert all(level[1] in "12" for level in CEFR_LEVELS)
