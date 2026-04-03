"""Unit tests for stream adapter module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from collections.abc import AsyncGenerator
import json

from italianollama.api import stream_adapter


class TestStreamGraphResponse:
    """Tests for stream_graph_response function."""

    @pytest.mark.asyncio
    async def test_stream_graph_response_basic(self):
        """Test basic graph streaming."""
        # Mock graph
        mock_graph = AsyncMock()
        mock_graph.ainvoke = AsyncMock(return_value={
            "messages": [
                {"role": "assistant", "content": "Ciao! Come stai?"}
            ]
        })

        input_data = {
            "student_id": "test-student",
            "messages": [{"role": "user", "content": "Ciao"}],
            "current_level": None,
            "exercise_type": None,
            "exercise_state": {},
        }

        result = []
        async for chunk in stream_adapter.stream_graph_response(
            mock_graph,
            input_data,
            "test-student",
            "test-request-id"
        ):
            result.append(chunk)

        assert len(result) > 0
        assert mock_graph.ainvoke.called

    @pytest.mark.asyncio
    async def test_stream_graph_response_no_messages(self):
        """Test graph streaming with no messages in result."""
        mock_graph = AsyncMock()
        mock_graph.ainvoke = AsyncMock(return_value={
            "messages": []
        })

        input_data = {"student_id": "test", "messages": [], "current_level": None}

        result = []
        async for chunk in stream_adapter.stream_graph_response(
            mock_graph, input_data, "test", "req-1"
        ):
            result.append(chunk)

        # Should fall back to default message
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_stream_graph_response_error(self):
        """Test graph streaming handles errors."""
        mock_graph = AsyncMock()
        mock_graph.ainvoke = AsyncMock(side_effect=ValueError("Graph error"))

        input_data = {"student_id": "test", "messages": [{"role": "user", "content": "Hi"}]}

        result = []
        async for chunk in stream_adapter.stream_graph_response(
            mock_graph, input_data, "test", "req-1"
        ):
            result.append(chunk)

        # Should yield error chunk
        assert any("error" in chunk for chunk in result)


class TestTokenizeResponse:
    """Tests for _tokenize_response function."""

    def test_tokenize_response_basic(self):
        """Test basic tokenization."""
        result = stream_adapter._tokenize_response("Hello world")
        
        assert "Hello" in result
        assert "world" in result

    def test_tokenize_response_single_word(self):
        """Test tokenization of single word."""
        result = stream_adapter._tokenize_response("Hello")
        
        assert "Hello" in result

    def test_tokenize_response_empty(self):
        """Test tokenization of empty string."""
        result = stream_adapter._tokenize_response("")
        
        assert result == [""]

    def test_tokenize_response_multichunk(self):
        """Test tokenization with larger chunk size."""
        result = stream_adapter._tokenize_response("Hello world test", chunk_size=2)
        
        assert len(result) > 0


class TestStreamLLMResponse:
    """Tests for stream_llm_response function."""

    @pytest.mark.asyncio
    async def test_stream_llm_response_basic(self):
        """Test basic LLM streaming."""
        async def mock_stream():
            yield MagicMock(content="Hello ")
            yield MagicMock(content="world")

        result = []
        async for chunk in stream_adapter.stream_llm_response(mock_stream(), "req-1"):
            result.append(chunk)

        assert len(result) > 0
        assert any("Hello" in chunk or "world" in chunk for chunk in result)

    @pytest.mark.asyncio
    async def test_stream_llm_response_dict_content(self):
        """Test LLM streaming with dict content."""
        async def mock_stream():
            yield {"content": "Test message"}

        result = []
        async for chunk in stream_adapter.stream_llm_response(mock_stream(), "req-1"):
            result.append(chunk)

        assert any("Test message" in chunk for chunk in result)

    @pytest.mark.asyncio
    async def test_stream_llm_response_string_content(self):
        """Test LLM streaming with string content."""
        async def mock_stream():
            yield "Direct string"

        result = []
        async for chunk in stream_adapter.stream_llm_response(mock_stream(), "req-1"):
            result.append(chunk)

        assert any("Direct string" in chunk for chunk in result)

    @pytest.mark.asyncio
    async def test_stream_llm_response_empty_content(self):
        """Test LLM streaming skips empty content."""
        async def mock_stream():
            yield MagicMock(content="")
            yield MagicMock(content="Hello")

        result = []
        async for chunk in stream_adapter.stream_llm_response(mock_stream(), "req-1"):
            result.append(chunk)

        # Should contain Hello but not empty content
        assert any("Hello" in chunk for chunk in result)

    @pytest.mark.asyncio
    async def test_stream_llm_response_error(self):
        """Test LLM streaming handles errors."""
        async def mock_stream():
            yield MagicMock(content="Hello")
            raise RuntimeError("LLM error")

        result = []
        async for chunk in stream_adapter.stream_llm_response(mock_stream(), "req-1"):
            result.append(chunk)

        assert any("error" in chunk for chunk in result)


class TestStreamWithComponents:
    """Tests for stream_with_components function."""

    @pytest.mark.asyncio
    async def test_stream_with_components_basic(self):
        """Test basic component streaming."""
        async def mock_stream():
            yield "data: Hello\n\n"
            yield "data: __COMPONENT__:drill_card|{\"key\": \"value\"}\n\n"
            yield "data: World\n\n"

        result = []
        async for chunk in stream_adapter.stream_with_components(mock_stream(), "req-1"):
            result.append(chunk)

        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_stream_with_components_no_components(self):
        """Test stream without components passes through."""
        async def mock_stream():
            yield "data: Hello\n\n"
            yield "data: World\n\n"

        result = []
        async for chunk in stream_adapter.stream_with_components(mock_stream(), "req-1"):
            result.append(chunk)

        assert "Hello" in result[0]
        assert "World" in result[1]

    @pytest.mark.asyncio
    async def test_stream_with_components_multiple(self):
        """Test multiple components in stream."""
        async def mock_stream():
            yield "data: __COMPONENT__:drill_card|{\"a\":1}\n\n"
            yield "data: __COMPONENT__:grammar_feedback|{\"b\":2}\n\n"

        result = []
        async for chunk in stream_adapter.stream_with_components(mock_stream(), "req-1"):
            result.append(chunk)

        assert len(result) == 2
        assert any("drill_card" in chunk for chunk in result)
        assert any("grammar_feedback" in chunk for chunk in result)

    @pytest.mark.asyncio
    async def test_stream_with_components_error(self):
        """Test component streaming handles errors."""
        async def mock_stream():
            yield "data: Hello\n\n"
            raise ValueError("Component error")

        with pytest.raises(ValueError):
            async for _ in stream_adapter.stream_with_components(mock_stream(), "req-1"):
                pass
