"""Unit tests for the tutor graph."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from italianollama.graph.graph import (
    create_tutor_graph,
    router_node,
    chat_node,
    SOFIA_PERSONA,
)


class TestRouterNode:
    """Tests for the router node."""

    @pytest.mark.asyncio
    async def test_router_no_level(self):
        """Test router routes to placement when no level is set."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": None,
        }

        result = await router_node(state)

        assert result.get("router_decision") == "placement"

    @pytest.mark.asyncio
    async def test_router_placement_request(self):
        """Test router routes to placement on explicit request."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "Voglio fare un test di livello"}],
            "current_level": "A2",
        }

        result = await router_node(state)

        assert result.get("router_decision") == "placement"

    @pytest.mark.asyncio
    async def test_router_grammar(self):
        """Test router routes to grammar when exercise_type is grammar."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": "A2",
            "exercise_type": "grammar",
        }

        result = await router_node(state)

        assert result.get("router_decision") == "grammar"

    @pytest.mark.asyncio
    async def test_router_vocabulary(self):
        """Test router routes to vocabulary."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "Voglio fare esercizi di vocabolario"}],
            "current_level": "A2",
        }

        result = await router_node(state)

        assert result.get("router_decision") == "vocabulary"

    @pytest.mark.asyncio
    async def test_router_translation(self):
        """Test router routes to translation."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "Facciamo una traduzione"}],
            "current_level": "A2",
        }

        result = await router_node(state)

        assert result.get("router_decision") == "translation"

    @pytest.mark.asyncio
    async def test_router_niveau_test(self):
        """Test router routes to niveau test for exam prep."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "exam TELC"}],
            "current_level": "B1",
        }

        result = await router_node(state)

        assert result.get("router_decision") == "niveau_test"

    @pytest.mark.asyncio
    async def test_router_free_writing(self):
        """Test router routes to free writing."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "Voglio scrivere qualcosa"}],
            "current_level": "A2",
        }

        result = await router_node(state)

        assert result.get("router_decision") == "free_writing"

    @pytest.mark.asyncio
    async def test_router_default_chat(self):
        """Test router defaults to chat when no match."""
        state = {
            "student_id": "test",
            "messages": [{"role": "user", "content": "Ciao, come stai?"}],
            "current_level": "B1",
        }

        result = await router_node(state)

        assert result.get("router_decision") == "chat"


class TestChatNode:
    """Tests for the chat node."""

    @pytest.mark.asyncio
    async def test_chat_node(self, sample_tutor_state, mock_neo4j_client):
        """Test chat node returns a response."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.graph.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Ciao! Sono Sofia, la tua tutor di italiano.")
            MockLLM.return_value = mock_llm

            result = await chat_node(state, mock_neo4j_client)

        assert result.get("response") is not None
        assert result.get("should_continue") is False  # Stop by default to prevent infinite loops
        messages = result.get("messages", [])
        assert len(messages) >= len(state["messages"])

    @pytest.mark.asyncio
    async def test_chat_node_error_handling(self, sample_tutor_state, mock_neo4j_client):
        """Test chat node handles errors gracefully."""
        state = sample_tutor_state.copy()

        with patch("italianollama.graph.graph.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(side_effect=Exception("LLM Error"))
            MockLLM.return_value = mock_llm

            result = await chat_node(state, mock_neo4j_client)

        assert "Ciao!" in result.get("response", "")


class TestSofiaPersona:
    """Tests for Sofia persona."""

    def test_sofia_persona_defined(self):
        """Test Sofia persona is defined."""
        assert SOFIA_PERSONA is not None
        assert len(SOFIA_PERSONA) > 0

    def test_sofia_persona_contains_tutor(self):
        """Test Sofia persona mentions tutoring."""
        assert "tutor" in SOFIA_PERSONA.lower()

    def test_sofia_persona_contains_italian(self):
        """Test Sofia persona mentions Italian."""
        assert "italian" in SOFIA_PERSONA.lower()


class TestCreateTutorGraph:
    """Tests for create_tutor_graph function."""

    def test_create_tutor_graph_returns_graph(self, mock_neo4j_client):
        """Test create_tutor_graph returns a compiled graph."""
        graph = create_tutor_graph(mock_neo4j_client)
        assert graph is not None

    def test_create_tutor_graph_with_checkpoint_db(self, mock_neo4j_client):
        """Test create_tutor_graph accepts checkpoint_db parameter."""
        graph = create_tutor_graph(mock_neo4j_client, checkpoint_db=None)
        assert graph is not None