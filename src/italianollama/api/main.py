"""FastAPI application - Italian Tutor Backend (Optimized).

This module provides the REST API for the Italian Tutor application.
It exposes endpoints for:
- Chat: LangGraph-based conversational interface
- Student Management: Registration and profile retrieval
- Authentication: JWT token generation and verification
- Learning Analytics: Velocity, skills, errors tracking
- Recommendations: Personalized next-module suggestions
- Health Checks: Neo4j and LiteLLM connectivity

This is an optimized merge of main.py and main_enhanced.py, combining:
- Stable core endpoints from main.py
- Enhanced analytics from main_enhanced.py
- Fixed endpoint definitions and proper request body handling
"""

import logging

from fastapi import FastAPI, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from italianollama.api.config import get_settings
from italianollama.api.exceptions import AuthenticationError, NotFoundError, ValidationError
from italianollama.api.middleware.auth import (
    create_access_token,
    verify_access_token,
    get_current_student,
)
from italianollama.api.middleware.context import ContextMiddleware
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
    description="AI-powered Italian language tutor with LangGraph and semantic analytics",
    version="0.3.0-optimized",
)

# ============ Middleware Stack ============

# Request logging (must be first)
app.add_middleware(LoggingMiddleware)

# Context injection - request_id, student_id, session_id
app.add_middleware(ContextMiddleware)

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
        "version": "0.3.0-optimized",
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

    # Check LiteLLM (with shorter timeout)
    litellm_status = "unknown"
    try:
        import httpx

        async with httpx.AsyncClient(timeout=2.0) as client:  # Reduced from 5s to 2s
            response = await client.get(f"{settings.litellm_base_url}/health")
            if response.status_code == 200:
                litellm_status = "connected"
                logger.debug("LiteLLM health check passed")
    except Exception as e:
        litellm_status = "unreachable"
        logger.debug(
            f"LiteLLM health check failed (non-critical): {e}"
        )  # Changed from warning to debug

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
async def verify_token(authorization: str | None = Header(None)):
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


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    authorization: str | None = Header(None, alias="Authorization"),
    student_id: str | None = Header(None, alias="X-Student-ID"),
):
    """Refresh an expiring or expired token.

    Frontend calls this when token is about to expire or has expired.
    Requires either a valid (or recently expired) token or student_id header.

    Args:
        authorization: Bearer token (can be expired for refresh)
        student_id: Fallback student_id if token is invalid

    Returns:
        TokenResponse with new JWT token
    """
    logger.info("Token refresh request")

    student = None

    # Try to extract student from token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            payload = verify_access_token(token)
            student = payload.get("sub")
            logger.debug(f"Refreshed token for student: {student}")
        except AuthenticationError:
            # Token invalid - check header
            if not student_id:
                raise AuthenticationError(
                    "Cannot refresh token. Provide valid token or X-Student-ID header."
                )
            student = student_id
    elif student_id:
        student = student_id
    else:
        raise ValidationError("Authorization header or X-Student-ID required")

    if not student:
        raise ValidationError("Student ID not found")

    # Generate new token

    token = create_access_token(student)
    logger.info(f"Token refreshed for student: {student}")

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expiration_hours * 3600,
    )


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
            },
            {"recursion_limit": 100},  # Prevent infinite loops
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
async def get_student_endpoint(
    student_id: str,
    req: Request,
):
    """Get student info.

    Returns student profile and basic info.
    No authentication required for public student lookup.
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


async def get_student(
    student_id: str,
    req: Request,
    current_student: str = Depends(get_current_student),
):
    """Get student info and progress.

    Returns student profile, current CEFR level, vocabulary count, etc.
    Requires valid JWT token. Students can only access their own data.
    """
    logger.info(f"Fetching student info: {student_id}")

    # Ownership check: students can only access their own data
    if current_student != student_id:
        logger.warning(f"Access denied: {current_student} tried to access {student_id}")
        raise AuthenticationError("Access denied to this student's data")

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


@app.get("/api/student/{student_id}/stats")
async def get_student_stats(
    student_id: str,
    current_student: str = Depends(get_current_student),
):
    """Get aggregated stats for dashboard KPI metrics.

    Requires valid JWT token. Students can only access their own stats.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    client = get_neo4j_client()
    return await client.get_student_stats(student_id)


