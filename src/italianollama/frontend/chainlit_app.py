"""Sofia – Chainlit-based Italian Tutor chat interface.

Entry-point for the Chainlit frontend.  On session start the app:

1. Retrieves (or falls back gracefully for) the student profile from the
   FastAPI backend.
2. Stores the profile in the Chainlit user session.
3. Greets the student with a CEFR-level–appropriate welcome message.

Subsequent user messages are forwarded to the backend's
``POST /v1/chat/completions`` endpoint via SSE streaming and the tokens are
streamed back into the Chainlit UI in real time.

## Middleware Integration

This frontend properly integrates with the API middleware:
- JWT token management via /auth/token and /auth/refresh endpoints
- Session tracking via cookies (X-Session-ID header)
- Rate limit handling (429 responses with automatic retry)
- Timeout handling (408 responses)
- Request ID tracking for debugging (X-Request-ID header)

Run locally (without Docker)::

    poetry install
    chainlit run src/italianollama/frontend/chainlit_app.py --port 8501

Environment variables (all optional, defaults shown):

- ``BACKEND_URL`` – ``http://localhost:8000``
- ``BACKEND_TIMEOUT`` – ``240``
- ``DEFAULT_STUDENT_ID`` – ``demo``
- ``CHAT_PLACEHOLDER`` – ``Scrivi il tuo messaggio qui...`` (Italian)
- ``LOG_LEVEL`` – ``INFO``

## Architecture

Uses modular components from italianollama.frontend.ui:

- **CEFRGreeter**: CEFR level-aware greetings
- **SessionManager**: Student profile and chat history management
- **MessageHandler**: Backend communication, streaming, and error handling
"""

from datetime import datetime, timedelta, timezone
import logging

import chainlit as cl
import httpx

from italianollama.frontend.config import get_settings
from italianollama.frontend.ui import (
    CEFRGreeter,
    MessageHandler,
    SessionManager,
)

# ---------------------------------------------------------------------------
# Module setup
# ---------------------------------------------------------------------------

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

logger.info("Sofia initialized | version=%s", "1.0.0")


