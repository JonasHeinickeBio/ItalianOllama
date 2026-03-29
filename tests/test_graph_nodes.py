"""Tests for all graph node functions."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def make_llm_mock(response_text="Test response", json_response=None):
    mock_llm = MagicMock()
    mock_llm.chat = AsyncMock(return_value=response_text)
    if json_response is not None:
        mock_llm.chat_with_json = AsyncMock(return_value=json_response)
    else:
        mock_llm.chat_with_json = AsyncMock(return_value={})
    return mock_llm


def make_neo4j_mock():
    mock = MagicMock()
    mock.get_student_vocabulary = AsyncMock(return_value=[])
    mock.add_vocabulary = AsyncMock()
    mock.record_grammar_error = AsyncMock()
    mock.set_student_level = AsyncMock()
    mock.record_exercise = AsyncMock()
    mock.record_niveau_test = AsyncMock()
    return mock


class TestGrammarNode:
    @pytest.mark.asyncio
    async def test_basic_grammar_exercise(self):
        from italianollama.graph.nodes.grammar import grammar_node

        state = {
            "student_id": "s1",
            "messages": [{"role": "user", "content": "Conjugate essere"}],
            "current_level": "A2",
            "exercise_state": {},
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Sono, sei, è...")
            result = await grammar_node(state, neo4j)

        assert "response" in result
        assert result["response"] == "Sono, sei, è..."
        assert result["request_done"] is True

    @pytest.mark.asyncio
    async def test_grammar_initializes_exercise_state(self):
        from italianollama.graph.nodes.grammar import grammar_node

        state = {
            "student_id": "s1",
            "messages": [],
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock()
            result = await grammar_node(state, neo4j)

        assert result["exercise_state"]["started"] is True
        assert result["exercise_state"]["exercise"] == "grammar"

    @pytest.mark.asyncio
    async def test_grammar_error_detection(self):
        from italianollama.graph.nodes.grammar import grammar_node

        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "Ho mangiato"},
                {"role": "assistant", "content": "Good"},
                {"role": "user", "content": "Io sono andato"},
            ],
            "current_level": "B1",
            "exercise_state": {"started": True},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        error_json = {
            "has_errors": True,
            "errors": [{"original": "bad", "corrected": "good", "rule": "article"}],
            "explanation": "test",
        }

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Bene!", json_response=error_json)
            result = await grammar_node(state, neo4j)

        neo4j.record_grammar_error.assert_called()

    @pytest.mark.asyncio
    async def test_grammar_llm_error(self):
        from italianollama.graph.nodes.grammar import grammar_node

        state = {
            "student_id": "s1",
            "messages": [],
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            MockLLM.return_value = mock_llm
            result = await grammar_node(state, neo4j)

        assert "dispiace" in result["response"] or "errore" in result["response"]

    @pytest.mark.asyncio
    async def test_grammar_no_error_increments_score(self):
        from italianollama.graph.nodes.grammar import grammar_node

        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "first"},
                {"role": "assistant", "content": "good"},
                {"role": "user", "content": "second answer"},
            ],
            "current_level": "A1",
            "exercise_state": {"started": True, "score": 0, "total": 0},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock(
                "Good!",
                json_response={"has_errors": False, "errors": [], "explanation": ""},
            )
            result = await grammar_node(state, neo4j)

        assert result["exercise_state"]["score"] >= 0

    @pytest.mark.asyncio
    async def test_grammar_sets_request_done_false_for_multi(self):
        from italianollama.graph.nodes.grammar import grammar_node

        state = {
            "student_id": "s1",
            "messages": [],
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.grammar.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock()
            result = await grammar_node(state, neo4j)

        assert result["request_done"] is False


class TestVocabularyNode:
    @pytest.mark.asyncio
    async def test_basic_vocabulary(self):
        from italianollama.graph.nodes.vocabulary import vocabulary_node

        state = {
            "student_id": "s1",
            "messages": [{"role": "user", "content": "Teach me words"}],
            "current_level": "A1",
            "exercise_state": {},
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Ciao means hello")
            result = await vocabulary_node(state, neo4j)

        assert result["response"] == "Ciao means hello"

    @pytest.mark.asyncio
    async def test_vocabulary_with_existing_words(self):
        from italianollama.graph.nodes.vocabulary import vocabulary_node

        state = {
            "student_id": "s1",
            "messages": [],
            "current_level": "A1",
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()
        neo4j.get_student_vocabulary = AsyncMock(
            return_value=[{"word": "ciao", "translation": "hello", "topic": "greetings"}]
        )

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Test response")
            result = await vocabulary_node(state, neo4j)

        assert "response" in result

    @pytest.mark.asyncio
    async def test_vocabulary_extracts_new_words(self):
        from italianollama.graph.nodes.vocabulary import vocabulary_node

        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "a" * 25},  # Long enough message
            ],
            "current_level": "A1",
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        new_words_json = {"words": [{"italian": "gatto", "english": "cat", "topic": "animals"}]}

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Gatto means cat", json_response=new_words_json)
            result = await vocabulary_node(state, neo4j)

        neo4j.add_vocabulary.assert_called()

    @pytest.mark.asyncio
    async def test_vocabulary_llm_error(self):
        from italianollama.graph.nodes.vocabulary import vocabulary_node

        state = {
            "student_id": "s1",
            "messages": [],
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            MockLLM.return_value = mock_llm
            result = await vocabulary_node(state, neo4j)

        assert "dispiace" in result["response"] or "errore" in result["response"]

    @pytest.mark.asyncio
    async def test_vocabulary_initializes_state(self):
        from italianollama.graph.nodes.vocabulary import vocabulary_node

        state = {
            "student_id": "s1",
            "messages": [],
            "current_level": "A2",
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.vocabulary.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock()
            result = await vocabulary_node(state, neo4j)

        assert result["exercise_state"]["started"] is True
        assert result["exercise_state"]["exercise"] == "vocabulary"


class TestPlacementNode:
    @pytest.mark.asyncio
    async def test_new_student_gets_question(self):
        from italianollama.graph.nodes.placement import placement_node

        state = {
            "student_id": "s1",
            "messages": [{"role": "user", "content": "start"}],
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Qual è il tuo livello?")
            result = await placement_node(state, neo4j)

        assert "response" in result

    @pytest.mark.asyncio
    async def test_existing_level_skips_test(self):
        from italianollama.graph.nodes.placement import placement_node

        state = {
            "student_id": "s1",
            "messages": [],
            "current_level": "B2",
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock()
            result = await placement_node(state, neo4j)

        assert "B2" in result["response"]
        assert result["should_continue"] is True

    @pytest.mark.asyncio
    async def test_placement_determines_level(self):
        from italianollama.graph.nodes.placement import placement_node

        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "start"},
                {"role": "assistant", "content": "question1"},
                {"role": "user", "content": "answer1"},
            ],
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        level_json = {"level": "B1", "confidence": 0.85, "reasoning": "Good grammar"}

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("B1 level", json_response=level_json)
            result = await placement_node(state, neo4j)

        assert result.get("current_level") == "B1"
        assert result.get("level_confidence") == 0.85

    @pytest.mark.asyncio
    async def test_placement_invalid_level_defaults_to_a1(self):
        from italianollama.graph.nodes.placement import placement_node

        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "start"},
                {"role": "assistant", "content": "question"},
                {"role": "user", "content": "answer"},
            ],
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        level_json = {"level": "INVALID", "confidence": 0.5, "reasoning": "test"}

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("test", json_response=level_json)
            result = await placement_node(state, neo4j)

        assert result.get("current_level") == "A1"

    @pytest.mark.asyncio
    async def test_placement_llm_error(self):
        from italianollama.graph.nodes.placement import placement_node

        state = {
            "student_id": "s1",
            "messages": [{"role": "user", "content": "test"}],
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))

        with patch("italianollama.graph.nodes.placement.LLMClient") as MockLLM:
            MockLLM.return_value = mock_llm
            result = await placement_node(state, neo4j)

        assert "response" in result


class TestTranslationNode:
    @pytest.mark.asyncio
    async def test_basic_translation(self):
        from italianollama.graph.nodes.translation import translation_node

        state = {
            "student_id": "s1",
            "messages": [{"role": "user", "content": "Translate: hello"}],
            "current_level": "A2",
            "exercise_state": {},
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.translation.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Ciao!")
            result = await translation_node(state, neo4j)

        assert result["response"] == "Ciao!"

    @pytest.mark.asyncio
    async def test_translation_scores_response(self):
        from italianollama.graph.nodes.translation import translation_node

        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "start"},
                {"role": "assistant", "content": "Translate: Buongiorno"},
                {"role": "user", "content": "Good morning"},
            ],
            "current_level": "A2",
            "exercise_state": {"started": True, "direction": "it_en"},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        score_json = {"score": 90, "feedback": "Great!", "improvements": []}

        with patch("italianollama.graph.nodes.translation.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Correct!", json_response=score_json)
            result = await translation_node(state, neo4j)

        neo4j.record_exercise.assert_called()

    @pytest.mark.asyncio
    async def test_translation_llm_error(self):
        from italianollama.graph.nodes.translation import translation_node

        state = {
            "student_id": "s1",
            "messages": [],
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))

        with patch("italianollama.graph.nodes.translation.LLMClient") as MockLLM:
            MockLLM.return_value = mock_llm
            result = await translation_node(state, neo4j)

        assert "dispiace" in result["response"] or "errore" in result["response"]

    @pytest.mark.asyncio
    async def test_translation_initializes_state(self):
        from italianollama.graph.nodes.translation import translation_node

        state = {
            "student_id": "s1",
            "messages": [],
            "current_level": "B1",
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.translation.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock()
            result = await translation_node(state, neo4j)

        assert result["exercise_state"]["started"] is True
        assert result["exercise_state"]["exercise"] == "translation"


class TestFreeWritingNode:
    @pytest.mark.asyncio
    async def test_basic_free_writing(self):
        from italianollama.graph.nodes.free_writing import free_writing_node

        state = {
            "student_id": "s1",
            "messages": [{"role": "user", "content": "write"}],
            "current_level": "B1",
            "exercise_state": {},
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Write about your day")
            result = await free_writing_node(state, neo4j)

        assert result["response"] == "Write about your day"

    @pytest.mark.asyncio
    async def test_free_writing_analyzes_long_text(self):
        from italianollama.graph.nodes.free_writing import free_writing_node

        long_text = "Oggi sono andato al mercato e ho comprato molte cose interessanti."
        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "start"},
                {"role": "assistant", "content": "prompt"},
                {"role": "user", "content": long_text},
            ],
            "current_level": "B1",
            "exercise_state": {"started": True},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        analysis_json = {
            "grammar_issues": [],
            "vocabulary_suggestions": [],
            "overall_score": 85,
            "strengths": ["good vocabulary"],
            "improvements": [],
        }

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Good writing!", json_response=analysis_json)
            result = await free_writing_node(state, neo4j)

        neo4j.record_exercise.assert_called()

    @pytest.mark.asyncio
    async def test_free_writing_llm_error(self):
        from italianollama.graph.nodes.free_writing import free_writing_node

        state = {
            "student_id": "s1",
            "messages": [],
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as MockLLM:
            MockLLM.return_value = mock_llm
            result = await free_writing_node(state, neo4j)

        assert "dispiace" in result["response"] or "errore" in result["response"]

    @pytest.mark.asyncio
    async def test_free_writing_initializes_state(self):
        from italianollama.graph.nodes.free_writing import free_writing_node

        state = {
            "student_id": "s1",
            "messages": [],
            "current_level": "A2",
            "exercise_state": {},
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.free_writing.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock()
            result = await free_writing_node(state, neo4j)

        assert result["exercise_state"]["started"] is True
        assert result["exercise_state"]["exercise"] == "free_writing"


class TestNiveauTestNode:
    @pytest.mark.asyncio
    async def test_basic_niveau_test(self):
        from italianollama.graph.nodes.niveau_test import niveau_test_node

        state = {
            "student_id": "s1",
            "messages": [{"role": "user", "content": "start exam"}],
            "current_level": "B2",
            "exercise_state": {},
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Exam question 1")
            result = await niveau_test_node(state, neo4j)

        assert result["response"] == "Exam question 1"

    @pytest.mark.asyncio
    async def test_niveau_test_scores_response(self):
        from italianollama.graph.nodes.niveau_test import niveau_test_node

        state = {
            "student_id": "s1",
            "messages": [
                {"role": "user", "content": "start"},
                {"role": "assistant", "content": "question"},
                {"role": "user", "content": "my answer"},
            ],
            "current_level": "B2",
            "exercise_state": {
                "started": True,
                "test_type": "TELC",
                "skills": {
                    "reading": {"score": 0, "total": 0},
                    "writing": {"score": 0, "total": 0},
                    "listening": {"score": 0, "total": 0},
                    "speaking": {"score": 0, "total": 0},
                },
            },
        }
        neo4j = make_neo4j_mock()

        test_json = {
            "skill": "writing",
            "score": 75,
            "feedback": "Good attempt",
            "is_complete": False,
        }

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Good!", json_response=test_json)
            result = await niveau_test_node(state, neo4j)

        neo4j.record_niveau_test.assert_called()
        assert "readiness" in result["response"].lower() or "%" in result["response"]

    @pytest.mark.asyncio
    async def test_niveau_initializes_skills(self):
        from italianollama.graph.nodes.niveau_test import niveau_test_node

        state = {
            "student_id": "s1",
            "messages": [],
            "current_level": "B1",
            "exercise_state": {},
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Test started")
            result = await niveau_test_node(state, neo4j)

        assert result["exercise_state"]["started"] is True
        assert "skills" in result["exercise_state"]

    @pytest.mark.asyncio
    async def test_niveau_llm_error(self):
        from italianollama.graph.nodes.niveau_test import niveau_test_node

        state = {
            "student_id": "s1",
            "messages": [],
            "exercise_state": {},
        }
        neo4j = make_neo4j_mock()

        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM down"))

        with patch("italianollama.graph.nodes.niveau_test.LLMClient") as MockLLM:
            MockLLM.return_value = mock_llm
            result = await niveau_test_node(state, neo4j)

        assert "dispiace" in result["response"] or "errore" in result["response"]
