"""Streaming utilities for OpenAI-compatible SSE responses."""

from collections.abc import AsyncGenerator
import json


async def stream_chat_response(
    message_chunks: AsyncGenerator[str, None],
    model: str = "tutor",
    include_component_prefix: bool = False,
) -> AsyncGenerator[str, None]:
    """Convert message chunks to OpenAI-compatible SSE format.

    Yields SSE-formatted chunks compatible with OpenAI client libraries
    and Chainlit's SSE parser.

    Args:
        message_chunks: Async generator of message text chunks
        model: Model name for response metadata
        include_component_prefix: If True, support __COMPONENT__: prefix

    Yields:
        SSE-formatted strings like: 'data: {...json...}\n\n'

    Example:
        async def stream_llm():
            yield "Hello "
            yield "world"

        async for chunk in stream_chat_response(stream_llm()):
            print(chunk)  # 'data: {"choices": [{"delta": {"content": "Hello "}}]}\n\n'
    """
    try:
        async for chunk in message_chunks:
            if not chunk:
                continue

            # Check for component prefix (for Chainlit)
            if include_component_prefix and chunk.startswith("__COMPONENT__:"):
                # Pass through component data as-is (special format)
                yield f"data: {chunk}\n\n"
            else:
                # Standard OpenAI delta format
                response = {
                    "object": "text_completion.chunk",
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "role": "assistant",
                                "content": chunk,
                            },
                            "finish_reason": None,
                        }
                    ],
                }
                yield f"data: {json.dumps(response)}\n\n"

        # Send completion marker
        yield "data: [DONE]\n\n"

    except Exception as e:
        # Send error in SSE format
        error_response = {
            "object": "error",
            "error": {
                "message": str(e),
                "type": "server_error",
            },
        }
        yield f"data: {json.dumps(error_response)}\n\n"


def format_sse_chunk(content: str, model: str = "tutor") -> str:
    """Format a single message chunk as SSE.

    Args:
        content: Message content
        model: Model name

    Returns:
        SSE-formatted string
    """
    response = {
        "object": "text_completion.chunk",
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": None,
            }
        ],
    }
    return f"data: {json.dumps(response)}\n\n"


def format_sse_done() -> str:
    """Format completion marker as SSE.

    Returns:
        SSE completion string
    """
    return "data: [DONE]\n\n"


def format_sse_component(component_type: str, data: dict) -> str:
    """Format component data for Chainlit.

    Chainlit looks for __COMPONENT__:{type}|{json_data} format.

    Args:
        component_type: Component type (drill_card, grammar_feedback, etc)
        data: Component data as dict

    Returns:
        SSE-formatted component string
    """
    component_str = f"__COMPONENT__:{component_type}|{json.dumps(data)}"
    return f"data: {component_str}\n\n"
