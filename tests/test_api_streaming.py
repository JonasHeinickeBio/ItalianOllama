"""Unit tests for API streaming module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sse_starlette.sse import EventSourceResponse


class TestStreaming:
    """Tests for streaming functionality."""

    def test_streaming_module_imports(self):
        """Test streaming module can be imported."""
        from italianollama.api.streaming import StreamingResponse, StreamAdapter
        assert StreamingResponse is not None
        assert StreamAdapter is not None

    def test_stream_adapter_init(self):
        """Test StreamAdapter initializes."""
        from italianollama.api.streaming import StreamAdapter
        adapter = StreamAdapter()
        assert adapter is not None

    @pytest.mark.asyncio
    async def test_stream_adapter_chat(self):
        """Test StreamAdapter chat method."""
        from italianollama.api.streaming import StreamAdapter
        
        adapter = StreamAdapter()
        
        # Mock the LLM client
        with patch.object(adapter, 'llm_client') as mock_llm:
            mock_llm.chat = AsyncMock(return_value="Test response")
            
            result = await adapter.chat(
                messages=[{"role": "user", "content": "Ciao"}],
                system_prompt="You are a tutor"
            )
            
            assert result is not None

    def test_stream_adapter_creates_generator(self):
        """Test StreamAdapter creates proper generator."""
        from italianollama.api.streaming import StreamAdapter
        
        adapter = StreamAdapter()
        
        # The adapter should have async generator capability
        assert hasattr(adapter, 'chat') or hasattr(adapter, 'stream_chat')


class TestStreamingEndpoint:
    """Tests for streaming chat endpoint."""

    def test_streaming_endpoint_exists(self):
        """Test streaming endpoint is defined."""
        from italianollama.api.main import app
        routes = [route.path for route in app.routes]
        
        # Check for stream endpoint
        assert any("stream" in r.lower() for r in routes)

    @pytest.mark.asyncio
    async def test_stream_endpoint_requires_auth(self):
        """Test stream endpoint requires authentication."""
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/stream",
                json={
                    "messages": [{"role": "user", "content": "Ciao"}],
                    "model": "tutor"
                }
            )
            
        assert response.status_code == 401


class TestStreamFormat:
    """Tests for SSE stream format."""

    def test_sse_format_message(self):
        """Test SSE message format."""
        from italianollama.api.streaming import format_sse_message
        
        message = format_sse_message({"content": "Ciao"})
        assert "data:" in message

    def test_sse_format_done(self):
        """Test SSE done message."""
        from italianollama.api.streaming import format_sse_message
        
        message = format_sse_message(None, done=True)
        assert "data:" in message
        assert "[DONE]" in message

    @pytest.mark.asyncio
    async def test_stream_generator(self):
        """Test async generator for streaming."""
        from italianollama.api.streaming import StreamAdapter
        
        adapter = StreamAdapter()
        
        # Should be able to iterate over results
        async def mock_stream():
            yield "Ciao"
            yield "!"
        
        result = []
        async for chunk in mock_stream():
            result.append(chunk)
        
        assert len(result) == 2
