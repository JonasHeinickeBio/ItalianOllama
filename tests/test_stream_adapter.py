"""Unit tests for stream adapter with mocking."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock


class TestStreamAdapter:
    """Tests for stream_adapter module."""

    @pytest.mark.asyncio
    async def test_stream_graph_response_basic(self):
        """Test basic graph streaming."""
        from italianollama.api.stream_adapter import stream_graph_response

        # Mock the graph
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(
            return_value={
                "messages": [
                    {"role": "user", "content": "Ciao"},
                    {"role": "assistant", "content": "Ciao! Come stai?"},
                ]
            }
        )

        # Collect streamed chunks
        chunks = []
        async for chunk in stream_graph_response(
            mock_graph,
            {"student_id": "test_student", "messages": [{"role": "user", "content": "Ciao"}]},
            "test_student",
            "test_request",
        ):
            chunks.append(chunk)

        # Verify chunks
        assert len(chunks) > 0
        assert any("data: [DONE]" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_graph_response_empty_messages(self):
        """Test graph streaming with empty messages."""
        from italianollama.api.stream_adapter import stream_graph_response

        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(return_value={"messages": []})

        chunks = []
        async for chunk in stream_graph_response(
            mock_graph,
            {"student_id": "test", "messages": []},
            "test",
            "req123",
        ):
            chunks.append(chunk)

        # Should still have default response
        assert any("Ciao!" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_graph_response_error(self):
        """Test graph streaming handles errors."""
        from italianollama.api.stream_adapter import stream_graph_response

        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(side_effect=Exception("Graph error"))

        chunks = []
        async for chunk in stream_graph_response(
            mock_graph,
            {"student_id": "test", "messages": []},
            "test",
            "req123",
        ):
            chunks.append(chunk)

        # Should have error chunk
        assert any("error" in chunk for chunk in chunks)

    def test_tokenize_response_basic(self):
        """Test tokenization of response text."""
        from italianollama.api.stream_adapter import _tokenize_response

        result = _tokenize_response("Ciao mondo")
        
        assert "Ciao" in result
        assert "mondo" in result

    def test_tokenize_response_empty(self):
        """Test tokenization of empty string."""
        from italianollama.api.stream_adapter import _tokenize_response

        result = _tokenize_response("")
        assert result == [""]

    def test_tokenize_response_single_word(self):
        """Test tokenization of single word."""
        from italianollama.api.stream_adapter import _tokenize_response

        result = _tokenize_response("Ciao")
        assert "Ciao" in result

    @pytest.mark.asyncio
    async def test_stream_llm_response_basic(self):
        """Test LLM response streaming."""
        from italianollama.api.stream_adapter import stream_llm_response

        # Mock LLM stream
        async def mock_llm_stream():
            yield "Hello "
            yield "world"

        chunks = []
        async for chunk in stream_llm_response(mock_llm_stream(), "req123"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert any("[DONE]" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_llm_response_error(self):
        """Test LLM response streaming handles errors."""
        from italianollama.api.stream_adapter import stream_llm_response

        async def error_stream():
            yield "Hello"
            raise Exception("LLM error")

        chunks = []
        async for chunk in stream_llm_response(error_stream(), "req123"):
            chunks.append(chunk)

        # Should have error chunk
        assert any("error" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_with_components_basic(self):
        """Test component-aware streaming."""
        from italianollama.api.stream_adapter import stream_with_components

        # Mock base stream with component
        async def mock_base_stream():
            yield "data: Hello __COMPONENT__:test|{\"key\": \"value\"}\n\n"
            yield "data: world\n\n"

        chunks = []
        async for chunk in stream_with_components(mock_base_stream(), "req123"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert any("__COMPONENT__" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_with_components_no_components(self):
        """Test component-aware streaming without components."""
        from italianollama.api.stream_adapter import stream_with_components

        async def mock_base_stream():
            yield "data: Hello world\n\n"

        chunks = []
        async for chunk in stream_with_components(mock_base_stream(), "req123"):
            chunks.append(chunk)

        assert len(chunks) > 0


class TestStreaming:
    """Tests for streaming module."""

    @pytest.mark.asyncio
    async def test_stream_chat_response_basic(self):
        """Test chat response streaming."""
        from italianollama.api.streaming import stream_chat_response

        async def message_chunks():
            yield "Hello "
            yield "world"

        chunks = []
        async for chunk in stream_chat_response(message_chunks()):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert any("choices" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_chat_response_with_components(self):
        """Test chat response with component prefix."""
        from italianollama.api.streaming import stream_chat_response

        async def message_chunks():
            yield "__COMPONENT__:drill_card|{\"type\": \"test\"}"

        chunks = []
        async for chunk in stream_chat_response(
            message_chunks(), include_component_prefix=True
        ):
            chunks.append(chunk)

        assert any("__COMPONENT__" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_stream_chat_response_error(self):
        """Test chat response handles errors."""
        from italianollama.api.streaming import stream_chat_response

        async def error_chunks():
            yield "Hello"
            raise Exception("Test error")

        chunks = []
        async for chunk in stream_chat_response(error_chunks()):
            chunks.append(chunk)

        # Should have error
        assert any("error" in chunk for chunk in chunks)

    def test_format_sse_chunk(self):
        """Test SSE chunk formatting."""
        from italianollama.api.streaming import format_sse_chunk

        result = format_sse_chunk("Hello")
        
        assert "data:" in result
        assert "Hello" in result
        assert "choices" in result

    def test_format_sse_chunk_with_model(self):
        """Test SSE chunk with custom model."""
        from italianollama.api.streaming import format_sse_chunk

        result = format_sse_chunk("Test", model="custom_model")
        
        assert "custom_model" in result

    def test_format_sse_done(self):
        """Test SSE done marker."""
        from italianollama.api.streaming import format_sse_done

        result = format_sse_done()
        
        assert "data: [DONE]" in result

    def test_format_sse_component(self):
        """Test SSE component formatting."""
        from italianollama.api.streaming import format_sse_component

        result = format_sse_component("drill_card", {"key": "value"})
        
        assert "__COMPONENT__" in result
        assert "drill_card" in result
        assert "key" in result
"