"""Unit tests for graph nodes."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from italianollama.graph.nodes import (
    placement_node,
    vocabulary_node,
    grammar_node,
    translation_node,
    free_writing_node,
    niveau_test_node,
)
from italianollama.graph.state import CEFR_LEVELS, TutorState


class TestPlacementNode:
    """Tests for the placement node."""

    @pytest.mark.asyncio
    async def test_placement_node_new_student(self, sample_tutor_state_no_level, mock_neo4j_client):
        """Test placement node for a new student without a level."""
        # Clear the level to simulate new student
        state = sample_tutor_state_no_level.copy()

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Qual è il tuo livello di italiano?")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "level": "B1",
                "confidence": 0.85,
                "reasoning": "You can handle intermediate conversations."
            })
            MockLLM.return_value = mock_llm

            result = await placement_node(state, mock_neo4j_client)

        assert "current_level" in result
        assert result.get("level_confidence") is not None

    @pytest.mark.asyncio
    async def test_placement_node_existing_level(self, sample_tutor_state, mock_neo4j_client):
        """Test placement node when student already has a level."""
        state = sample_tutor_state.copy()

        result = await placement_node(state, mock_neo4j_client)

        assert "Il tuo livello attuale è A2" in result.get("response", "")
        assert result.get("should_continue") is True

    @pytest.mark.asyncio
    async def test_placement_node_invalid_level_fallback(self, sample_tutor_state_no_level, mock_neo4j_client):
        """Test placement node handles invalid level from LLM."""
        state = sample_tutor_state_no_level.copy()
        # Need more than 1 message to trigger level parsing logic
        state["messages"] = [
            {"role": "user", "content": "Risposta studente"},
            {"role": "assistant", "content": "Qual è la tua risposta?"}
        ]

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Response")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "level": "INVALID",
                "confidence": 0.5,
                "reasoning": "Test"
            })
            MockLLM.return_value = mock_llm

            result = await placement_node(state, mock_neo4j_client)

        # Should fallback to A1 for invalid level
        assert result.get("current_level") == "A1"

    @pytest.mark.asyncio
    async def test_placement_node_llm_error(self, sample_tutor_state_no_level, mock_neo4j_client):
        """Test placement node handles LLM errors gracefully."""
        state = sample_tutor_state_no_level.copy()

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM Error"))
            mock_llm.chat_with_json = AsyncMock(side_effect=Exception("LLM Error"))
            MockLLM.return_value = mock_llm

            result = await placement_node(state, mock_neo4j_client)

        assert "Mi dispiace" in result.get("response", "")


class TestVocabularyNode:
    """Tests for the vocabulary node."""

    @pytest.mark.asyncio
    async def test_vocabulary_node_new_exercise(self, sample_tutor_state, mock_neo4j_client):
        """Test vocabulary node starts new exercise correctly."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Ecco le flashcards!")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "words": [{"italian": "nuovo", "english": "new", "topic": "general"}]
            })
            MockLLM.return_value = mock_llm

            result = await vocabulary_node(state, mock_neo4j_client)

        assert result.get("exercise_state", {}).get("started") is True
        assert result.get("exercise_state", {}).get("exercise") == "vocabulary"
        assert result.get("should_continue") is True

    @pytest.mark.asyncio
    async def test_vocabulary_node_extracts_new_words(self, sample_tutor_state, mock_neo4j_client):
        """Test vocabulary node extracts new words from user input."""
        state = sample_tutor_state.copy()
        state["messages"] = [
            {"role": "user", "content": "Voglio imparare la parola 'mare' che significa 'sea'"},
            {"role": "assistant", "content": "Ecco le flashcards!"},
        ]

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Ecco le flashcards!")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "words": [{"italian": "mare", "english": "sea", "topic": "travel"}]
            })
            MockLLM.return_value = mock_llm

            result = await vocabulary_node(state, mock_neo4j_client)

        # Verify vocabulary was added
        mock_neo4j_client.add_vocabulary.assert_called()

    @pytest.mark.asyncio
    async def test_vocabulary_node_llm_error(self, sample_tutor_state, mock_neo4j_client):
        """Test vocabulary node handles LLM errors gracefully."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM Error"))
            MockLLM.return_value = mock_llm

            result = await vocabulary_node(state, mock_neo4j_client)

        assert "Mi dispiace" in result.get("response", "")


class TestGrammarNode:
    """Tests for the grammar node."""

    @pytest.mark.asyncio
    async def test_grammar_node_new_exercise(self, sample_tutor_state, mock_neo4j_client):
        """Test grammar node starts new exercise correctly."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Ecco un esercizio di grammatica!")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "has_errors": False,
                "errors": [],
                "explanation": "Corretto!"
            })
            MockLLM.return_value = mock_llm

            result = await grammar_node(state, mock_neo4j_client)

        assert result.get("exercise_state", {}).get("started") is True
        assert result.get("exercise_state", {}).get("exercise") == "grammar"

    @pytest.mark.asyncio
    async def test_grammar_node_records_errors(self, sample_tutor_state, mock_neo4j_client):
        """Test grammar node records grammar errors."""
        state = sample_tutor_state.copy()
        state["messages"] = [
            {"role": "user", "content": "Io avere fame"},  # Grammatical error
            {"role": "assistant", "content": "Ecco un esercizio!"},
        ]

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Correzione: Io ho fame")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "has_errors": True,
                "errors": [{"original": "Io avere", "corrected": "Io ho", "rule": "Present tense of avere"}],
                "explanation": "Use 'ho' instead of 'avere'"
            })
            MockLLM.return_value = mock_llm

            result = await grammar_node(state, mock_neo4j_client)

        # Verify grammar error was recorded
        mock_neo4j_client.record_grammar_error.assert_called()

    @pytest.mark.asyncio
    async def test_grammar_node_llm_error(self, sample_tutor_state, mock_neo4j_client):
        """Test grammar node handles LLM errors gracefully."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM Error"))
            MockLLM.return_value = mock_llm

            result = await grammar_node(state, mock_neo4j_client)

        assert "Mi dispiace" in result.get("response", "")


class TestTranslationNode:
    """Tests for the translation node."""

    @pytest.mark.asyncio
    async def test_translation_node_new_exercise(self, sample_tutor_state, mock_neo4j_client):
        """Test translation node starts new exercise correctly."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.translation.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Translate this sentence:")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "score": 85,
                "feedback": "Good translation!",
                "improvements": ["Minor article issue"]
            })
            MockLLM.return_value = mock_llm

            result = await translation_node(state, mock_neo4j_client)

        assert result.get("exercise_state", {}).get("started") is True
        assert result.get("exercise_state", {}).get("exercise") == "translation"

    @pytest.mark.asyncio
    async def test_translation_node_scores_translation(self, sample_tutor_state, mock_neo4j_client):
        """Test translation node scores user translation."""
        state = sample_tutor_state.copy()
        state["messages"] = [
            {"role": "user", "content": "La casa è grande"},
            {"role": "assistant", "content": "Please translate this to English"},
        ]

        with patch("italianollama.graph.nodes.translation.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Good translation")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "score": 90,
                "feedback": "Perfect!",
                "improvements": []
            })
            MockLLM.return_value = mock_llm

            result = await translation_node(state, mock_neo4j_client)

        # Verify exercise was recorded
        mock_neo4j_client.record_exercise.assert_called()

    @pytest.mark.asyncio
    async def test_translation_node_llm_error(self, sample_tutor_state, mock_neo4j_client):
        """Test translation node handles LLM errors gracefully."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.translation.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM Error"))
            MockLLM.return_value = mock_llm

            result = await translation_node(state, mock_neo4j_client)

        assert "Mi dispiace" in result.get("response", "")


class TestFreeWritingNode:
    """Tests for the free writing node."""

    @pytest.mark.asyncio
    async def test_free_writing_node_new_exercise(self, sample_tutor_state, mock_neo4j_client):
        """Test free writing node starts new exercise correctly."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Scrivi qualcosa in italiano:")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "grammar_issues": [],
                "vocabulary_suggestions": [],
                "overall_score": 80,
                "strengths": ["Good vocabulary"],
                "improvements": ["Work on verb conjugations"]
            })
            MockLLM.return_value = mock_llm

            result = await free_writing_node(state, mock_neo4j_client)

        assert result.get("exercise_state", {}).get("started") is True
        assert result.get("exercise_state", {}).get("exercise") == "free_writing"

    @pytest.mark.asyncio
    async def test_free_writing_node_analyzes_writing(self, sample_tutor_state, mock_neo4j_client):
        """Test free writing node analyzes student writing."""
        state = sample_tutor_state.copy()
        # Need message longer than 50 chars and more than 1 message total
        state["messages"] = [
            {"role": "user", "content": "Oggi vado al mercato per comprare delle mele fresche e delicious"},
            {"role": "assistant", "content": "Scrivi qualcosa!"},
        ]

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Analisi del testo")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "grammar_issues": [],
                "vocabulary_suggestions": [{"word": "mercato", "suggestion": "Consider using 'negozio' too"}],
                "overall_score": 85,
                "strengths": ["Good sentence structure"],
                "improvements": ["Add more adjectives"]
            })
            MockLLM.return_value = mock_llm

            result = await free_writing_node(state, mock_neo4j_client)

        # Verify exercise was recorded
        mock_neo4j_client.record_exercise.assert_called()

    @pytest.mark.asyncio
    async def test_free_writing_node_llm_error(self, sample_tutor_state, mock_neo4j_client):
        """Test free writing node handles LLM errors gracefully."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM Error"))
            MockLLM.return_value = mock_llm

            result = await free_writing_node(state, mock_neo4j_client)

        assert "Mi dispiace" in result.get("response", "")


class TestNiveauTestNode:
    """Tests for the niveau test node."""

    @pytest.mark.asyncio
    async def test_niveau_test_node_new_test(self, sample_tutor_state, mock_neo4j_client):
        """Test niveau test node starts new test correctly."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Iniziamo il test TELC:")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "skill": "reading",
                "score": 75,
                "feedback": "Good understanding",
                "is_complete": False
            })
            MockLLM.return_value = mock_llm

            result = await niveau_test_node(state, mock_neo4j_client)

        assert result.get("exercise_state", {}).get("started") is True
        assert result.get("exercise_state", {}).get("exercise") == "niveau_test"

    @pytest.mark.asyncio
    async def test_niveau_test_node_updates_skills(self, sample_tutor_state, mock_neo4j_client):
        """Test niveau test node updates skill scores."""
        state = sample_tutor_state.copy()
        state["messages"] = [
            {"role": "user", "content": "My answer to reading comprehension"},
            {"role": "assistant", "content": "Test question"},
        ]

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Test response")
            mock_llm.chat_with_json = AsyncMock(return_value={
                "skill": "reading",
                "score": 80,
                "feedback": "Good",
                "is_complete": False
            })
            MockLLM.return_value = mock_llm

            result = await niveau_test_node(state, mock_neo4j_client)

        # Verify test was recorded
        mock_neo4j_client.record_niveau_test.assert_called()

    @pytest.mark.asyncio
    async def test_niveau_test_node_llm_error(self, sample_tutor_state, mock_neo4j_client):
        """Test niveau test node handles LLM errors gracefully."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM Error"))
            MockLLM.return_value = mock_llm

            result = await niveau_test_node(state, mock_neo4j_client)

        assert "Mi dispiace" in result.get("response", "")


class TestCEFRLevels:
    """Tests for CEFR level constants."""

    def test_cef_levels_list(self):
        """Test CEFR levels are defined correctly."""
        assert "A1" in CEFR_LEVELS
        assert "A2" in CEFR_LEVELS
        assert "B1" in CEFR_LEVELS
        assert "B2" in CEFR_LEVELS
        assert "C1" in CEFR_LEVELS
        assert "C2" in CEFR_LEVELS
        assert len(CEFR_LEVELS) == 6
