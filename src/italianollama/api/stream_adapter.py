"""Streaming adapter for converting LangGraph output to SSE format.

This module bridges the gap between LangGraph's synchronous/async output
and the OpenAI-compatible streaming format expected by clients like Chainlit.
"""

import asyncio
from collections.abc import AsyncGenerator
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def stream_graph_response(
    graph,
    input_data: dict[str, Any],
    student_id: str,
    request_id: str,
) -> AsyncGenerator[str, None]:
    """Convert LangGraph output to OpenAI-compatible SSE stream.

    Args:
        graph: LangGraph compiled graph
        input_data: Input state for the graph
        student_id: Student ID for logging
        request_id: Request ID for tracking

    Yields:
        SSE-formatted strings (JSON + newlines)
    """
    logger.debug(f"[{request_id}] Starting graph stream for student: {student_id}")

    try:
        # Run graph with streaming
        # Note: LangGraph ainvoke returns the final state, not a stream
        # For true streaming, we'd need to use a callback system
        # For now, we'll mock streaming by yielding tokens one at a time

        # Invoke the graph
        result = await graph.ainvoke(input_data)

        # Extract assistant message
        response_text = "Ciao! Sono il tuo tutore di italiano. Come posso aiutarti oggi?"
        for msg in reversed(result.get("messages", [])):
            if msg.get("role") == "assistant":
                response_text = msg.get("content", response_text)
                break

        logger.debug(f"[{request_id}] Graph returned: {len(response_text)} chars")

        # Yield tokens one at a time to simulate streaming
        # In production, this would integrate with LiteLLM streaming
        for chunk in _tokenize_response(response_text):
            sse_chunk = json.dumps(
                {
                    "choices": [
                        {
                            "delta": {"content": chunk},
                            "index": 0,
                            "finish_reason": None,
                        }
                    ]
                }
            )
            yield f"data: {sse_chunk}\n\n"

            # Small delay to simulate streaming
            await asyncio.sleep(0.01)

        # Send final completion chunk
        logger.debug(f"[{request_id}] Sending completion")
        final_chunk = json.dumps(
            {
                "choices": [
                    {
                        "delta": {"content": ""},
                        "index": 0,
                        "finish_reason": "stop",
                    }
                ]
            }
        )
        yield f"data: {final_chunk}\n\n"

        # Send [DONE] marker
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"[{request_id}] Error in stream: {e}", exc_info=True)
        # Send error chunk
        error_chunk = json.dumps(
            {
                "error": {
                    "message": str(e),
                    "type": "server_error",
                }
            }
        )
        yield f"data: {error_chunk}\n\n"


def _tokenize_response(text: str, chunk_size: int = 1) -> list[str]:
    """Split response into chunks for streaming.

    Simple word-based tokenization to make streaming look natural.

    Args:
        text: Full response text
        chunk_size: Number of tokens per chunk (default 1 for char-by-char)

    Yields:
        Text chunks
    """
    # Split by words first
    words = text.split()
    chunks = []

    for word in words:
        # Add space before word (except first)
        if chunks and not chunks[-1].endswith(" "):
            chunks.append(" ")
        chunks.append(word)

    # Yield chunks
    result = []
    for chunk in chunks:
        result.append(chunk)

    return result if result else [""]


async def stream_llm_response(
    llm_stream,
    request_id: str,
) -> AsyncGenerator[str, None]:
    """Stream LLM response directly from LiteLLM.

    When LiteLLM is configured to use a streaming LLM, this handles
    converting its output to OpenAI-compatible SSE format.

    Args:
        llm_stream: Async iterator from LiteLLM
        request_id: Request ID for tracking

    Yields:
        SSE-formatted strings
    """
    logger.debug(f"[{request_id}] Starting LLM stream")

    try:
        buffer = ""
        async for chunk in llm_stream:
            # Extract content from chunk
            if hasattr(chunk, "content"):
                content = chunk.content
            elif isinstance(chunk, dict) and "content" in chunk:
                content = chunk["content"]
            else:
                content = str(chunk)

            if not content:
                continue

            buffer += content

            # Yield word-sized chunks
            words = buffer.split(" ")
            for word in words[:-1]:
                sse_chunk = json.dumps(
                    {
                        "choices": [
                            {
                                "delta": {"content": word + " "},
                                "index": 0,
                                "finish_reason": None,
                            }
                        ]
                    }
                )
                yield f"data: {sse_chunk}\n\n"

            # Keep last partial word in buffer
            buffer = words[-1] if words else ""

        # Flush buffer
        if buffer:
            sse_chunk = json.dumps(
                {
                    "choices": [
                        {
                            "delta": {"content": buffer},
                            "index": 0,
                            "finish_reason": None,
                        }
                    ]
                }
            )
            yield f"data: {sse_chunk}\n\n"

        # Send completion
        final_chunk = json.dumps(
            {
                "choices": [
                    {
                        "delta": {"content": ""},
                        "index": 0,
                        "finish_reason": "stop",
                    }
                ]
            }
        )
        yield f"data: {final_chunk}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"[{request_id}] Error in LLM stream: {e}", exc_info=True)
        error_chunk = json.dumps(
            {
                "error": {
                    "message": str(e),
                    "type": "server_error",
                }
            }
        )
        yield f"data: {error_chunk}\n\n"


async def stream_with_components(
    base_stream: AsyncGenerator[str, None],
    request_id: str,
) -> AsyncGenerator[str, None]:
    """Enhance stream with Chainlit component support.

    Detects __COMPONENT__: prefix in streamed content and yields
    component data in proper SSE format.

    Args:
        base_stream: Base SSE stream
        request_id: Request ID for tracking

    Yields:
        Enhanced SSE-formatted strings
    """
    logger.debug(f"[{request_id}] Starting component-aware stream")

    component_buffer = ""
    in_component = False

    try:
        async for chunk in base_stream:
            # Check if this chunk starts or contains component marker
            if "__COMPONENT__:" in chunk:
                # Parse component
                parts = chunk.split("__COMPONENT__:")

                # Yield any text before component
                if parts[0]:
                    yield parts[0]

                # Extract component data
                if len(parts) > 1:
                    component_data = parts[1].strip()
                    logger.debug(f"[{request_id}] Component detected: {component_data[:50]}")

                    # Format as component SSE
                    component_sse = f"data: __COMPONENT__:{component_data}\n\n"
                    yield component_sse

                    # Continue with any remaining text
                    if len(parts) > 2:
                        yield parts[2]
            else:
                yield chunk

    except Exception as e:
        logger.error(f"[{request_id}] Error in component stream: {e}", exc_info=True)
        raise