@app.get("/api/student/{student_id}/vocabulary")
async def get_student_vocabulary(
    student_id: str,
    limit: int = 50,
    current_student: str = Depends(get_current_student),
):
    """Get student's vocabulary with confidence scores.

    Requires valid JWT token. Students can only access their own vocabulary.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    client = get_neo4j_client()
    return await client.get_student_vocabulary(student_id, limit=limit)


@app.get("/api/student/{student_id}/grammar-errors")
async def get_student_grammar_errors(
    student_id: str,
    limit: int = 10,
    current_student: str = Depends(get_current_student),
):
    """Get most common grammar errors for student.

    Requires valid JWT token. Students can only access their own errors.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    client = get_neo4j_client()
    return await client.get_common_errors(student_id, limit=limit)


@app.get("/api/student/{student_id}/graph")
async def get_student_graph(
    student_id: str,
    current_student: str = Depends(get_current_student),
):
    """Get nodes and relationships for st-link-analysis.

    Requires valid JWT token. Students can only access their own graph.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    client = get_neo4j_client()
    return await client.get_full_knowledge_graph(student_id)


@app.get("/api/student/{student_id}/test-readiness")
async def get_student_test_readiness(
    student_id: str,
    current_student: str = Depends(get_current_student),
):
    """Get CEFR test readiness scores.

    Requires valid JWT token. Students can only access their own readiness.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    client = get_neo4j_client()
    return await client.get_test_readiness(student_id)


# ============ Analytics Routes ============


@app.get("/analytics/velocity/{student_id}")
async def get_learning_velocity(
    student_id: str,
    days: int = 7,
    req: Request = None,
    current_student: str = Depends(get_current_student),
):
    """Get learning velocity for a student over the past N days.

    Velocity = (exercises_completed / days) in past N days
    Returns: exercises per day, trend, estimated time to next level

    Requires valid JWT token. Students can only access their own velocity.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    logger.info(f"Fetching learning velocity for {student_id} (last {days} days)")

    client = get_neo4j_client()

    try:
        # Query: count completed exercises in last N days
        query = """
        MATCH (s:Student {student_id: $student_id})-[:COMPLETED]->(e:Exercise)
        WHERE e.completed_at >= datetime() - duration({days: $days})
        WITH count(e) AS exercises_completed
        RETURN {
            student_id: $student_id,
            period_days: $days,
            exercises_completed: exercises_completed,
            velocity: ROUND(toFloat(exercises_completed) / $days, 2),
            unit: "exercises/day"
        } AS velocity
        """

        async with client._driver.session(database=client.database) as session:
            result = await session.run(query, student_id=student_id, days=days)
            record = await result.single()

            if record:
                return record["velocity"]
            else:
                # No data yet
                return {
                    "student_id": student_id,
                    "period_days": days,
                    "exercises_completed": 0,
                    "velocity": 0.0,
                    "unit": "exercises/day",
                }
    except Exception as e:
        logger.error(f"Error fetching velocity: {e}", exc_info=True)
        raise


@app.get("/analytics/skills/{student_id}")
async def get_student_skills(
    student_id: str,
    req: Request = None,
    current_student: str = Depends(get_current_student),
):
    """Get skill breakdown for a student.

    Returns: grammar, vocabulary, listening, speaking, reading, writing scores

    Requires valid JWT token. Students can only access their own skills.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    logger.info(f"Fetching skills for {student_id}")

    client = get_neo4j_client()

    try:
        # Query: get grammar errors and vocabulary to infer skill levels
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[r:HAS_PLACEMENT_LEVEL]->(l:CEFRLevel)
        OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
        OPTIONAL MATCH (s)-[:MADE_ERROR]->(err:GrammarError)
        OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise {type: 'grammar'})
        WITH s, l, r,
             count(DISTINCT v) AS vocabulary_count,
             count(DISTINCT err) AS grammar_errors,
             count(DISTINCT e) AS grammar_exercises
        RETURN {
            student_id: $student_id,
            grammar: ROUND(100 - (toFloat(grammar_errors) / CASE WHEN grammar_exercises > 0 THEN grammar_exercises ELSE 1 END * 100), 1),
            vocabulary: ROUND(toFloat(vocabulary_count) / 100 * 100, 1),
            placement_level: l.name,
            last_assessed: r.determined_at
        } AS skills
        """

        async with client._driver.session(database=client.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()

            if record:
                return record["skills"]
            else:
                return {
                    "student_id": student_id,
                    "grammar": 0.0,
                    "vocabulary": 0.0,
                    "placement_level": None,
                    "last_assessed": None,
                }
    except Exception as e:
        logger.error(f"Error fetching skills: {e}", exc_info=True)
        raise


@app.get("/analytics/errors/{student_id}")
async def get_common_errors(
    student_id: str,
    limit: int = 5,
    req: Request = None,
    current_student: str = Depends(get_current_student),
):
    """Get most common grammar errors for a student.

    Returns: top N grammar errors with frequency and rule explanations

    Requires valid JWT token. Students can only access their own errors.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    logger.info(f"Fetching common errors for {student_id} (limit: {limit})")

    client = get_neo4j_client()

    try:
        return await client.get_common_errors(student_id, limit=limit)
    except Exception as e:
        logger.error(f"Error fetching common errors: {e}", exc_info=True)
        raise


