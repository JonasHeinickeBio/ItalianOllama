"""HTTP client for the Italian Tutor FastAPI backend.

Provides:
- :func:`get_student_profile` – fetch student metadata from ``GET /students/{id}``.
- :func:`stream_chat_completions` – consume the OpenAI-compatible SSE stream from
  ``POST /v1/chat/completions`` and yield plain-text content tokens.
"""

from collections.abc import AsyncIterator
import json
import logging
from typing import Any

import httpx

from frontend.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Student profile
# ---------------------------------------------------------------------------


async def get_student_profile(student_id: str) -> dict[str, Any] | None:
    """Fetch a student profile from ``GET /students/{student_id}``.

    Args:
        student_id: Identifier of the student to retrieve.

    Returns:
        A dict with keys ``student_id``, ``name``, ``level``, ``level_confidence``,
        ``vocab_count``, ``exercise_count``, and ``created_at``, or ``None`` when
        the student does not exist (404) or the backend is unreachable.
    """
    settings = get_settings()
    url = f"{settings.backend_url}/students/{student_id}"

    try:
        async with httpx.AsyncClient(timeout=settings.backend_timeout) as client:
            response = await client.get(url)

        if response.status_code == 404:
            logger.info("Student not found: %s", student_id)
            return None

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as exc:
        logger.warning("Backend returned %s for %s: %s", exc.response.status_code, url, exc)
        return None
    except httpx.RequestError as exc:
        logger.warning("Could not reach backend at %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# SSE stream parsing
# ---------------------------------------------------------------------------


async def stream_chat_completions(
    messages: list[dict[str, str]],
    model: str = "tutor",
    *,
    extra_headers: dict[str, str] | None = None,
) -> AsyncIterator[str]:
    """Stream chat completions from ``POST /v1/chat/completions`` via SSE.

    Parses the OpenAI-compatible Server-Sent Events response emitted by the
    backend's :func:`stream_chat_response` helper.  Only plain content tokens
    are yielded – the ``[DONE]`` sentinel and component frames are consumed
    silently.  Malformed JSON lines are logged and skipped.

    Args:
        messages: List of ``{"role": ..., "content": ...}`` dicts.
        model: Model name forwarded to the backend.
        extra_headers: Optional additional HTTP headers (e.g. ``Authorization``).

    Yields:
        Decoded content strings as they arrive from the backend.
    """
    settings = get_settings()
    url = f"{settings.backend_url}/v1/chat/completions"
    payload = {"model": model, "messages": messages, "stream": True}
    headers = {"Accept": "text/event-stream", **(extra_headers or {})}

    async with httpx.AsyncClient(timeout=None) as client, client.stream(
        "POST", url, json=payload, headers=headers
    ) as response:
        response.raise_for_status()

        async for line in response.aiter_lines():
            # SSE lines that carry data start with "data: "
            if not line.startswith("data:"):
                continue

            raw = line[len("data:"):].strip()

            # Stream termination sentinel
            if raw == "[DONE]":
                logger.debug("SSE stream finished ([DONE] received)")
                break

            # Component frame – not a plain text token, skip
            if raw.startswith("__COMPONENT__:"):
                logger.debug("SSE component frame skipped: %s", raw[:80])
                continue

            # Decode JSON chunk
            try:
                chunk = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Malformed SSE JSON, skipping line: %r", raw[:120])
                continue

            # Extract delta content (OpenAI chunk format)
            try:
                content: str | None = (
                    chunk["choices"][0]["delta"].get("content")
                )
            except (KeyError, IndexError, TypeError):
                logger.debug("Unexpected SSE chunk structure: %s", chunk)
                continue

            if content:
                yield content
