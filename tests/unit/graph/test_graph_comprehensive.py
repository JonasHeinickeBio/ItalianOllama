"""Comprehensive unit tests for graph components."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from italianollama.graph.state import TutorState, CEFR_LEVELS


class TestTutorState:
    """Tests for TutorState."""

    def test_tutor_state_creation(self):
        """Test TutorState can be created with required fields."""
        state: TutorState = {
            "student_id": "test_student",
            "session_id": "test_session",
            "messages": [],
            "current_level": "A2",
            "level_confidence": 0.8,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        assert state["student_id"] == "test_student"
        assert state["current_level"] == "A2"

    def test_tutor_state_with_messages(self):
        """Test TutorState with message history."""
        state: TutorState = {
            "student_id": "test_student",
            "session_id": "test_session",
            "messages": [
                {"role": "user", "content": "Ciao!"},
                {"role": "assistant", "content": "Ciao! Come stai?"},
            ],
            "current_level": "B1",
            "level_confidence": 0.9,
            "exercise_type": "vocabulary",
            "exercise_state": {"started": True},
            "response": "Test response",
            "should_continue": True,
        }
        assert len(state["messages"]) == 2
        assert state["exercise_type"] == "vocabulary"

    def test_cefr_levels(self):
        """Test CEFR_LEVELS constant."""
        assert "A1" in CEFR_LEVELS
        assert "A2" in CEFR_LEVELS
        assert "B1" in CEFR_LEVELS
        assert "B2" in CEFR_LEVELS
        assert "C1" in CEFR_LEVELS
        assert "C2" in CEFR_LEVELS
        assert len(CEFR_LEVELS) == 6


class TestGraphNodes:
    """Tests for graph node functions."""

    @pytest.fixture
    def mock_neo4j(self):
        """Create a mock Neo4j client."""
        mock = MagicMock()
        mock.get_student_vocabulary = AsyncMock(return_value=[])
        mock.add_vocabulary = AsyncMock()
        mock.set_student_level = AsyncMock()
        mock.record_grammar_error = AsyncMock()
        mock.record_exercise = AsyncMock()
        mock.get_student = AsyncMock(return_value=None)
        mock.get_common_errors = AsyncMock(return_value=[])
        mock.record_niveau_test = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_placement_node_new_student(self, mock_neo4j):
        """Test placement node for new student without level."""
        from italianollama.graph.nodes.placement import placement_node

        state: TutorState = {
            "student_id": "new_student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Voglio imparare l'italiano"}],
            "current_level": None,
            "level_confidence": 0.0,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        with patch("italianollama.graph.nodes.placement.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value=" Qual è il tuo livello attuale di italiano?")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "level": "A2",
                "confidence": 0.8,
                "reasoning": "You can handle basic sentences"
            })
            mock_llm_class.return_value = mock_llm

            result = await placement_node(state, mock_neo4j)

            assert result["should_continue"] is True
            assert "response" in result

    @pytest.mark.asyncio
    async def test_placement_node_existing_level(self, mock_neo4j):
        """Test placement node skips when level exists."""
        from italianollama.graph.nodes.placement import placement_node

        state: TutorState = {
            "student_id": "existing_student",
            "session_id": "session_1",
            "messages": [],
            "current_level": "B1",
            "level_confidence": 0.9,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        result = await placement_node(state, mock_neo4j)

        assert result["current_level"] == "B1"
        assert "B1" in result["response"]

    @pytest.mark.asyncio
    async def test_grammar_node(self, mock_neo4j):
        """Test grammar node functionality."""
        from italianollama.graph.nodes.grammar import grammar_node

        state: TutorState = {
            "student_id": "test_student",
            "session_id": "session_1",
            "messages": [
                {"role": "user", "content": "Io avere fame"}
            ],
            "current_level": "A2",
            "level_confidence": 0.8,
            "exercise_type": "grammar",
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        with patch("italianollama.graph.nodes.grammar.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Grammar exercise: Conjugate the verb 'essere'")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "has_errors": True,
                "errors": [{"original": "avere", "corrected": "ho", "rule": "verb conjugation"}],
                "explanation": "Use 'ho' instead of 'avere' for first person"
            })
            mock_llm_class.return_value = mock_llm

            result = await grammar_node(state, mock_neo4j)

            assert result["should_continue"] is True
            assert "exercise_state" in result

    @pytest.mark.asyncio
    async def test_vocabulary_node(self, mock_neo4j):
        """Test vocabulary node functionality."""
        from italianollama.graph.nodes.vocabulary import vocabulary_node

        mock_neo4j.get_student_vocabulary = AsyncMock(return_value=[
            {"word": "ciao", "translation": "hello", "topic": "greetings", "confidence": 0.5}
        ])

        state: TutorState = {
            "student_id": "test_student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Vocabolo"}],
            "current_level": "A1",
            "level_confidence": 0.7,
            "exercise_type": "vocabulary",
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Let's learn vocabulary!")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "words": [{"italian": "gatto", "english": "cat", "topic": "animals"}]
            })
            mock_llm_class.return_value = mock_llm

            result = await vocabulary_node(state, mock_neo4j)

            assert result["should_continue"] is True

    @pytest.mark.asyncio
    async def test_translation_node(self, mock_neo4j):
        """Test translation node functionality."""
        from italianollama.graph.nodes.translation import translation_node

        state: TutorState = {
            "student_id": "test_student",
            "session_id": "session_1",
            "messages": [
                {"role": "user", "content": "Translate: I love pizza"}
            ],
            "current_level": "A2",
            "level_confidence": 0.8,
            "exercise_type": "translation",
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        with patch("italianollama.graph.nodes.translation.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Translation exercise")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "score": 85,
                "feedback": "Good job!",
                "improvements": ["Consider using 'Adoro' instead of 'Amo'"]
            })
            mock_llm_class.return_value = mock_llm

            result = await translation_node(state, mock_neo4j)

            assert result["should_continue"] is True
            mock_neo4j.record_exercise.assert_called_once()

    @pytest.mark.asyncio
    async def test_free_writing_node(self, mock_neo4j):
        """Test free writing node functionality."""
        from italianollama.graph.nodes.free_writing import free_writing_node

        state: TutorState = {
            "student_id": "test_student",
            "session_id": "session_1",
            "messages": [
                {"role": "user", "content": "Scrivi qualcosa in italiano"}
            ],
            "current_level": "B1",
            "level_confidence": 0.8,
            "exercise_type": "free_writing",
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Writing prompt: Describe your day")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "grammar_issues": [],
                "vocabulary_suggestions": [],
                "overall_score": 80,
                "strengths": ["Good vocabulary"],
                "improvements": ["Use more complex sentences"]
            })
            mock_llm_class.return_value = mock_llm

            result = await free_writing_node(state, mock_neo4j)

            assert result["should_continue"] is True

    @pytest.mark.asyncio
    async def test_niveau_test_node(self, mock_neo4j):
        """Test niveau test node functionality."""
        from italianollama.graph.nodes.niveau_test import niveau_test_node

        state: TutorState = {
            "student_id": "test_student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Voglio fare un test"}],
            "current_level": "B2",
            "level_confidence": 0.9,
            "exercise_type": "niveau",
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="TELC Test - Reading comprehension")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "skill": "reading",
                "score": 75,
                "feedback": "Good comprehension",
                "is_complete": False
            })
            mock_llm_class.return_value = mock_llm

            result = await niveau_test_node(state, mock_neo4j)

            assert result["should_continue"] is True


class TestRouterNode:
    """Tests for router node logic."""

    @pytest.mark.asyncio
    async def test_router_no_level(self):
        """Test router goes to placement when no level."""
        from italianollama.graph.graph import router_node

        state: TutorState = {
            "student_id": "new_student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": None,
            "level_confidence": 0.0,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        result = await router_node(state)
        assert result["router_decision"] == "placement"

    @pytest.mark.asyncio
    async def test_router_placement_keyword(self):
        """Test router detects placement keyword."""
        from italianollama.graph.graph import router_node

        state: TutorState = {
            "student_id": "student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Voglio fare un test di placement"}],
            "current_level": "A2",
            "level_confidence": 0.8,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        result = await router_node(state)
        assert result["router_decision"] == "placement"

    @pytest.mark.asyncio
    async def test_router_vocabulary_keyword(self):
        """Test router detects vocabulary keyword."""
        from italianollama.graph.graph import router_node

        state: TutorState = {
            "student_id": "student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Voglio练习vocabolario"}],
            "current_level": "B1",
            "level_confidence": 0.8,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        result = await router_node(state)
        assert result["router_decision"] == "vocabulary"

    @pytest.mark.asyncio
    async def test_router_exercise_type_vocabulary(self):
        """Test router uses explicit exercise_type."""
        from italianollama.graph.graph import router_node

        state: TutorState = {
            "student_id": "student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": "A2",
            "level_confidence": 0.8,
            "exercise_type": "vocabulary",
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        result = await router_node(state)
        assert result["router_decision"] == "vocabulary"

    @pytest.mark.asyncio
    async def test_router_exercise_type_grammar(self):
        """Test router uses explicit exercise_type for grammar."""
        from italianollama.graph.graph import router_node

        state: TutorState = {
            "student_id": "student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": "B1",
            "level_confidence": 0.8,
            "exercise_type": "grammar",
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        result = await router_node(state)
        assert result["router_decision"] == "grammar"

    @pytest.mark.asyncio
    async def test_router_default_chat(self):
        """Test router defaults to chat."""
        from italianollama.graph.graph import router_node

        state: TutorState = {
            "student_id": "student",
            "session_id": "session_1",
            "messages": [{"role": "user", "content": "Come stai?"}],
            "current_level": "A2",
            "level_confidence": 0.8,
            "exercise_type": None,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }

        result = await router_node(state)
        assert result["router_decision"] == "chat"