# ============ Recommendations Routes ============


@app.get("/recommendations/next-module/{student_id}")
async def get_next_module(
    student_id: str,
    req: Request = None,
    current_student: str = Depends(get_current_student),
):
    """Get personalized next module recommendation.

    Returns: recommended module, difficulty, reason for recommendation

    Requires valid JWT token. Students can only access their own recommendations.
    """
    if current_student != student_id:
        raise AuthenticationError("Access denied to this student's data")

    logger.info(f"Fetching next recommended module for student_id={student_id}")

    client = get_neo4j_client()

    try:
        # Query: get student's current level and recommend next
        query = """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[r:HAS_PLACEMENT_LEVEL]->(l:CEFRLevel)
        WITH s, l, r
        RETURN {
            student_id: $student_id,
            current_level: l.name,
            recommended_module: CASE
                WHEN l.name IN ['A1'] THEN 'Introduction to Italian'
                WHEN l.name IN ['A2'] THEN 'Elementary Conversations'
                WHEN l.name IN ['B1'] THEN 'Intermediate Grammar'
                WHEN l.name IN ['B2'] THEN 'Advanced Reading'
                WHEN l.name IN ['C1'] THEN 'Literature & Nuance'
                ELSE 'Placement Test'
            END,
            focus_area: CASE
                WHEN l.name IN ['A1', 'A2'] THEN 'Vocabulary & Basic Grammar'
                WHEN l.name IN ['B1'] THEN 'Complex Tenses & Subjunctive'
                ELSE 'Style & Idiomatic Expressions'
            END,
            time_estimate_minutes: 30,
            difficulty: l.name
        } AS recommendation
        """

        async with client._driver.session(database=client.database) as session:
            result = await session.run(query, student_id=student_id)
            record = await result.single()

            if record:
                return record["recommendation"]
            else:
                # No level determined yet - recommend placement test
                return {
                    "student_id": student_id,
                    "current_level": None,
                    "recommended_module": "Placement Test",
                    "focus_area": "Determine your initial level",
                    "time_estimate_minutes": 25,
                    "difficulty": "N/A",
                }
    except Exception as e:
        logger.error(f"Error fetching next module: {e}", exc_info=True)
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

        # P0+P1 COMPLETE: Initialize DB schema (constraints, indexes, touch tokens)
        await client.setup_schema()
        logger.info("✓ Neo4j schema initialization complete")
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
