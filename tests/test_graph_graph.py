"""Tests for italianollama.graph.graph module."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from italianollama.graph.graph import (
    SOFIA_PERSONA,
    chat_node,
    create_node_wrapper,
    create_tutor_graph,
    router_node,
)
from italianollama.graph.state import TutorState


def make_llm_mock(response="test response"):
    mock = MagicMock()
    mock.chat = AsyncMock(return_value=response)
    return mock


def make_neo4j_mock():
    mock = MagicMock()
    mock.record_grammar_error = AsyncMock()
    mock.record_exercise = AsyncMock()
    mock.set_student_level = AsyncMock()
    mock.get_student_vocabulary = AsyncMock(return_value=[])
    mock.add_vocabulary = AsyncMock()
    mock.record_niveau_test = AsyncMock()
    return mock


class TestRouterNode:
    @pytest.mark.asyncio
    async def test_no_level_routes_to_placement(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "hello"}],
        }
        result = await router_node(state)
        assert result["router_decision"] == "placement"

    @pytest.mark.asyncio
    async def test_grammar_exercise_routes_to_grammar(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "do grammar"}],
            "current_level": "B1",
            "exercise_type": "grammar",
        }
        result = await router_node(state)
        assert result["router_decision"] == "grammar"

    @pytest.mark.asyncio
    async def test_vocabulary_keyword_routes_to_vocabulary(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "show me vocabolario"}],
            "current_level": "A2",
        }
        result = await router_node(state)
        assert result["router_decision"] == "vocabulary"

    @pytest.mark.asyncio
    async def test_translation_exercise_type(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "help me"}],
            "current_level": "B2",
            "exercise_type": "translation",
        }
        result = await router_node(state)
        assert result["router_decision"] == "translation"

    @pytest.mark.asyncio
    async def test_niveau_test_keyword(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "I want certificazione"}],
            "current_level": "C1",
        }
        result = await router_node(state)
        assert result["router_decision"] == "niveau_test"

    @pytest.mark.asyncio
    async def test_free_writing_exercise_type(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "help"}],
            "current_level": "B1",
            "exercise_type": "free_writing",
        }
        result = await router_node(state)
        assert result["router_decision"] == "free_writing"

    @pytest.mark.asyncio
    async def test_default_routes_to_chat(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "hello there"}],
            "current_level": "B1",
        }
        result = await router_node(state)
        assert result["router_decision"] == "chat"

    @pytest.mark.asyncio
    async def test_placement_keyword_in_message(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "do a placement test"}],
            "current_level": "A1",
        }
        result = await router_node(state)
        assert result["router_decision"] == "placement"

    @pytest.mark.asyncio
    async def test_empty_messages(self):
        state: TutorState = {"messages": []}
        result = await router_node(state)
        assert result["router_decision"] == "placement"

    @pytest.mark.asyncio
    async def test_writing_keyword(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "I want writing practice"}],
            "current_level": "B1",
        }
        result = await router_node(state)
        assert result["router_decision"] == "free_writing"

    @pytest.mark.asyncio
    async def test_flashcard_keyword(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "show me some flashcard"}],
            "current_level": "A1",
        }
        result = await router_node(state)
        assert result["router_decision"] == "vocabulary"

    @pytest.mark.asyncio
    async def test_traduzione_keyword(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "help with traduzione"}],
            "current_level": "A2",
        }
        result = await router_node(state)
        assert result["router_decision"] == "translation"

    @pytest.mark.asyncio
    async def test_exam_keyword(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "prepare for exam"}],
            "current_level": "B2",
        }
        result = await router_node(state)
        assert result["router_decision"] == "niveau_test"


class TestChatNode:
    @pytest.mark.asyncio
    async def test_basic_chat(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "Ciao!"}],
            "single_request": True,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.graph.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("Ciao! Come stai?")
            result = await chat_node(state, neo4j)

        assert result["response"] == "Ciao! Come stai?"
        assert result["request_done"] is True
        assert len(result["messages"]) == 2

    @pytest.mark.asyncio
    async def test_chat_appends_message(self):
        state: TutorState = {
            "messages": [{"role": "user", "content": "test"}],
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.graph.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("response")
            result = await chat_node(state, neo4j)

        assert {"role": "assistant", "content": "response"} in result["messages"]

    @pytest.mark.asyncio
    async def test_chat_llm_error(self):
        state: TutorState = {
            "messages": [],
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(side_effect=Exception("LLM error"))

        with patch("italianollama.graph.graph.LLMClient") as MockLLM:
            MockLLM.return_value = mock_llm
            result = await chat_node(state, neo4j)

        resp_lower = result["response"].lower()
        assert "problem" in resp_lower or "dispiace" in resp_lower or "riprova" in resp_lower

    @pytest.mark.asyncio
    async def test_chat_single_request_false(self):
        state: TutorState = {
            "messages": [],
            "single_request": False,
        }
        neo4j = make_neo4j_mock()

        with patch("italianollama.graph.graph.LLMClient") as MockLLM:
            MockLLM.return_value = make_llm_mock("hello")
            result = await chat_node(state, neo4j)

        assert result["request_done"] is False
        assert result["should_continue"] is True


class TestCreateNodeWrapper:
    @pytest.mark.asyncio
    async def test_wrapper_calls_original(self):
        called_with = {}

        async def original_func(state, neo4j):
            called_with["state"] = state
            called_with["neo4j"] = neo4j
            return state

        wrapped = create_node_wrapper(original_func)
        state = {"student_id": "s1"}
        neo4j = make_neo4j_mock()
        result = await wrapped(state, neo4j)

        assert called_with["state"] is state
        assert called_with["neo4j"] is neo4j


class TestCreateTutorGraph:
    def test_creates_graph(self):
        from unittest.mock import patch as _patch
        from langgraph.graph import StateGraph

        neo4j = make_neo4j_mock()
        mock_compiled = MagicMock()
        mock_compiled.ainvoke = AsyncMock(return_value={"messages": []})

        with _patch.object(StateGraph, "compile", return_value=mock_compiled):
            graph = create_tutor_graph(neo4j)

        assert graph is not None

    def test_graph_has_invoke(self):
        from unittest.mock import patch as _patch
        from langgraph.graph import StateGraph

        neo4j = make_neo4j_mock()
        mock_compiled = MagicMock()
        mock_compiled.ainvoke = AsyncMock(return_value={"messages": []})

        with _patch.object(StateGraph, "compile", return_value=mock_compiled):
            graph = create_tutor_graph(neo4j)

        assert hasattr(graph, "ainvoke") or hasattr(graph, "invoke")


class TestSofiaPersona:
    def test_persona_defined(self):
        assert isinstance(SOFIA_PERSONA, str)
        assert len(SOFIA_PERSONA) > 0
        assert "Sofia" in SOFIA_PERSONA

    def test_persona_mentions_italian(self):
        assert "Italian" in SOFIA_PERSONA or "italiano" in SOFIA_PERSONA.lower()
