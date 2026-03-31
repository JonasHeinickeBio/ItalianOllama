"""Unit tests for graph nodes base module with proper mocking."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestLLMClient:
    """Unit tests for LLMClient class."""

    def test_llm_client_init(self):
        """Test LLMClient initialization with custom env."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch.dict('os.environ', {'LITELLM_BASE_URL': 'http://test:4000'}):
            client = LLMClient()
            
            assert client.base_url == "http://test:4000"
            assert client.api_key == "dummy"
            assert client.model == "tutor"

    def test_llm_client_default_env(self):
        """Test LLMClient with default environment."""
        from italianollama.graph.nodes.base import LLMClient
        
        client = LLMClient()
        
        assert client.base_url == "http://litellm:4000"
        assert client.model == "tutor"

    def test_llm_client_custom_model(self):
        """Test LLMClient with custom model."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch.dict('os.environ', {'LITELLM_MODEL': 'gpt-4'}):
            client = LLMClient()
            
            assert client.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_chat_success(self):
        """Test successful chat request."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch('italianollama.graph.nodes.base.httpx.AsyncClient') as mock_httpx_class:
            # Create mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Ciao!"}}]
            }
            
            # Create mock async client
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx_class.return_value = mock_client
            
            client = LLMClient()
            result = await client.chat([{"role": "user", "content": "Ciao"}])
            
            assert result == "Ciao!"

    @pytest.mark.asyncio
    async def test_chat_error(self):
        """Test chat error handling."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch('italianollama.graph.nodes.base.httpx.AsyncClient') as mock_httpx_class:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Error"
            
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx_class.return_value = mock_client
            
            client = LLMClient()
            
            with pytest.raises(Exception) as exc_info:
                await client.chat([{"role": "user", "content": "test"}])
            
            assert "LiteLLM error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_chat_with_system_prompt(self):
        """Test chat with system prompt."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch('italianollama.graph.nodes.base.httpx.AsyncClient') as mock_httpx_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}]
            }
            
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx_class.return_value = mock_client
            
            client = LLMClient()
            result = await client.chat(
                [{"role": "user", "content": "Hello"}],
                system_prompt="You are a helpful tutor."
            )
            
            assert result == "Response"
            
            # Verify post was called with correct messages
            call_args = mock_client.post.call_args
            json_data = call_args.kwargs.get('json', {})
            messages = json_data.get('messages', [])
            assert len(messages) == 2  # system + user
            assert messages[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_chat_with_json(self):
        """Test chat_with_json method."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch('italianollama.graph.nodes.base.httpx.AsyncClient') as mock_httpx_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": '{"key": "value"}'}}]
            }
            
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx_class.return_value = mock_client
            
            client = LLMClient()
            result = await client.chat_with_json(
                [{"role": "user", "content": "Test"}],
                response_schema={"key": "string"}
            )
            
            assert result == {"key": "value"}

    def test_create_llm_client_factory(self):
        """Test factory function creates LLMClient."""
        from italianollama.graph.nodes.base import create_llm_client, LLMClient
        
        client = create_llm_client()
        
        assert isinstance(client, LLMClient)


class TestLLMClientTemperature:
    """Test LLMClient with different temperature settings."""

    @pytest.mark.asyncio
    async def test_chat_default_temperature(self):
        """Test chat uses default temperature."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch('italianollama.graph.nodes.base.httpx.AsyncClient') as mock_httpx_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}]
            }
            
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx_class.return_value = mock_client
            
            client = LLMClient()
            await client.chat([{"role": "user", "content": "test"}])
            
            call_args = mock_client.post.call_args
            json_data = call_args.kwargs.get('json', {})
            assert json_data.get('temperature') == 0.7

    @pytest.mark.asyncio
    async def test_chat_custom_temperature(self):
        """Test chat uses custom temperature."""
        from italianollama.graph.nodes.base import LLMClient
        
        with patch('italianollama.graph.nodes.base.httpx.AsyncClient') as mock_httpx_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}]
            }
            
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx_class.return_value = mock_client
            
            client = LLMClient()
            await client.chat([{"role": "user", "content": "test"}], temperature=0.5)
            
            call_args = mock_client.post.call_args
            json_data = call_args.kwargs.get('json', {})
            assert json_data.get('temperature') == 0.5
