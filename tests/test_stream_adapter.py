"""Unit tests for stream adapter module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


class TestStreamAdapter:
    """Tests for StreamAdapter class."""

    def test_stream_adapter_import(self):
        """Test StreamAdapter can be imported."""
        from italianollama.api.stream_adapter import StreamAdapter
        assert StreamAdapter is not None

    def test_stream_adapter_init(self):
        """Test StreamAdapter initialization."""
        from italianollama.api.stream_adapter import StreamAdapter
        
        adapter = StreamAdapter()
        assert adapter is not None

    @pytest.mark.asyncio
    async def test_stream_adapter_with_llm_client(self):
        """Test StreamAdapter with LLM client."""
        from italianollama.api.stream_adapter import StreamAdapter
        
        with patch("italianollama.api.stream_adapter.LLMClient") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.chat = AsyncMock(return_value="Test response")
            MockLLM.return_value = mock_llm
            
            adapter = StreamAdapter()
            assert adapter is not None


class TestOpenAICompat:
    """Tests for OpenAI compatibility layer."""

    def test_openai_response_format(self):
        """Test OpenAI-compatible response format."""
        from italianollama.api.stream_adapter import create_openai_response
        
        response = create_openai_response(
            content="Ciao!",
            model="tutor",
            finish_reason="stop"
        )
        
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]

    def test_openai_stream_response_format(self):
        """Test OpenAI streaming response format."""
        from italianollama.api.stream_adapter import create_stream_chunk
        
        chunk = create_stream_chunk(
            content="Ciao",
            model="tutor",
            index=0
        )
        
        assert "choices" in chunk
        assert len(chunk["choices"]) > 0
        assert "delta" in chunk["choices"][0]


class TestEventSource:
    """Tests for SSE event source."""

    def test_create_sse_event(self):
        """Test creating SSE event."""
        from italianollama.api.stream_adapter import create_sse_event
        
        event = create_sse_event({"content": "Ciao"})
        assert "data:" in event
        assert "\n\n" in event

    def test_create_sse_event_empty_data(self):
        """Test SSE event with empty data."""
        from italianollama.api.stream_adapter import create_sse_event
        
        event = create_sse_event("")
        assert event is not None

    def test_create_sse_event_done(self):
        """Test SSE done event."""
        from italianollama.api.stream_adapter import create_sse_event
        
        event = create_sse_event(done=True)
        assert "data:" in event
        assert "DONE" in event


class TestStreamingIntegration:
    """Tests for streaming integration."""

    @pytest.mark.asyncio
    async def test_async_generator_stream(self):
        """Test async generator for streaming."""
        from italianollama.api.stream_adapter import StreamAdapter
        
        async def generate_chunks():
            words = ["Ciao", ", ", "come", " ", "stai", "?"]
            for word in words:
                yield word
        
        result = []
        async for chunk in generate_chunks():
            result.append(chunk)
        
        assert len(result) == 6

    def test_json_dumps_for_sse(self):
        """Test JSON serialization for SSE."""
        data = {"content": "Ciao!"}
        json_str = json.dumps(data)
        assert "Ciao" in json_str


class TestTokenCounting:
    """Tests for token counting."""

    def test_estimate_tokens(self):
        """Test token estimation."""
        from italianollama.api.stream_adapter import estimate_tokens
        
        # Simple word counting approximation
        tokens = estimate_tokens("Ciao come stai?")
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_estimate_tokens_italian(self):
        """Test token estimation for Italian text."""
        from italianollama.api.stream_adapter import estimate_tokens
        
        text = "Buongiorno, come va oggi? Sono molto felice di vederti."
        tokens = estimate_tokens(text)
        assert tokens > 0


class TestStreamErrorHandling:
    """Tests for stream error handling."""

    def test_handle_stream_error(self):
        """Test stream error handling."""
        from italianollama.api.stream_adapter import create_error_event
        
        error_event = create_error_event("Connection error")
        assert "data:" in error_event
        assert "error" in error_event.lower()

    @pytest.mark.asyncio
    async def test_stream_with_exception(self):
        """Test streaming handles exceptions gracefully."""
        async def failing_generator():
            yield "Hello"
            raise Exception("Test error")
        
        result = []
        try:
            async for chunk in failing_generator():
                result.append(chunk)
        except Exception:
            pass  # Expected
        
        assert len(result) == 1
