"""HTTP client for Italian Tutor FastAPI backend.

Functions:
- get_student_profile: Fetch student metadata via GET /students/{id}
- get_auth_token: Generate JWT token via POST /auth/token
- stream_chat_completions: Stream responses from POST /v1/chat/completions via SSE
"""

import asyncio
from collections.abc import AsyncIterator
import json
import logging
from typing import Any

import httpx

from italianollama.frontend.config import get_settings

from .errors import BackendConnectionError, BackendError, StreamingError, StudentNotFoundError

logger = logging.getLogger(__name__)


class BackendClient:
    """Async HTTP client for backend API.

    Handles connection pooling, timeout, error handling, logging, and retries.
    Designed for use in async context (Chainlit environment).
    """

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        """Initialize client with timeout and retry configuration.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async client (lazy initialization).

        Returns:
            httpx.AsyncClient: Shared async client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _retry_with_backoff(self, coro, operation: str = "request"):
        """Execute async operation with exponential backoff retry logic.

        Args:
            coro: Async coroutine to execute
            operation: Operation name for logging

        Returns:
            Result of the coroutine

        Raises:
            BackendConnectionError: If all retries exhausted
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return await coro()
            except httpx.RequestError as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    wait_time = 2**attempt  # Exponential backoff: 1, 2, 4 seconds
                    logger.warning(
                        f"{operation} attempt {attempt + 1}/{self.max_retries} failed, "
                        f"retrying in {wait_time}s: {exc}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"{operation} failed after {self.max_retries} retries: {exc}")
            except httpx.HTTPStatusError as exc:
                # Don't retry on 4xx errors (except 429)
                if 400 <= exc.response.status_code < 500 and exc.response.status_code != 429:
                    raise
                last_error = exc
                if attempt < self.max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(
                        f"{operation} attempt {attempt + 1}/{self.max_retries} failed "
                        f"(status {exc.response.status_code}), retrying in {wait_time}s"
                    )
                    await asyncio.sleep(wait_time)

        if last_error:
            raise BackendConnectionError(
                f"Backend unreachable after {self.max_retries} retries"
            ) from last_error
        raise BackendConnectionError(f"{operation} failed")

    async def get_student_profile(self, student_id: str) -> dict[str, Any] | None:
        """Fetch student profile from backend with retries.

        Args:
            student_id: Student identifier

        Returns:
            Student profile dict or None if not found

        Raises:
            BackendConnectionError: If backend is unreachable
        """
        settings = get_settings()
        url = f"{settings.backend_url}/students/{student_id}"

        async def fetch():
            client = await self._get_client()
            return await client.get(url)

        try:
            response = await self._retry_with_backoff(
                fetch, operation=f"get_student_profile({student_id})"
            )

            if response.status_code == 404:
                logger.info("Student not found: %s", student_id)
                raise StudentNotFoundError(f"Student {student_id} not found")

            response.raise_for_status()
            logger.debug("Student profile retrieved: %s", student_id)
            return response.json()

        except httpx.HTTPStatusError as exc:
            logger.warning("Backend error %d for %s: %s", exc.response.status_code, url, exc)
            raise BackendError(f"Backend returned {exc.response.status_code}") from exc
        except BackendConnectionError:
            raise

    async def create_student(self, student_id: str, name: str) -> dict[str, Any] | None:
        """Create a new student in the backend with retries.

        Args:
            student_id: Unique student identifier
            name: Student's name

        Returns:
            Student creation response or None on error
        """
        settings = get_settings()
        url = f"{settings.backend_url}/students"
        payload = {"student_id": student_id, "name": name}

        async def create():
            client = await self._get_client()
            return await client.post(url, json=payload)

        try:
            response = await self._retry_with_backoff(
                create, operation=f"create_student({student_id})"
            )
            response.raise_for_status()
            logger.info("Student created: %s", student_id)
            return response.json()

        except httpx.HTTPStatusError as exc:
            logger.warning("Failed to create student %s: %s", student_id, exc)
            raise BackendError(f"Failed to create student: {exc.response.status_code}") from exc
        except BackendConnectionError:
            raise

    async def get_auth_token(self, student_id: str) -> str | None:
        """Generate JWT authentication token.

        Args:
            student_id: Student identifier

        Returns:
            JWT access token or None on error
        """
        settings = get_settings()
        url = f"{settings.backend_url}/auth/token"
        payload = {"student_id": student_id}

        try:
            client = await self._get_client()
            response = await client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            token = data.get("access_token")
            logger.debug("Token generated for student: %s", student_id)
            return token

        except httpx.HTTPError as exc:
            logger.warning("Failed to generate token for %s: %s", student_id, exc)
            return None

    async def stream_chat_completions(
        self,
        messages: list[dict[str, str]],
        model: str = "tutor",
        extra_headers: dict[str, str] | None = None,
    ) -> AsyncIterator[str]:
        """Stream chat completions via SSE (Server-Sent Events).

        Args:
            messages: List of {"role": ..., "content": ...} message dicts
            model: Model name to send to backend
            extra_headers: Optional additional HTTP headers

        Yields:
            Content tokens as they arrive

        Raises:
            StreamingError: If SSE parsing fails
        """
        settings = get_settings()
        url = f"{settings.backend_url}/v1/chat/completions"
        payload = {"model": model, "messages": messages, "stream": True}
        headers = {"Accept": "text/event-stream", **(extra_headers or {})}

        try:
            client = await self._get_client()
            # Streaming LLM generation needs a significantly longer timeout (5 min)
            async with client.stream(
                "POST", url, json=payload, headers=headers, timeout=300.0
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue

                    raw = line[len("data:") :].strip()

                    if raw == "[DONE]":
                        break

                    if not raw:
                        continue

                    try:
                        data = json.loads(raw)
                        # Extract token from OpenAI-compatible format
                        token = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        logger.debug("Skipping malformed SSE line: %s", raw[:50])
                        continue

        except httpx.HTTPError as exc:
            logger.error("Error streaming from backend: %s", exc)
            raise StreamingError(f"Streaming failed: {exc}") from exc


# Global singleton client
_client: BackendClient | None = None


def get_backend_client() -> BackendClient:
    """Get or create async backend client.

    Returns:
        BackendClient: Shared client instance
    """
    global _client
    if _client is None:
        settings = get_settings()
        _client = BackendClient(timeout=settings.backend_timeout)
    return _client


# Public convenience functions (maintain backward compatibility)


async def get_student_profile(student_id: str) -> dict[str, Any] | None:
    """Get student profile (convenience wrapper).

    Args:
        student_id: Student identifier

    Returns:
        Student profile dict or None if not found
    """
    try:
        client = get_backend_client()
        return await client.get_student_profile(student_id)
    except StudentNotFoundError:
        return None
    except BackendConnectionError as exc:
        logger.warning("Backend unreachable: %s", exc)
        return None


async def create_student(student_id: str, name: str) -> dict[str, Any] | None:
    """Create a new student (convenience wrapper).

    Args:
        student_id: Unique student identifier
        name: Student's name

    Returns:
        Creation response or None on error
    """
    try:
        client = get_backend_client()
        return await client.create_student(student_id, name)
    except BackendConnectionError as exc:
        logger.warning("Backend unreachable: %s", exc)
        return None
    except BackendError as exc:
        logger.warning("Failed to create student: %s", exc)
        return None


async def get_auth_token(student_id: str) -> str | None:
    """Generate JWT token (convenience wrapper).

    Args:
        student_id: Student identifier

    Returns:
        JWT token or None on error
    """
    client = get_backend_client()
    return await client.get_auth_token(student_id)


async def stream_chat_completions(
    messages: list[dict[str, str]],
    model: str = "tutor",
    extra_headers: dict[str, str] | None = None,
) -> AsyncIterator[str]:
    """Stream chat completions (convenience wrapper).

    Args:
        messages: List of message dicts
        model: Model name
        extra_headers: Optional headers

    Yields:
        Content tokens
    """
    client = get_backend_client()
    async for token in client.stream_chat_completions(messages, model, extra_headers):
        yield token