# ---------------------------------------------------------------------------
# Chainlit lifecycle hooks
# ---------------------------------------------------------------------------


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize a new student session.

    1. Check backend availability with retries



    2. Extract student_id from query parameters
    3. Obtain JWT token via /auth/token endpoint (middleware integration)
    4. Load student profile from backend
    5. Store token in Chainlit session for API calls
    6. Send CEFR-level appropriate greeting
    """
    logger.info("Starting new chat session")

    # 1. Check backend availability with retries

    backend_available = False
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.backend_url}/health")
                if resp.status_code == 200:
                    logger.info("Backend health check: OK (attempt %d)", attempt + 1)
                    backend_available = True
                    break
                else:
                    logger.warning(
                        "Backend health check failed: status %d (attempt %d)",
                        resp.status_code,
                        attempt + 1,
                    )
        except Exception as e:
            logger.warning("Backend health check failed (attempt %d): %s", attempt + 1, e)
            if attempt < 2:
                import asyncio

                await asyncio.sleep(1)  # Wait before retry

    if not backend_available:
        logger.warning("Backend availability check failed after retries, will use fallback mode")

    # 2. Extract student_id from query parameters if embedded
    # Chainlit sometimes wraps query params in a list, e.g. {'student_id': ['Jonas']}
    query_params = cl.user_session.get("client_query_params", {})
    if not query_params and hasattr(cl.context, "session"):
        query_params = getattr(cl.context.session, "client_query_params", {})

    logger.debug("Raw query params: %s", query_params)

    student_id = query_params.get("student_id")
    if isinstance(student_id, list) and len(student_id) > 0:
        student_id = student_id[0]

    if student_id:
        logger.info("Found student_id in query params: %s", student_id)
    else:
        logger.debug("No student_id in query params, will use default")

    # Store JWT token and session info for middleware integration
    session_token = None
    token_expires_at = None
    session_cookies = {}

    # 3. Check for token passed from Streamlit (shared session)
    # First check query params for token passed from Streamlit
    query_params = cl.user_session.get("client_query_params", {})
    passed_token = query_params.get("token")
    if isinstance(passed_token, list):
        passed_token = passed_token[0]

    if passed_token:
        # Use token passed from Streamlit (shared session)
        try:
            from italianollama.api.middleware.auth import verify_access_token

            payload = verify_access_token(passed_token)
            token_student = payload.get("sub")
            if token_student == student_id:
                session_token = passed_token
                exp = payload.get("exp")
                if exp:
                    token_expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
                logger.info(
                    "Using shared JWT token from Streamlit | student=%s | expires=%s",
                    student_id,
                    token_expires_at.isoformat() if token_expires_at else "unknown",
                )
            else:
                logger.warning("Token student_id doesn't match URL student_id")
        except Exception as e:
            logger.warning("Failed to verify passed token: %s", e)

    # 4. If no valid token from Streamlit, obtain new token (fallback)
    if not session_token and backend_available and student_id:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Request token from backend
                token_resp = await client.post(
                    f"{settings.backend_url}/auth/token",
                    json={"student_id": student_id},
                )

                if token_resp.status_code == 200:
                    token_data = token_resp.json()
                    session_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 14400)  # Default 4 hours
                    token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

                    # Extract session cookies for session tracking
                    for cookie in token_resp.cookies:
                        session_cookies[cookie.name] = cookie.value

                    logger.info(
                        "JWT token obtained for %s | expires_at=%s",
                        student_id,
                        token_expires_at.isoformat(),
                    )
                else:
                    logger.warning(
                        "Failed to get token: status=%d",
                        token_resp.status_code,
                    )
        except Exception as e:
            logger.warning("Failed to obtain JWT token: %s", e)

    # Store token and session info in Chainlit user session for middleware integration
    cl.user_session.set("jwt_token", session_token)
    cl.user_session.set("token_expires_at", token_expires_at)
    cl.user_session.set("session_cookies", session_cookies)
    cl.user_session.set("student_id", student_id)

    # Track request IDs for debugging
    cl.user_session.set("request_ids", [])

    try:
        # 4. Initialize session with fallback enabled if backend unavailable
        profile = await SessionManager.initialize_session(
            student_id=student_id,
            use_demo_fallback=not backend_available,
        )

        logger.info(
            "Session initialized | student=%s | level=%s | demo=%s | token=%s",
            profile.get("student_id"),
            profile.get("cefr_level"),
            profile.get("is_demo", False),
            "yes" if session_token else "no",
        )

        # 5. Generate and send greeting
        level = SessionManager.get_student_level()
        greeting = CEFRGreeter.get_greeting(level)

        # Add demo mode notice if applicable
        if profile.get("is_demo"):
            greeting += "\n\n_⚠️ Modalità demo: alcuni dati potrebbero non essere salvati._"

        # Add token info for debugging
        if session_token:
            greeting += (
                f"\n\n_Sessione autenticata (token expira: {token_expires_at.strftime('%H:%M')})_"
            )

        await cl.Message(content=greeting).send()
        logger.debug("Greeting sent | level=%s", level)

    except Exception as e:
        logger.error("Failed to initialize session: %s", e, exc_info=True)
        error_msg = (
            "🔌 Mi dispiace, non riesco a connettermi al server. "
            "Per favore, riprova tra qualche istante."
        )
        await cl.Message(content=error_msg).send()


# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------


async def _get_auth_headers() -> dict:
    """Get authorization headers for API calls, with token refresh if needed.

    Returns headers with JWT token for middleware authentication.
    Handles token refresh via /auth/refresh endpoint when needed.
    Uses token from query params if available (shared with Streamlit).
    """
    headers = {"Content-Type": "application/json"}

    # First, try to get token from query params (passed from Streamlit)
    query_params = cl.user_session.get("client_query_params", {})
    token = query_params.get("token")
    if isinstance(token, list):
        token = token[0]

    # Fall back to stored token if not in query params
    if not token:
        token = cl.user_session.get("jwt_token")

    token_expires_at = cl.user_session.get("token_expires_at")
    student_id = cl.user_session.get("student_id")

    if not token or not student_id:
        logger.debug("No JWT token available")
        return headers

    # Check if token is expired or about to expire (within 5 minutes)
    if token_expires_at and token_expires_at < datetime.now(timezone.utc) + timedelta(minutes=5):
        logger.info("Token expiring soon, attempting refresh")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                refresh_resp = await client.post(
                    f"{settings.backend_url}/auth/refresh",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Student-ID": student_id,
                    },
                )
                if refresh_resp.status_code == 200:
                    token_data = refresh_resp.json()
                    new_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 14400)
                    new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

                    # Update stored token
                    cl.user_session.set("jwt_token", new_token)
                    cl.user_session.set("token_expires_at", new_expires_at)

                    logger.info("Token refreshed successfully")
                    token = new_token
                else:
                    logger.warning("Token refresh failed: status=%d", refresh_resp.status_code)
        except Exception as e:
            logger.warning("Token refresh error: %s", e)

    # Add authorization header
    headers["Authorization"] = f"Bearer {token}"

    return headers


async def _handle_api_response(response: httpx.Response, student_id: str) -> None:
    """Handle special API responses (rate limits, timeouts, auth errors).

    Args:
        response: The HTTP response from the API
        student_id: Current student ID for logging

    Raises:
        Exception: With user-friendly message for different error types
    """
    # Track request ID for debugging
    request_id = response.headers.get("X-Request-ID")
    if request_id:
        request_ids = cl.user_session.get("request_ids", [])
        request_ids.append(request_id)
        # Keep last 10 request IDs
        cl.user_session.set("request_ids", request_ids[-10:])
        logger.debug("Request ID: %s", request_id)

    # Handle rate limit (429)
    if response.status_code == 429:
        retry_after = int(response.headers.get("X-RateLimit-Window", "60"))
        limit = response.headers.get("X-RateLimit-Limit", "unknown")
        raise Exception(
            f"⚠️ Troppe richieste! Per favore, aspetta {retry_after} secondi prima di inviare un altro messaggio. "
            f"(Limite: {limit} richieste/minuto)"
        )

    # Handle auth errors (401)
    if response.status_code == 401:
        # Try to refresh token
        token = cl.user_session.get("jwt_token")
        if token:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    refresh_resp = await client.post(
                        f"{settings.backend_url}/auth/refresh",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "X-Student-ID": student_id,
                        },
                    )
                    if refresh_resp.status_code == 200:
                        token_data = refresh_resp.json()
                        cl.user_session.set("jwt_token", token_data.get("access_token"))
                        logger.info("Token refreshed after 401")
                        return  # Let the caller retry
            except Exception:
                pass

        # Clear invalid token
        cl.user_session.set("jwt_token", None)
        raise Exception(
            "🔐 La sessione è scaduta. Per favore, ricarica la pagina per accedere di nuovo."
        )

    # Handle timeout (408)
    if response.status_code == 408:
        timeout = response.headers.get("X-Request-Timeout", "30")
        raise Exception(
            f"⏱️ La richiesta ha superato il timeout di {timeout} secondi. "
            "Il server sta impiegando più del solito. Per favore, riprova."
        )

    # Handle other errors
    if response.status_code >= 400:
        try:
            error_data = response.json()
            error_msg = error_data.get("detail", "Errore sconosciuto")
        except:
            error_msg = f"Errore {response.status_code}"

        raise Exception(f"❌ Errore del server: {error_msg}")


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Forward user message to backend and stream response.

    This handler properly integrates with API middleware:
    1. Uses JWT token from session for authentication
    2. Handles 429 rate limit with user-friendly messages
    3. Handles 401 auth errors with token refresh
    4. Handles 408 timeout errors gracefully
    5. Tracks request IDs for debugging

    Args:
        message: Incoming Chainlit message from the student
    """
    user_content = message.content
    student_id = cl.user_session.get("student_id") or SessionManager.get_student_id()

    logger.debug(
        "Received message | student=%s | len=%d",
        student_id,
        len(user_content),
    )

    # Get current history (excluding this message)
    history = SessionManager.get_chat_history()

    # Append user message to session history
    SessionManager.append_to_chat_history("user", user_content)

    # Add to history for API call
    api_history = history + [{"role": "user", "content": user_content}]

    # Stream response to UI
    response_msg = cl.Message(content="")
    await response_msg.send()

    collected_tokens = []
    full_response = ""

    # Retry logic for middleware-related errors
    max_retries = 2
    retry_count = 0

    while retry_count <= max_retries:
        try:
            # Get auth headers with token refresh if needed
            headers = await _get_auth_headers()

            # Make request with proper headers
            async with httpx.AsyncClient(timeout=settings.backend_timeout) as client:
                # Send request to chat completions endpoint
                request_data = {
                    "model": "tutor",
                    "messages": api_history,
                    "stream": True,
                }

                async with client.stream(
                    "POST",
                    f"{settings.backend_url}/v1/chat/completions",
                    json=request_data,
                    headers=headers,
                ) as response:
                    # Handle middleware errors
                    await _handle_api_response(response, student_id)

                    # Stream tokens from response
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                break

                            try:
                                import json

                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        token = delta["content"]
                                        collected_tokens.append(token)
                                        await response_msg.stream_token(token)
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue

            # Success - exit retry loop
            break

        except Exception as e:
            error_str = str(e)

            # Check if it's a retryable error (rate limit, auth)
            if "Troppe richieste" in error_str or "sessione è scaduta" in error_str:
                if retry_count < max_retries:
                    retry_count += 1
                    logger.warning("Retrying after error: %s (attempt %d)", error_str, retry_count)

                    # Wait before retry
                    import asyncio

                    await asyncio.sleep(2)
                    continue

            # Non-retryable error or max retries reached
            logger.error(
                "Error streaming message for %s: %s",
                student_id,
                e,
                exc_info=True,
            )
            error_response = MessageHandler.handle_error(e)
            await response_msg.stream_token(f"\n\n{error_response}")
            break

    try:
        # Append full response to session history
        full_response = "".join(collected_tokens)
        SessionManager.append_to_chat_history("assistant", full_response)

        logger.debug(
            "Message completed | student=%s | response_len=%d",
            student_id,
            len(full_response),
        )

        # Persist to Neo4j (non-blocking, best effort)
        try:
            await _persist_chat_message_to_neo4j(student_id, user_content, full_response)
        except Exception as e:
            logger.warning("Failed to persist chat to Neo4j for %s: %s", student_id, e)

    except Exception as e:
        logger.error(
            "Error streaming message for %s: %s",
            student_id,
            e,
            exc_info=True,
        )
        error_response = MessageHandler.handle_error(e)
        await response_msg.stream_token(f"\n\n{error_response}")

    finally:
        await response_msg.update()

        # Log request IDs for debugging
        request_ids = cl.user_session.get("request_ids", [])
        if request_ids:
            logger.debug("Request IDs for this session: %s", request_ids)


