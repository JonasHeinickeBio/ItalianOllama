"""Unit tests for base node (LLM client)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from italianollama.graph.nodes.base import LLMClient, create_llm_client


class TestLLMClient:
    """Tests for the LLM client wrapper."""

    @pytest.fixture
    def llm_client(self):
        """Create an LLM client instance."""
        return LLMClient()

    def test_llm_client_init_default(self):
        """Test LLM client initialization with defaults."""
        client = LLMClient()
        assert client.base_url == "http://litellm:4000"
        assert client.api_key == "dummy"
        assert client.model == "tutor"

    def test_llm_client_init_from_env(self):
        """Test LLM client initialization from environment."""
        with patch.dict(
            "os.environ",
            {
                "LITELLM_BASE_URL": "http://custom:8000",
                "LITELLM_API_KEY": "test_key",
                "LITELLM_MODEL": "gpt-4",
            },
        ):
            client = LLMClient()
            assert client.base_url == "http://custom:8000"
            assert client.api_key == "test_key"
            assert client.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_llm_client_chat(self, llm_client):
        """Test LLM client chat method."""
        messages = [{"role": "user", "content": "Ciao"}]

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Ciao! Come stai?"}}]
            }

            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            MockAsyncClient.return_value = mock_client

            result = await llm_client.chat(messages)

            assert result == "Ciao! Come stai?"

    @pytest.mark.asyncio
    async def test_llm_client_chat_with_system_prompt(self, llm_client):
        """Test LLM client chat with system prompt."""
        messages = [{"role": "user", "content": "Ciao"}]
        system_prompt = "You are a helpful tutor."

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response with system prompt"}}]
            }

            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            MockAsyncClient.return_value = mock_client

            result = await llm_client.chat(messages, system_prompt=system_prompt)

            assert result == "Response with system prompt"

    @pytest.mark.asyncio
    async def test_llm_client_chat_error(self, llm_client):
        """Test LLM client handles errors."""
        messages = [{"role": "user", "content": "Ciao"}]

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            MockAsyncClient.return_value = mock_client

            with pytest.raises(Exception) as exc_info:
                await llm_client.chat(messages)

            assert "LiteLLM error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_llm_client_chat_with_json(self, llm_client):
        """Test LLM client chat with JSON response."""
        messages = [{"role": "user", "content": "Dimmi qualcosa in JSON"}]
        response_schema = {"name": "string", "age": "integer"}

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": '{"name": "Mario", "age": 25}'}}]
            }

            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            MockAsyncClient.return_value = mock_client

            result = await llm_client.chat_with_json(messages, response_schema)

            assert result == {"name": "Mario", "age": 25}

    @pytest.mark.asyncio
    async def test_llm_client_chat_with_json_invalid(self, llm_client):
        """Test LLM client handles invalid JSON."""
        messages = [{"role": "user", "content": "Dimmi qualcosa"}]
        response_schema = {"name": "string"}

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "not valid json"}}]
            }

            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            MockAsyncClient.return_value = mock_client

            with pytest.raises(Exception):
                await llm_client.chat_with_json(messages, response_schema)


class TestCreateLLMClient:
    """Tests for the create_llm_client factory function."""

    def test_create_llm_client(self):
        """Test create_llm_client factory function."""
        client = create_llm_client()
        assert isinstance(client, LLMClient)
        assert client.base_url == "http://litellm:4000"

    def test_create_llm_client_returns_new_instance(self):
        """Test create_llm_client returns new instance each time."""
        client1 = create_llm_client()
        client2 = create_llm_client()
        assert client1 is not client2
