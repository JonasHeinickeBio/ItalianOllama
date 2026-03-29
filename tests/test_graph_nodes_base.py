"""Tests for italianollama.graph.nodes.base module."""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from italianollama.graph.nodes.base import LLMClient, create_llm_client


class TestLLMClientInit:
    def test_defaults(self):
        with patch.dict(os.environ, {}, clear=False):
            client = LLMClient()
        assert client.base_url == os.getenv("LITELLM_BASE_URL", "http://litellm:4000")
        assert client.api_key == os.getenv("LITELLM_API_KEY", "dummy")
        assert client.model == os.getenv("LITELLM_MODEL", "tutor")

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("LITELLM_BASE_URL", "http://custom:8000")
        monkeypatch.setenv("LITELLM_API_KEY", "secret")
        monkeypatch.setenv("LITELLM_MODEL", "gpt-4")
        client = LLMClient()
        assert client.base_url == "http://custom:8000"
        assert client.api_key == "secret"
        assert client.model == "gpt-4"

    def test_default_base_url(self, monkeypatch):
        monkeypatch.delenv("LITELLM_BASE_URL", raising=False)
        monkeypatch.delenv("LITELLM_API_KEY", raising=False)
        monkeypatch.delenv("LITELLM_MODEL", raising=False)
        client = LLMClient()
        assert client.base_url == "http://litellm:4000"
        assert client.api_key == "dummy"
        assert client.model == "tutor"


class TestLLMClientChat:
    @pytest.mark.asyncio
    async def test_basic_chat(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Ciao!"}}]
        }

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.chat(messages=[{"role": "user", "content": "Ciao"}])

        assert result == "Ciao!"

    @pytest.mark.asyncio
    async def test_chat_with_system_prompt(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Reply"}}]
        }

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.chat(
                messages=[{"role": "user", "content": "test"}],
                system_prompt="You are a tutor",
            )

        assert result == "Reply"
        call_args = mock_httpx_client.post.call_args
        sent_messages = call_args.kwargs["json"]["messages"]
        assert sent_messages[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_chat_http_error(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(Exception) as exc_info:
                await client.chat(messages=[{"role": "user", "content": "test"}])
        assert "LiteLLM error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_chat_temperature_and_tokens(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OK"}}]
        }

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.chat(
                messages=[{"role": "user", "content": "test"}],
                temperature=0.5,
                max_tokens=512,
            )

        assert result == "OK"
        call_json = mock_httpx_client.post.call_args.kwargs["json"]
        assert call_json["temperature"] == 0.5
        assert call_json["max_tokens"] == 512

    @pytest.mark.asyncio
    async def test_chat_no_system_prompt(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "no system"}}]
        }

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.chat(messages=[{"role": "user", "content": "hi"}])

        call_json = mock_httpx_client.post.call_args.kwargs["json"]
        # No system message since no system_prompt provided
        assert all(m["role"] != "system" for m in call_json["messages"])


class TestLLMClientChatWithJson:
    @pytest.mark.asyncio
    async def test_basic_json_response(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"level": "B1", "confidence": 0.8}'}}]
        }

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.chat_with_json(
                messages=[{"role": "user", "content": "test"}],
                response_schema={"level": "string", "confidence": "float"},
            )

        assert result == {"level": "B1", "confidence": 0.8}

    @pytest.mark.asyncio
    async def test_json_with_system_prompt(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"result": "ok"}'}}]
        }

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.chat_with_json(
                messages=[{"role": "user", "content": "test"}],
                response_schema={"result": "string"},
                system_prompt="Be precise",
            )

        assert result == {"result": "ok"}

    @pytest.mark.asyncio
    async def test_json_http_error(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "error"

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(Exception) as exc_info:
                await client.chat_with_json(
                    messages=[{"role": "user", "content": "test"}],
                    response_schema={},
                )
        assert "LiteLLM error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_no_system_prompt(self):
        client = LLMClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"key": "value"}'}}]
        }

        mock_httpx_client = AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_class:
            mock_class.return_value.__aenter__ = AsyncMock(return_value=mock_httpx_client)
            mock_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await client.chat_with_json(
                messages=[{"role": "user", "content": "test"}],
                response_schema={"key": "string"},
            )

        assert result == {"key": "value"}


class TestCreateLlmClient:
    def test_creates_llm_client(self):
        client = create_llm_client()
        assert isinstance(client, LLMClient)
