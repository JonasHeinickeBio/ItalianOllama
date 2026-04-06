"""Unit tests for graph nodes and memory modules."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestGraphNodes:
    """Test graph nodes."""

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_placement_node_new_student(self, mock_llm_class):
        """Test placement node for new student."""
        from italianollama.graph.nodes.placement import placement_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="Qual è il tuo nome?")
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": None,
        }
        
        result = await placement_node(state, mock_neo4j)
        
        assert "response" in result
        assert result["should_continue"] is True

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_placement_node_existing_level(self, mock_llm_class):
        """Test placement node when level exists."""
        from italianollama.graph.nodes.placement import placement_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": "B1",
        }
        
        result = await placement_node(state, mock_neo4j)
        
        assert "response" in result
        assert "B1" in result["response"]

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_placement_node_with_json_response(self, mock_llm_class):
        """Test placement node with JSON level response."""
        from italianollama.graph.nodes.placement import placement_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm.chat_with_json = AsyncMock(return_value={
            "level": "A2",
            "confidence": 0.85,
            "reasoning": "Good grammar usage"
        })
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        mock_neo4j.set_student_level = AsyncMock()
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [
                {"role": "user", "content": "Ciao"},
                {"role": "assistant", "content": "Qual è il tuo nome?"},
                {"role": "user", "content": "Mi chiamo Mario"}
            ],
            "current_level": None,
        }
        
        result = await placement_node(state, mock_neo4j)
        
        assert result["current_level"] == "A2"
        mock_neo4j.set_student_level.assert_called_once()


class TestVocabularyNode:
    """Test vocabulary node."""

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_vocabulary_node(self, mock_llm_class):
        """Test vocabulary node."""
        from italianollama.graph.nodes.vocabulary import vocabulary_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="Ecco una flashcard...")
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        mock_neo4j.get_student_vocabulary = AsyncMock(return_value=[])
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [{"role": "user", "content": "Vocabolo"}],
            "current_level": "A2",
            "exercise_state": {},
        }
        
        result = await vocabulary_node(state, mock_neo4j)
        
        assert "response" in result
        assert result["exercise_state"]["started"] is True


class TestGrammarNode:
    """Test grammar node."""

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_grammar_node(self, mock_llm_class):
        """Test grammar node."""
        from italianollama.graph.nodes.grammar import grammar_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="Ecco un esercizio...")
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [{"role": "user", "content": "Grammatica"}],
            "current_level": "B1",
            "exercise_state": {},
        }
        
        result = await grammar_node(state, mock_neo4j)
        
        assert "response" in result
        assert result["exercise_state"]["started"] is True


class TestTranslationNode:
    """Test translation node."""

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_translation_node(self, mock_llm_class):
        """Test translation node."""
        from italianollama.graph.nodes.translation import translation_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="Traduci questa frase...")
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [{"role": "user", "content": "Traduzione"}],
            "current_level": "A2",
            "exercise_state": {},
        }
        
        result = await translation_node(state, mock_neo4j)
        
        assert "response" in result
        assert result["exercise_state"]["started"] is True


class TestFreeWritingNode:
    """Test free writing node."""

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_free_writing_node(self, mock_llm_class):
        """Test free writing node."""
        from italianollama.graph.nodes.free_writing import free_writing_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="Scrivi su questo argomento...")
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [{"role": "user", "content": "Scrivere"}],
            "current_level": "B1",
            "exercise_state": {},
        }
        
        result = await free_writing_node(state, mock_neo4j)
        
        assert "response" in result
        assert result["exercise_state"]["started"] is True


class TestNiveauTestNode:
    """Test niveau test node."""

    @pytest.mark.asyncio
    @patch("italianollama.graph.nodes.base.LLMClient")
    async def test_niveau_test_node(self, mock_llm_class):
        """Test niveau test node."""
        from italianollama.graph.nodes.niveau_test import niveau_test_node
        from italianollama.graph.state import TutorState
        
        mock_llm = MagicMock()
        mock_llm.chat = AsyncMock(return_value="Ecco un esercizio...")
        mock_llm_class.return_value = mock_llm
        
        mock_neo4j = MagicMock()
        
        state: TutorState = {
            "student_id": "test_student",
            "messages": [{"role": "user", "content": "Esame"}],
            "current_level": "B1",
            "exercise_state": {},
        }
        
        result = await niveau_test_node(state, mock_neo4j)
        
        assert "response" in result
        assert result["exercise_state"]["started"] is True
        assert result["exercise_state"]["exercise"] == "niveau_test"


class TestNeo4jClientUnit:
    """Test Neo4j client unit."""

    @pytest.mark.asyncio
    @patch("italianollama.memory.base.AsyncGraphDatabase.driver")
    async def test_set_student_level(self, mock_driver):
        """Test setting student level."""
        from italianollama.memory.neo4j_client import Neo4jClient
        
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        mock_driver_instance = MagicMock()
        mock_driver_instance.session = MagicMock(return_value=mock_session)
        mock_driver.return_value = mock_driver_instance
        
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        await client.connect()
        
        await client.set_student_level("student123", "B1", 0.9)
        
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("italianollama.memory.base.AsyncGraphDatabase.driver")
    async def test_update_vocabulary_confidence(self, mock_driver):
        """Test updating vocabulary confidence."""
        from italianollama.memory.neo4j_client import Neo4jClient
        
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        mock_driver_instance = MagicMock()
        mock_driver_instance.session = MagicMock(return_value=mock_session)
        mock_driver.return_value = mock_driver_instance
        
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        await client.connect()
        
        await client.update_vocabulary_confidence("student123", "ciao", 0.8)
        
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("italianollama.memory.base.AsyncGraphDatabase.driver")
    async def test_record_grammar_error(self, mock_driver):
        """Test recording grammar error."""
        from italianollama.memory.neo4j_client import Neo4jClient
        
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        mock_driver_instance = MagicMock()
        mock_driver_instance.session = MagicMock(return_value=mock_session)
        mock_driver.return_value = mock_driver_instance
        
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        await client.connect()
        
        await client.record_grammar_error(
            student_id="student123",
            original="io sono",
            corrected="io sono",
            rule="verb_conjugation"
        )
        
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("italianollama.memory.base.AsyncGraphDatabase.driver")
    async def test_get_exercise_history(self, mock_driver):
        """Test getting exercise history."""
        from italianollama.memory.neo4j_client import Neo4jClient
        
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.data = AsyncMock(return_value=[
            {"type": "vocabulary", "score": 85, "level": "A2"}
        ])
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        mock_driver_instance = MagicMock()
        mock_driver_instance.session = MagicMock(return_value=mock_session)
        mock_driver.return_value = mock_driver_instance
        
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        await client.connect()
        
        result = await client.get_exercise_history("student123")
        
        assert len(result) == 1

    @pytest.mark.asyncio
    @patch("italianollama.memory.base.AsyncGraphDatabase.driver")
    async def test_get_common_errors(self, mock_driver):
        """Test getting common errors."""
        from italianollama.memory.neo4j_client import Neo4jClient
        
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.data = AsyncMock(return_value=[
            {"rule": "verb_conjugation", "seen_count": 5}
        ])
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.run = AsyncMock(return_value=mock_result)
        
        mock_driver_instance = MagicMock()
        mock_driver_instance.session = MagicMock(return_value=mock_session)
        mock_driver.return_value = mock_driver_instance
        
        client = Neo4jClient(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        await client.connect()
        
        result = await client.get_common_errors("student123")
        
        assert len(result) == 1


class TestStreamAdapter:
    """Test stream adapter module."""

    @pytest.mark.asyncio
    async def test_tokenize_response(self):
        """Test response tokenization."""
        from italianollama.api.stream_adapter import _tokenize_response
        
        result = _tokenize_response("Ciao mondo")
        assert "Ciao" in result
        assert "mondo" in result

    @pytest.mark.asyncio
    async def test_tokenize_response_empty(self):
        """Test tokenization of empty string."""
        from italianollama.api.stream_adapter import _tokenize_response
        
        result = _tokenize_response("")
        assert result == [""]


class TestStreaming:
    """Test streaming utilities."""

    def test_format_sse_chunk(self):
        """Test SSE chunk formatting."""
        from italianollama.api.streaming import format_sse_chunk
        
        result = format_sse_chunk("Hello")
        assert "data:" in result
        assert "Hello" in result

    def test_format_sse_done(self):
        """Test SSE done formatting."""
        from italianollama.api.streaming import format_sse_done
        
        result = format_sse_done()
        assert "DONE" in result

    def test_format_sse_component(self):
        """Test SSE component formatting."""
        from italianollama.api.streaming import format_sse_component
        
        result = format_sse_component("drill_card", {"key": "value"})
        assert "__COMPONENT__" in result
        assert "drill_card" in result
