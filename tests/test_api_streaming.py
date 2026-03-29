"""Tests for italianollama.api.streaming module."""
import json

import pytest

from italianollama.api.streaming import (
    format_sse_chunk,
    format_sse_component,
    format_sse_done,
    stream_chat_response,
)


async def async_gen(*items):
    for item in items:
        yield item


class TestStreamChatResponse:
    @pytest.mark.asyncio
    async def test_basic_chunks(self):
        gen = async_gen("Hello", " world")
        chunks = []
        async for chunk in stream_chat_response(gen):
            chunks.append(chunk)
        # Should have 2 data chunks + DONE
        assert len(chunks) == 3
        assert chunks[-1] == "data: [DONE]\n\n"

    @pytest.mark.asyncio
    async def test_chunk_format(self):
        gen = async_gen("test")
        chunks = []
        async for chunk in stream_chat_response(gen, model="my-model"):
            chunks.append(chunk)
        data = chunks[0]
        assert data.startswith("data: ")
        assert data.endswith("\n\n")
        payload = json.loads(data[6:])
        assert payload["model"] == "my-model"
        assert payload["choices"][0]["delta"]["content"] == "test"
        assert payload["choices"][0]["delta"]["role"] == "assistant"
        assert payload["object"] == "text_completion.chunk"

    @pytest.mark.asyncio
    async def test_empty_chunks_skipped(self):
        gen = async_gen("", "hello", "")
        chunks = []
        async for chunk in stream_chat_response(gen):
            chunks.append(chunk)
        # Only "hello" + DONE
        assert len(chunks) == 2

    @pytest.mark.asyncio
    async def test_done_marker(self):
        gen = async_gen("hi")
        chunks = []
        async for chunk in stream_chat_response(gen):
            chunks.append(chunk)
        assert chunks[-1] == "data: [DONE]\n\n"

    @pytest.mark.asyncio
    async def test_component_prefix_included(self):
        gen = async_gen("__COMPONENT__:chart|{}")
        chunks = []
        async for chunk in stream_chat_response(gen, include_component_prefix=True):
            chunks.append(chunk)
        assert any("__COMPONENT__" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_component_prefix_not_included(self):
        gen = async_gen("__COMPONENT__:chart|{}")
        chunks = []
        async for chunk in stream_chat_response(gen, include_component_prefix=False):
            chunks.append(chunk)
        # Should be wrapped as normal JSON response
        non_done = [c for c in chunks if c != "data: [DONE]\n\n"]
        payload = json.loads(non_done[0][6:])
        assert "choices" in payload

    @pytest.mark.asyncio
    async def test_exception_yields_error(self):
        async def bad_gen():
            yield "start"
            raise ValueError("stream error")

        chunks = []
        async for chunk in stream_chat_response(bad_gen()):
            chunks.append(chunk)
        # Should have error chunk
        error_chunks = [c for c in chunks if "error" in c]
        assert len(error_chunks) > 0

    @pytest.mark.asyncio
    async def test_default_model(self):
        gen = async_gen("hello")
        chunks = []
        async for chunk in stream_chat_response(gen):
            chunks.append(chunk)
        payload = json.loads(chunks[0][6:])
        assert payload["model"] == "tutor"

    @pytest.mark.asyncio
    async def test_empty_generator(self):
        gen = async_gen()
        chunks = []
        async for chunk in stream_chat_response(gen):
            chunks.append(chunk)
        # Only DONE
        assert len(chunks) == 1
        assert chunks[0] == "data: [DONE]\n\n"


class TestFormatSseChunk:
    def test_basic_chunk(self):
        result = format_sse_chunk("hello")
        assert result.startswith("data: ")
        assert result.endswith("\n\n")
        payload = json.loads(result[6:])
        assert payload["choices"][0]["delta"]["content"] == "hello"

    def test_custom_model(self):
        result = format_sse_chunk("test", model="gpt-4")
        payload = json.loads(result[6:])
        assert payload["model"] == "gpt-4"

    def test_finish_reason_none(self):
        result = format_sse_chunk("test")
        payload = json.loads(result[6:])
        assert payload["choices"][0]["finish_reason"] is None

    def test_role_is_assistant(self):
        result = format_sse_chunk("test")
        payload = json.loads(result[6:])
        assert payload["choices"][0]["delta"]["role"] == "assistant"

    def test_object_type(self):
        result = format_sse_chunk("test")
        payload = json.loads(result[6:])
        assert payload["object"] == "text_completion.chunk"


class TestFormatSseDone:
    def test_done_format(self):
        result = format_sse_done()
        assert result == "data: [DONE]\n\n"


class TestFormatSseComponent:
    def test_basic_component(self):
        result = format_sse_component("chart", {"type": "bar"})
        assert result.startswith("data: ")
        assert "__COMPONENT__:chart|" in result
        assert result.endswith("\n\n")

    def test_component_data(self):
        data = {"labels": ["a", "b"], "values": [1, 2]}
        result = format_sse_component("table", data)
        # Extract JSON from component string
        parts = result.replace("data: __COMPONENT__:table|", "").strip()
        parsed = json.loads(parts)
        assert parsed == data

    def test_component_type(self):
        result = format_sse_component("progress", {})
        assert "progress" in result

    def test_component_empty_data(self):
        result = format_sse_component("marker", {})
        assert "__COMPONENT__:marker|{}" in result
