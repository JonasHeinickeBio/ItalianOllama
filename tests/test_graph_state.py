"""Tests for italianollama.graph.state module."""
import pytest

from italianollama.graph.state import CEFR_LEVELS, TutorState


class TestCefrLevels:
    def test_all_levels_present(self):
        assert "A1" in CEFR_LEVELS
        assert "A2" in CEFR_LEVELS
        assert "B1" in CEFR_LEVELS
        assert "B2" in CEFR_LEVELS
        assert "C1" in CEFR_LEVELS
        assert "C2" in CEFR_LEVELS

    def test_level_count(self):
        assert len(CEFR_LEVELS) == 6

    def test_levels_ordered(self):
        assert CEFR_LEVELS.index("A1") < CEFR_LEVELS.index("A2")
        assert CEFR_LEVELS.index("A2") < CEFR_LEVELS.index("B1")
        assert CEFR_LEVELS.index("B1") < CEFR_LEVELS.index("B2")
        assert CEFR_LEVELS.index("B2") < CEFR_LEVELS.index("C1")
        assert CEFR_LEVELS.index("C1") < CEFR_LEVELS.index("C2")

    def test_levels_are_strings(self):
        for level in CEFR_LEVELS:
            assert isinstance(level, str)


class TestTutorState:
    def test_create_empty_state(self):
        state: TutorState = {}
        assert state == {}

    def test_create_full_state(self):
        state: TutorState = {
            "student_id": "student123",
            "session_id": "session456",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": "B1",
            "level_confidence": 0.9,
            "exercise_type": "grammar",
            "exercise_state": {"started": True},
            "response": "Buongiorno!",
            "should_continue": True,
            "single_request": False,
            "request_done": False,
            "router_decision": "grammar",
        }
        assert state["student_id"] == "student123"
        assert state["current_level"] == "B1"

    def test_partial_state(self):
        state: TutorState = {"student_id": "s1"}
        assert "messages" not in state

    def test_state_with_none_level(self):
        state: TutorState = {"current_level": None}
        assert state["current_level"] is None

    def test_state_messages_list(self):
        msgs = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
        state: TutorState = {"messages": msgs}
        assert len(state["messages"]) == 2

    def test_is_typed_dict(self):
        state = dict(student_id="test", messages=[])
        assert state["student_id"] == "test"

    def test_state_is_dict_subtype(self):
        state: TutorState = {"student_id": "s1", "response": "ok"}
        assert isinstance(state, dict)
        assert state.get("response") == "ok"

    def test_state_exercise_state(self):
        state: TutorState = {
            "exercise_state": {"started": True, "score": 5, "total": 10}
        }
        assert state["exercise_state"]["score"] == 5

    def test_state_request_flags(self):
        state: TutorState = {
            "single_request": True,
            "request_done": False,
            "should_continue": True,
        }
        assert state["single_request"] is True
        assert state["request_done"] is False
        assert state["should_continue"] is True