async def _persist_chat_message_to_neo4j(
    student_id: str,
    user_message: str,
    assistant_response: str,
) -> None:
    """Persist chat message exchange to Neo4j.

    Args:
        student_id: Student identifier
        user_message: User's input message
        assistant_response: AI tutor's response
    """
    try:
        # Lazy import to avoid circular dependencies
        from italianollama.memory.neo4j_client import Neo4jClient

        client = Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )

        # Create Cypher query to store chat exchange
        query = """
        MATCH (s:Student {student_id: $student_id})
        CREATE (msg:ChatMessage {
            timestamp: datetime(),
            user_content: $user_content,
            assistant_content: $assistant_content,
            content_length: $content_length
        })
        CREATE (s)-[:HAS_CHAT_MESSAGE]->(msg)
        RETURN msg
        """

        params = {
            "student_id": student_id,
            "user_content": user_message,
            "assistant_content": assistant_response,
            "content_length": len(user_message) + len(assistant_response),
        }

        # Execute with async driver
        async with client._driver.session() as session:
            result = await session.run(query, params)
            await result.consume()

        logger.debug(
            "Chat message persisted to Neo4j | student=%s | msg_len=%d",
            student_id,
            len(user_message) + len(assistant_response),
        )

    except Exception as e:
        logger.warning("Neo4j persistence failed for %s: %s", student_id, e)


# ---------------------------------------------------------------------------
# Optional: Chat configuration
# ---------------------------------------------------------------------------


@cl.on_settings_update
async def setup_agent(settings_dict):
    """Handle settings updates from Chainlit UI."""
    logger.info("Settings updated: %s", settings_dict)


# Chainlit UI customization (optional)
# Note: Slider component may not be available in all Chainlit versions
# Disabled for compatibility with Chainlit 2.6.3
chat_settings = []
