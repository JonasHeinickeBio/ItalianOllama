"""Unit tests for graph module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from italianollama.graph.graph import (
    create_tutor_graph,
    router_node,
    chat_node,
    SOFIA_PERSONA,
)
from italianollama.graph.state import TutorState


class TestRouterNode:
    """Tests for router_node."""

    @pytest.mark.asyncio
    async def test_router_no_level(self):
        """Test routes to placement when no level set."""
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Ciao!"}],
            "level_confidence": 0.0,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        result = await router_node(state)
        
        assert result["router_decision"] == "placement"

    @pytest.mark.asyncio
    async def test_router_placement_keyword(self):
        """Test routes to placement with placement keyword."""
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Voglio fare il test di livello"}],
            "current_level": "A2",
            "level_confidence": 0.8,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        result = await router_node(state)
        
        assert result["router_decision"] == "placement"

    @pytest.mark.asyncio
    async def test_router_vocabulary_keyword(self):
        """Test routes to vocabulary with vocabulary keyword."""
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Facciamo vocabolario"}],
            "current_level": "B1",
            "level_confidence": 0.8,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        result = await router_node(state)
        
        assert result["router_decision"] == "vocabulary"

    @pytest.mark.asyncio
    async def test_router_exercise_type_vocabulary(self):
        """Test routes based on exercise_type."""
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": "B1",
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
        """Test routes based on exercise_type grammar."""
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
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
    async def test_router_translation_keyword(self):
        """Test routes to translation."""
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Come si dice traduzione?"}],
            "current_level": "B1",
            "level_confidence": 0.8,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        result = await router_node(state)
        
        assert result["router_decision"] == "translation"

    @pytest.mark.asyncio
    async def test_router_default_chat(self):
        """Test default route to chat."""
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Ciao! Come stai?"}],
            "current_level": "B1",
            "level_confidence": 0.8,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        result = await router_node(state)
        
        assert result["router_decision"] == "chat"


class TestChatNode:
    """Tests for chat_node."""

    @pytest.mark.asyncio
    async def test_chat_node_basic(self):
        """Test basic chat node."""
        mock_client = MagicMock()
        
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Ciao!"}],
            "level_confidence": 0.0,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        with patch('italianollama.graph.graph.LLMClient') as MockLLM:
            mock_llm = AsyncMock()
            mock_llm.chat = AsyncMock(return_value="Ciao! Come stai?")
            MockLLM.return_value = mock_llm
            
            result = await chat_node(state, mock_client)
            
            assert "response" in result
            assert len(result["messages"]) == 2

    @pytest.mark.asyncio
    async def test_chat_node_error(self):
        """Test chat node handles errors."""
        mock_client = MagicMock()
        
        state: TutorState = {
            "student_id": "test",
            "session_id": "test",
            "messages": [{"role": "user", "content": "Ciao!"}],
            "level_confidence": 0.0,
            "exercise_state": {},
            "response": "",
            "should_continue": True,
        }
        
        with patch('italianollama.graph.graph.LLMClient') as MockLLM:
            mock_llm = AsyncMock()
            mock_llm.chat = AsyncMock(side_effect=ValueError("Test error"))
            MockLLM.return_value = mock_llm
            
            result = await chat_node(state, mock_client)
            
            assert "response" in result
            assert "error" in result["response"].lower()


class TestCreateTutorGraph:
    """Tests for create_tutor_graph."""

    def test_create_tutor_graph(self):
        """Test graph creation."""
        mock_client = MagicMock()
        
        graph = create_tutor_graph(mock_client)
        
        assert graph is not None

    def test_sofia_persona_exists(self):
        """Test Sofia persona is defined."""
        assert SOFIA_PERSONA is not None
        assert "Sofia" in SOFIA_PERSONA
        assert "Italian" in SOFIA_PERSONA
