"""FastAPI application - Italian Tutor Backend.

This module provides the REST API for the Italian Tutor application.
It exposes endpoints for chat, student management, and health checks.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from italianollama.api.config import get_settings
from italianollama.api.exceptions import NotFoundError, ValidationError
from italianollama.api.middleware.auth import create_access_token
from italianollama.api.middleware.errors import setup_error_handlers
from italianollama.api.middleware.logging import LoggingMiddleware
from italianollama.api.middleware.metrics import setup_metrics
from italianollama.api.middleware.rate_limit import RateLimitConfig, setup_rate_limiting
from italianollama.api.middleware.timeout import TimeoutConfig, setup_request_timeout
from italianollama.graph.graph import create_tutor_graph
from italianollama.memory.neo4j_client import Neo4jClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings (will validate all required env vars at startup)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Italian Tutor API",
    description="AI-powered Italian language tutor with LangGraph",
    version="0.2.0",
)

# ============ Middleware Stack ============

# Request logging (must be first)
app.add_middleware(LoggingMiddleware)

# CORS with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting (per-endpoint and per-student)
setup_rate_limiting(app, RateLimitConfig())

# Request timeout protection
setup_request_timeout(app, TimeoutConfig())

# Metrics collection (Prometheus)
setup_metrics(app)

# Error handlers (must be registered after middleware)
setup_error_handlers(app)

# Global instances
_tutor_graph = None
_neo4j_client = None


def get_neo4j_client() -> Neo4jClient:
    """Get or create Neo4j client using validated settings."""
    global _neo4j_client
    if _neo4j_client is None:
        logger.info(f"Initializing Neo4j client: {settings.neo4j_uri}")
        _neo4j_client = Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )
    return _neo4j_client


def get_tutor_graph():
    """Get or create tutor graph."""
    global _tutor_graph
    if _tutor_graph is None:
        logger.info("Building LangGraph tutor workflow")
        _tutor_graph = create_tutor_graph(get_neo4j_client())
    return _tutor_graph


# ============ Pydantic Models ============


class ChatMessage(BaseModel):
    """Chat message from user."""

    message: str
    student_id: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response to user."""

    response: str
    session_id: str
    student_level: str | None = None


class StudentCreate(BaseModel):
    """Create a new student."""

    student_id: str
    name: str


class TokenRequest(BaseModel):
    """Request for JWT token generation."""

    student_id: str
    expires_in_hours: int | None = None


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    neo4j: str
    litellm: str


# ============ Core Routes ============


@app.get("/")
async def root(request: Request):
    """Root endpoint with API information."""
    logger.info("Root endpoint accessed")
    return {
        "name": "Italian Tutor API",
        "version": "0.2.0",
        "docs": "/docs",
        "request_id": getattr(request.state, "request_id", "unknown"),
    }


@app.get("/health", response_model=HealthResponse)
async def health(request: Request):
    """Full health check endpoint.

    Checks connectivity of Neo4j and LiteLLM services.
    """
    # Check Neo4j
    neo4j_status = "disconnected"
    try:
        client = get_neo4j_client()
        if await client.verify_connectivity():
            neo4j_status = "connected"
            logger.debug("Neo4j health check passed")
    except Exception as e:
        logger.warning(f"Neo4j health check failed: {e}")

    # Check LiteLLM
    litellm_status = "unknown"
    try:
        import httpx

        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{settings.litellm_base_url}/health")
            if response.status_code == 200:
                litellm_status = "connected"
                logger.debug("LiteLLM health check passed")
    except Exception as e:
        litellm_status = "unreachable"
        logger.warning(f"LiteLLM health check failed: {e}")

    return HealthResponse(
        status="ok" if neo4j_status == "connected" else "degraded",
        neo4j=neo4j_status,
        litellm=litellm_status,
    )


# ============ Authentication Routes ============


@app.post("/auth/token", response_model=TokenResponse)
async def get_token(request: TokenRequest, req: Request):
    """Generate JWT access token for student.

    Frontend calls this after OAuth or login to get a token for protected routes.
    Token is valid for JWT_EXPIRATION_HOURS (default: 4 hours).

    Args:
        request: TokenRequest with student_id

    Returns:
        TokenResponse with JWT token
    """
    logger.info(f"Token request for student: {request.student_id}")

    if not request.student_id or not request.student_id.strip():
        raise ValidationError("student_id is required and cannot be empty")

    # Generate JWT token
    from datetime import timedelta

    expires_delta = None
    if request.expires_in_hours:
        expires_delta = timedelta(hours=request.expires_in_hours)

    token = create_access_token(request.student_id, expires_delta)

    logger.info(f"Token generated for student: {request.student_id}")

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiration_hours * 3600,
    )


@app.post("/auth/verify")
async def verify_token(authorization: str | None = None):
    """Verify JWT token validity.

    Used by frontends to check if a token is still valid.
    """
    from italianollama.api.middleware.auth import verify_access_token

    if not authorization:
        raise ValidationError("Authorization header required")

    # Extract token from "Bearer {token}"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValidationError("Invalid authorization header format")

    token = parts[1]

    try:
        payload = verify_access_token(token)
        logger.debug(f"Token verified for student: {payload.get('sub')}")

        return {
            "valid": True,
            "student_id": payload.get("sub"),
            "exp": payload.get("exp"),
        }
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise


# ============ Chat Routes ============


