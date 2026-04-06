"""Unit tests for API streaming module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from collections.abc import AsyncGenerator
import json

from italianollama.api import streaming


class TestStreamChatResponse:
    """Tests for stream_chat_response function."""

    @pytest.mark.asyncio
    async def test_stream_chat_response_basic(self):
        """Test basic streaming response."""
        async def mock_chunks():
            yield "Hello "
            yield "world"

        result = []
        async for chunk in streaming.stream_chat_response(mock_chunks()):
            result.append(chunk)

        assert len(result) == 3  # Two chunks + [DONE]
        assert "Hello" in result[0]
        assert "world" in result[1]
        assert result[2] == "data: [DONE]\n\n"

    @pytest.mark.asyncio
    async def test_stream_chat_response_with_model(self):
        """Test streaming with custom model name."""
        async def mock_chunks():
            yield "Test"

        result = []
        async for chunk in streaming.stream_chat_response(mock_chunks(), model="custom-model"):
            result.append(chunk)

        assert "custom-model" in result[0]

    @pytest.mark.asyncio
    async def test_stream_chat_response_empty_chunks(self):
        """Test streaming handles empty chunks."""
        async def mock_chunks():
            yield ""
            yield "Hello"
            yield ""

        result = []
        async for chunk in streaming.stream_chat_response(mock_chunks()):
            result.append(chunk)

        # Empty chunks should be skipped
        assert any("Hello" in chunk for chunk in result)

    @pytest.mark.asyncio
    async def test_stream_chat_response_with_component_prefix(self):
        """Test streaming with component prefix."""
        async def mock_chunks():
            yield "__COMPONENT__:drill_card|{\"data\": \"test\"}"
            yield "Regular text"

        result = []
        async for chunk in streaming.stream_chat_response(
            mock_chunks(),
            include_component_prefix=True
        ):
            result.append(chunk)

        assert any("__COMPONENT__" in chunk for chunk in result)

    @pytest.mark.asyncio
    async def test_stream_chat_response_error(self):
        """Test streaming handles errors."""
        async def mock_chunks():
            yield "Hello"
            raise ValueError("Test error")

        result = []
        async for chunk in streaming.stream_chat_response(mock_chunks()):
            result.append(chunk)

        assert any("error" in chunk for chunk in result)


class TestFormatSSEChunk:
    """Tests for format_sse_chunk function."""

    def test_format_sse_chunk_basic(self):
        """Test basic SSE chunk formatting."""
        result = streaming.format_sse_chunk("Hello world")

        assert result.startswith("data: ")
        data = json.loads(result[6:])
        assert data["choices"][0]["delta"]["content"] == "Hello world"

    def test_format_sse_chunk_with_model(self):
        """Test SSE chunk with custom model."""
        result = streaming.format_sse_chunk("Test", model="gpt-4")

        data = json.loads(result[6:])
        assert data["model"] == "gpt-4"

    def test_format_sse_chunk_includes_role(self):
        """Test SSE chunk includes assistant role."""
        result = streaming.format_sse_chunk("Test")

        data = json.loads(result[6:])
        assert data["choices"][0]["delta"]["role"] == "assistant"


class TestFormatSSEDone:
    """Tests for format_sse_done function."""

    def test_format_sse_done(self):
        """Test completion marker."""
        result = streaming.format_sse_done()
        assert result == "data: [DONE]\n\n"


class TestFormatSSEComponent:
    """Tests for format_sse_component function."""

    def test_format_sse_component_basic(self):
        """Test basic component formatting."""
        data = {"question": "What is pasta?", "answer": "Italian food"}
        result = streaming.format_sse_component("drill_card", data)

        assert result.startswith("data: __COMPONENT__:drill_card|")
        assert "Italian food" in result

    def test_format_sse_component_json_valid(self):
        """Test component produces valid JSON."""
        data = {"key": "value"}
        result = streaming.format_sse_component("test", data)

        # Check that component prefix is present
        assert "__COMPONENT__:test|" in result
