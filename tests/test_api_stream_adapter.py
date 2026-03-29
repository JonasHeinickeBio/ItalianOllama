"""Tests for italianollama.api.stream_adapter module."""
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from italianollama.api.stream_adapter import (
    _tokenize_response,
    stream_graph_response,
    stream_llm_response,
    stream_with_components,
)


class TestTokenizeResponse:
    def test_basic_text(self):
        result = _tokenize_response("Hello world")
        assert isinstance(result, list)
        assert len(result) > 0
        combined = "".join(result)
        assert "Hello" in combined
        assert "world" in combined

    def test_empty_string(self):
        result = _tokenize_response("")
        assert result == [""]

    def test_single_word(self):
        result = _tokenize_response("Ciao")
        assert "Ciao" in result

    def test_multiple_words(self):
        result = _tokenize_response("uno due tre")
        joined = "".join(result)
        assert "uno" in joined
        assert "due" in joined
        assert "tre" in joined

    def test_chunk_size(self):
        result = _tokenize_response("a b c", chunk_size=1)
        assert isinstance(result, list)

    def test_preserves_content(self):
        text = "Sono un tutore"
        result = _tokenize_response(text)
        assert "".join(result).replace(" ", "") == text.replace(" ", "")


class TestStreamGraphResponse:
    @pytest.mark.asyncio
    async def test_basic_stream(self):
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(
            return_value={"messages": [{"role": "assistant", "content": "Ciao!"}]}
        )

        chunks = []
        async for chunk in stream_graph_response(mock_graph, {}, "student1", "req1"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert any("[DONE]" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_stream_with_no_messages(self):
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(return_value={"messages": []})

        chunks = []
        async for chunk in stream_graph_response(mock_graph, {}, "s1", "r1"):
            chunks.append(chunk)

        assert any("[DONE]" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_stream_error_handling(self):
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(side_effect=RuntimeError("graph failed"))

        chunks = []
        async for chunk in stream_graph_response(mock_graph, {}, "s1", "r1"):
            chunks.append(chunk)

        assert any("error" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_stream_yields_sse_format(self):
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(
            return_value={"messages": [{"role": "assistant", "content": "Hello world"}]}
        )

        chunks = []
        async for chunk in stream_graph_response(mock_graph, {}, "s1", "r1"):
            chunks.append(chunk)

        data_chunks = [c for c in chunks if c.startswith("data: ") and "[DONE]" not in c]
        assert len(data_chunks) > 0
        for chunk in data_chunks:
            payload = json.loads(chunk[6:])
            assert "choices" in payload

    @pytest.mark.asyncio
    async def test_stream_uses_fallback_message_when_no_assistant(self):
        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(
            return_value={"messages": [{"role": "user", "content": "hello"}]}
        )

        chunks = []
        async for chunk in stream_graph_response(mock_graph, {}, "s1", "r1"):
            chunks.append(chunk)

        # Should have DONE at the end
        assert any("[DONE]" in c for c in chunks)


class TestStreamLlmResponse:
    @pytest.mark.asyncio
    async def test_basic_stream(self):
        async def gen():
            yield type("C", (), {"content": "Hello "})()
            yield type("C", (), {"content": "world"})()

        chunks = []
        async for chunk in stream_llm_response(gen(), "req1"):
            chunks.append(chunk)

        assert any("[DONE]" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_dict_content(self):
        async def gen():
            yield {"content": "Ciao "}
            yield {"content": "mondo"}

        chunks = []
        async for chunk in stream_llm_response(gen(), "req1"):
            chunks.append(chunk)

        assert any("[DONE]" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_empty_content_skipped(self):
        async def gen():
            yield type("C", (), {"content": ""})()
            yield type("C", (), {"content": "hello world"})()

        chunks = []
        async for chunk in stream_llm_response(gen(), "req1"):
            chunks.append(chunk)

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self):
        async def bad_gen():
            yield type("C", (), {"content": "start "})()
            raise ValueError("llm error")

        chunks = []
        async for chunk in stream_llm_response(bad_gen(), "req1"):
            chunks.append(chunk)

        assert any("error" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_string_chunk(self):
        async def gen():
            yield "plain string"

        chunks = []
        async for chunk in stream_llm_response(gen(), "req1"):
            chunks.append(chunk)

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_final_done_sent(self):
        async def gen():
            yield type("C", (), {"content": "hi"})()

        chunks = []
        async for chunk in stream_llm_response(gen(), "req1"):
            chunks.append(chunk)

        assert chunks[-1] == "data: [DONE]\n\n"


class TestStreamWithComponents:
    @pytest.mark.asyncio
    async def test_passthrough(self):
        async def base():
            yield "data: hello\n\n"
            yield "data: [DONE]\n\n"

        chunks = []
        async for chunk in stream_with_components(base(), "req1"):
            chunks.append(chunk)

        assert "data: hello\n\n" in chunks

    @pytest.mark.asyncio
    async def test_component_detected(self):
        async def base():
            yield "data: __COMPONENT__:chart|{}\n\n"

        chunks = []
        async for chunk in stream_with_components(base(), "req1"):
            chunks.append(chunk)

        assert any("__COMPONENT__" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_mixed_content(self):
        async def base():
            yield "prefix__COMPONENT__:chart|{}suffix"

        chunks = []
        async for chunk in stream_with_components(base(), "req1"):
            chunks.append(chunk)

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_error_propagated(self):
        async def bad_base():
            yield "ok"
            raise RuntimeError("stream error")

        with pytest.raises(RuntimeError):
            async for _ in stream_with_components(bad_base(), "req1"):
                pass

    @pytest.mark.asyncio
    async def test_no_component_passthrough(self):
        async def base():
            yield "just normal text"

        chunks = []
        async for chunk in stream_with_components(base(), "req1"):
            chunks.append(chunk)

        assert "just normal text" in chunks