@app.post("/v1/chat/completions")
async def chat_completions(request: dict, req: Request):
    """OpenAI-compatible chat endpoint with streaming support.

    Accepts OpenAI-style chat request format:
    {
        "model": "tutor",
        "messages": [
            {"role": "user", "content": "Ciao!"},
            ...
        ],
        "stream": false  # Set to true for SSE streaming
    }

    Returns OpenAI-compatible response format or SSE stream.
    """
    import re
    import time

    from italianollama.api.stream_adapter import stream_graph_response

    logger.debug(
        f"Chat completions request: {len(request.get('messages', []))} messages, stream={request.get('stream', False)}"
    )

    # Validate request
    messages = request.get("messages", [])
    if not messages:
        raise ValidationError("No messages provided")

    # Extract student_id from system prompt or use default
    student_id = "default"
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content", "")
            if "student_id" in content:
                match = re.search(r"student_id[:\s]+([\w-]+)", content)
                if match:
                    student_id = match.group(1)
                    break

    # Get last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    if not user_message:
        raise ValidationError("No user message found")

    logger.info(f"Processing chat for student: {student_id}")

    # Check if streaming requested
    stream = request.get("stream", False)

    if stream:
        # Return streaming response
        logger.debug(f"Returning streaming response for request {req.state.request_id}")

        graph = get_tutor_graph()
        input_data = {
            "student_id": student_id,
            "messages": [{"role": "user", "content": user_message}],
            "current_level": None,
            "exercise_type": None,
            "exercise_state": {},
        }

        generator = stream_graph_response(
            graph,
            input_data,
            student_id,
            req.state.request_id,
        )

        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Non-streaming path
    graph = get_tutor_graph()

    try:
        result = await graph.ainvoke(
            {
                "student_id": student_id,
                "messages": [{"role": "user", "content": user_message}],
                "current_level": None,
                "exercise_type": None,
                "exercise_state": {},
            }
        )

        # Extract last assistant message
        response_text = "Ciao! Sono il tuo tutore di italiano. Come posso aiutarti oggi?"
        for msg in reversed(result.get("messages", [])):
            if msg.get("role") == "assistant":
                response_text = msg.get("content", response_text)
                break

        # Return OpenAI-compatible response
        return {
            "id": f"chatcmpl-{req.state.request_id[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.get("model", "tutor"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_message.split()) + len(response_text.split()),
            },
        }

    except Exception as e:
        logger.error(f"Chat completions error: {e}", exc_info=True)
        raise


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, req: Request):
    """Simple chat endpoint for custom frontends.

    Simpler API than /v1/chat/completions for direct integration.
    """
    logger.info(f"Chat request from student: {message.student_id}")

    if not message.message or not message.message.strip():
        raise ValidationError("message cannot be empty")

    graph = get_tutor_graph()

    try:
        result = await graph.ainvoke(
            {
                "student_id": message.student_id,
                "messages": [{"role": "user", "content": message.message}],
                "current_level": None,
                "exercise_type": None,
                "exercise_state": {},
            }
        )

        # Extract assistant response
        response_text = "Mi dispiace, non ho capito. Puoi ripetere?"
        for msg in reversed(result.get("messages", [])):
            if msg.get("role") == "assistant":
                response_text = msg.get("content", response_text)
                break

        return ChatResponse(
            response=response_text,
            session_id=message.session_id or message.student_id,
            student_level=result.get("current_level"),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise


# ============ Student Management Routes ============


@app.post("/students")
async def create_student(student: StudentCreate, req: Request):
    """Create a new student.

    Initial call to register a student in the system.
    """
    logger.info(f"Creating student: {student.student_id}")

    if not student.student_id or not student.student_id.strip():
        raise ValidationError("student_id is required")

    if not student.name or not student.name.strip():
        raise ValidationError("name is required")

    client = get_neo4j_client()

    try:
        await client.create_student(student.student_id, student.name)
        logger.info(f"Student created: {student.student_id}")

        return {
            "status": "created",
            "student_id": student.student_id,
            "name": student.name,
        }
    except Exception as e:
        logger.error(f"Error creating student: {e}", exc_info=True)
        raise


@app.get("/students/{student_id}")
async def get_student(student_id: str, req: Request):
    """Get student info and progress.

    Returns student profile, current CEFR level, vocabulary count, etc.
    """
    logger.info(f"Fetching student info: {student_id}")

    client = get_neo4j_client()

    try:
        student = await client.get_student(student_id)
        if not student:
            raise NotFoundError("Student", f"Student {student_id} not found")

        logger.debug(f"Student info: {student.get('student_id')}")
        return student
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching student: {e}", exc_info=True)
        raise


# ============ Lifecycle Events ============


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    logger.info("=" * 60)
    logger.info("🚀 Italian Tutor API Starting Up")
    logger.info("=" * 60)

    # Load and validate settings
    try:
        logger.info(f"✓ Configuration loaded (LOG_LEVEL={settings.log_level})")
    except Exception as e:
        logger.error(f"✗ Configuration error: {e}")
        raise

    # Test Neo4j connection
    try:
        client = get_neo4j_client()
        await client.verify_connectivity()
        logger.info(f"✓ Neo4j connected: {settings.neo4j_uri}")
    except Exception as e:
        logger.error(f"✗ Neo4j connection failed: {e}")
        logger.warning("Continuing without Neo4j (operations will fail)")

    # Initialize LangGraph
    try:
        graph = get_tutor_graph()
        logger.info("✓ LangGraph workflow initialized")
    except Exception as e:
        logger.error(f"✗ LangGraph initialization failed: {e}")
        raise

    logger.info("=" * 60)
    logger.info("✓ Startup complete - API ready for requests")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down Italian Tutor API...")

    global _neo4j_client
    if _neo4j_client:
        try:
            await _neo4j_client.close()
            logger.info("✓ Neo4j connection closed")
        except Exception as e:
            logger.error(f"✗ Error closing Neo4j: {e}")

    logger.info("✓ Shutdown complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
