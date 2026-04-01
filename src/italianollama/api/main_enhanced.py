"""FastAPI application - Italian Tutor Backend (Enhanced).

This module provides the REST API for the Italian Tutor application with semantic endpoints.
It exposes endpoints for chat, student management, learning analytics, and personalized learning.

Key improvements over main.py:
- Uses enhanced Neo4j client with semantic operations
- Session/attempt tracking endpoints
- Vocabulary and spaced repetition endpoints
- Skill tracking and analytics
- Learning velocity and recommendations
- Performance metrics per attempt
"""

from datetime import timedelta
import logging

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from italianollama.api.config import get_settings
from italianollama.api.exceptions import NotFoundError, ValidationError
from italianollama.api.middleware.auth import create_access_token, verify_access_token
from italianollama.api.middleware.context import ContextMiddleware
from italianollama.api.middleware.errors import setup_error_handlers
from italianollama.api.middleware.logging import LoggingMiddleware
from italianollama.api.middleware.metrics import setup_metrics
from italianollama.api.middleware.rate_limit import RateLimitConfig, setup_rate_limiting
from italianollama.api.middleware.timeout import TimeoutConfig, setup_request_timeout
from italianollama.graph.graph import create_tutor_graph
from italianollama.memory.neo4j_client_enhanced import Neo4jClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings (will validate all required env vars at startup)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Italian Tutor API (Enhanced)",
    description="AI-powered Italian language tutor with semantic learning graph",
    version="0.3.0",
)

# ============ Middleware Stack ============

# Request logging + context injection (must be first)
app.add_middleware(ContextMiddleware)
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


async def get_neo4j_client() -> Neo4jClient:
    """Get or create Neo4j client using validated settings."""
    global _neo4j_client
    if _neo4j_client is None:
        logger.info(f"Initializing Neo4j client (enhanced): {settings.neo4j_uri}")
        _neo4j_client = Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )
        await _neo4j_client.connect()
    return _neo4j_client


async def get_tutor_graph():
    """Get or create tutor graph."""
    global _tutor_graph
    if _tutor_graph is None:
        logger.info("Building LangGraph tutor workflow")
        client = await get_neo4j_client()
        _tutor_graph = create_tutor_graph(client)
    return _tutor_graph


# ============ Pydantic Models - Core Chat ============


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


# ============ Pydantic Models - Student Management ============


class StudentCreate(BaseModel):
    """Create a new student."""

    student_id: str
    name: str
    native_language: str = "English"


class StudentProfile(BaseModel):
    """Student profile response."""

    student_id: str
    name: str
    native_language: str
    total_xp: int
    current_streak: int
    level: str | None = None
    vocabulary_count: int = 0
    session_count: int = 0
    last_active: str | None = None


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


# ============ Pydantic Models - Session & Attempts ============


class SessionCreate(BaseModel):
    """Create a new learning session."""

    student_id: str
    topic: str | None = None
    exercise_type: str | None = None


class SessionResponse(BaseModel):
    """Learning session response."""

    session_id: str
    student_id: str
    topic: str | None = None
    exercise_type: str | None = None
    started_at: str
    duration_minutes: int | None = None
    status: str


class ExerciseAttempt(BaseModel):
    """Record an exercise attempt."""

    session_id: str
    student_id: str
    exercise_template_id: str
    exercise_type: str
    correct: bool
    confidence: int = Field(..., ge=1, le=5)  # 1-5 scale
    duration_seconds: int
    hints_used: int = 0
    retries: int = 0
    performance_metrics: dict | None = None


class AttemptResponse(BaseModel):
    """Exercise attempt response."""

    attempt_id: str
    session_id: str
    student_id: str
    correct: bool
    xp_earned: int
    streak_updated: bool


# ============ Pydantic Models - Vocabulary ============


class VocabularyEntry(BaseModel):
    """Add vocabulary to student."""

    student_id: str
    italian_word: str
    english_translation: str
    part_of_speech: str
    cefr_level: str
    topic: str | None = None


class VocabularyResponse(BaseModel):
    """Vocabulary response."""

    vocabulary_id: str
    italian_word: str
    english_translation: str
    cefr_level: str
    next_review: str | None = None
    confidence_level: float = 0.0


# ============ Pydantic Models - Analytics ============


class SkillBreakdown(BaseModel):
    """Skill experience breakdown."""

    skill_name: str
    total_xp: int
    level: str
    progress_to_next: float  # 0.0-1.0


class LearningVelocity(BaseModel):
    """Learning velocity metrics."""

    xp_per_day: float
    sessions_per_week: float
    average_session_duration: float
    streak_days: int
    total_xp: int


class RecommendedModule(BaseModel):
    """Recommended next learning module."""

    module_id: str
    module_name: str
    topic: str
    difficulty: str
    reason: str  # Why recommended


# ============ Core Routes ============


@app.get("/")
async def root(request: Request):
    """Root endpoint with API information."""
    logger.info("Root endpoint accessed")
    return {
        "name": "Italian Tutor API (Enhanced)",
        "version": "0.3.0",
        "docs": "/docs",
        "semantic_graph": True,
        "request_id": getattr(request.state, "request_id", "unknown"),
        "student_id": getattr(request.state, "student_id", None),
    }


@app.get("/health", response_model=HealthResponse)
async def health(request: Request):
    """Full health check endpoint.

    Checks connectivity of Neo4j (enhanced) and LiteLLM services.
    """
    # Check Neo4j
    neo4j_status = "disconnected"
    try:
        client = await get_neo4j_client()
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
    """Generate JWT access token for student."""
    logger.info(f"Token request for student: {request.student_id}")

    if not request.student_id or not request.student_id.strip():
        raise ValidationError("student_id is required and cannot be empty")

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
    """Verify JWT token validity."""
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


# ============ Student Management Routes ============


@app.post("/students", response_model=StudentProfile)
async def create_student(student: StudentCreate, req: Request):
    """Create a new student."""
    logger.info(f"Creating student: {student.student_id}")

    if not student.student_id or not student.student_id.strip():
        raise ValidationError("student_id is required")

    if not student.name or not student.name.strip():
        raise ValidationError("name is required")

    client = await get_neo4j_client()

    try:
        await client.create_student(
            student.student_id,
            student.name,
            student.native_language,
        )
        logger.info(f"Student created: {student.student_id}")

        # Return full profile
        profile = await client.get_student(student.student_id)
        return StudentProfile(
            student_id=profile["student_id"],
            name=profile["name"],
            native_language=profile.get("native_language", "English"),
            total_xp=profile.get("total_xp", 0),
            current_streak=profile.get("current_streak", 0),
            level=None,
            vocabulary_count=0,
            session_count=0,
        )
    except Exception as e:
        logger.error(f"Error creating student: {e}", exc_info=True)
        raise


@app.get("/students/{student_id}", response_model=StudentProfile)
async def get_student(student_id: str, req: Request):
    """Get student profile and progress."""
    logger.info(f"Fetching student info: {student_id}")

    client = await get_neo4j_client()

    try:
        student = await client.get_student(student_id)
        if not student:
            raise NotFoundError("Student", f"Student {student_id} not found")

        stats = await client.get_student_stats(student_id)

        return StudentProfile(
            student_id=student["student_id"],
            name=student["name"],
            native_language=student.get("native_language", "English"),
            total_xp=student.get("total_xp", 0),
            current_streak=student.get("current_streak", 0),
            level=stats.get("highest_cefr_level"),
            vocabulary_count=stats.get("vocabulary_count", 0),
            session_count=stats.get("session_count", 0),
            last_active=student.get("last_active"),
        )
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching student: {e}", exc_info=True)
        raise


@app.get("/students/{student_id}/stats")
async def get_student_stats(student_id: str, req: Request):
    """Get detailed student statistics."""
    logger.info(f"Fetching student stats: {student_id}")
    client = await get_neo4j_client()

    try:
        student = await client.get_student(student_id)
        if not student:
            raise NotFoundError("Student", f"Student {student_id} not found")

        stats = await client.get_student_stats(student_id)
        velocity = await client.get_learning_velocity(student_id, days=7)
        skills = await client.get_skill_breakdown(student_id)

        return {
            "student_id": student_id,
            "stats": stats,
            "velocity": velocity,
            "skills": skills,
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        raise


# ============ Session Management Routes ============


@app.post("/sessions", response_model=SessionResponse)
async def create_session(session: SessionCreate, req: Request):
    """Create a new learning session."""
    logger.info(f"Creating session for student: {session.student_id}")

    client = await get_neo4j_client()

    try:
        session_id = await client.create_session(
            session.student_id,
            topic=session.topic,
            exercise_type=session.exercise_type,
        )

        return SessionResponse(
            session_id=session_id,
            student_id=session.student_id,
            topic=session.topic,
            exercise_type=session.exercise_type,
            started_at=str(
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
            ),
            status="active",
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise


@app.post("/sessions/{session_id}/end")
async def end_session(session_id: str, req: Request):
    """End a learning session."""
    logger.info(f"Ending session: {session_id}")

    client = await get_neo4j_client()

    try:
        await client.end_session(session_id)
        logger.info(f"Session ended: {session_id}")

        return {
            "status": "ended",
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Error ending session: {e}", exc_info=True)
        raise


# ============ Exercise Attempt Routes ============


@app.post("/attempts", response_model=AttemptResponse)
async def record_attempt(attempt: ExerciseAttempt, req: Request):
    """Record an exercise attempt with performance metrics."""
    logger.info(
        f"Recording attempt: session={attempt.session_id}, "
        f"exercise={attempt.exercise_template_id}, correct={attempt.correct}"
    )

    client = await get_neo4j_client()

    try:
        attempt_id = await client.record_exercise_attempt(
            session_id=attempt.session_id,
            student_id=attempt.student_id,
            exercise_template_id=attempt.exercise_template_id,
            exercise_type=attempt.exercise_type,
            correct=attempt.correct,
            confidence=attempt.confidence,
            duration_seconds=attempt.duration_seconds,
            hints_used=attempt.hints_used,
            retries=attempt.retries,
            performance_metrics=attempt.performance_metrics or {},
        )

        # Calculate XP earned (simplified)
        xp_earned = 50 if attempt.correct else 10
        if attempt.confidence >= 4:
            xp_earned += 20
        if attempt.hints_used == 0:
            xp_earned += 15

        return AttemptResponse(
            attempt_id=attempt_id,
            session_id=attempt.session_id,
            student_id=attempt.student_id,
            correct=attempt.correct,
            xp_earned=xp_earned,
            streak_updated=attempt.correct,
        )
    except Exception as e:
        logger.error(f"Error recording attempt: {e}", exc_info=True)
        raise


# ============ Vocabulary Routes ============


@app.post("/vocabulary", response_model=VocabularyResponse)
async def add_vocabulary(vocab: VocabularyEntry, req: Request):
    """Add a vocabulary entry to student's learning list."""
    logger.info(f"Adding vocabulary: {vocab.italian_word}")

    client = await get_neo4j_client()

    try:
        vocab_id = await client.add_vocabulary(
            student_id=vocab.student_id,
            italian_word=vocab.italian_word,
            english_translation=vocab.english_translation,
            part_of_speech=vocab.part_of_speech,
            cefr_level=vocab.cefr_level,
            topic=vocab.topic,
        )

        return VocabularyResponse(
            vocabulary_id=vocab_id,
            italian_word=vocab.italian_word,
            english_translation=vocab.english_translation,
            cefr_level=vocab.cefr_level,
            confidence_level=0.0,
        )
    except Exception as e:
        logger.error(f"Error adding vocabulary: {e}", exc_info=True)
        raise


@app.get("/vocabulary/{student_id}")
async def get_vocabulary(student_id: str, due_for_review: bool = False, req: Request = None):
    """Get student's vocabulary list (with optional spaced repetition filter)."""
    logger.info(f"Fetching vocabulary for student: {student_id}")

    client = await get_neo4j_client()

    try:
        vocab = await client.get_student_vocabulary(
            student_id,
            only_due_for_review=due_for_review,
        )
        logger.debug(f"Found {len(vocab)} vocabulary entries")
        return {"vocabulary": vocab}
    except Exception as e:
        logger.error(f"Error fetching vocabulary: {e}", exc_info=True)
        raise


@app.post("/vocabulary/{vocabulary_id}/confidence")
async def update_vocabulary_confidence(
    vocabulary_id: str,
    confidence: int = Field(..., ge=1, le=5),
    req: Request = None,
):
    """Update vocabulary confidence (spaced repetition tracking)."""
    logger.info(f"Updating vocabulary confidence: {vocabulary_id}")

    client = await get_neo4j_client()

    try:
        await client.update_vocabulary_confidence(
            vocabulary_id,
            confidence,
        )
        return {
            "status": "updated",
            "vocabulary_id": vocabulary_id,
            "confidence": confidence,
        }
    except Exception as e:
        logger.error(f"Error updating confidence: {e}", exc_info=True)
        raise


# ============ Analytics Routes ============


@app.get("/analytics/velocity/{student_id}")
async def get_velocity(student_id: str, days: int = 7, req: Request = None):
    """Get learning velocity metrics."""
    logger.info(f"Fetching learning velocity for student: {student_id}")

    client = await get_neo4j_client()

    try:
        velocity = await client.get_learning_velocity(student_id, days=days)
        return velocity
    except Exception as e:
        logger.error(f"Error fetching velocity: {e}", exc_info=True)
        raise


@app.get("/analytics/skills/{student_id}")
async def get_skills(student_id: str, req: Request = None):
    """Get skill breakdown."""
    logger.info(f"Fetching skill breakdown for student: {student_id}")

    client = await get_neo4j_client()

    try:
        skills = await client.get_skill_breakdown(student_id)
        return {"skills": skills}
    except Exception as e:
        logger.error(f"Error fetching skills: {e}", exc_info=True)
        raise


@app.get("/analytics/errors/{student_id}")
async def get_common_errors(student_id: str, limit: int = 10, req: Request = None):
    """Get common grammar/concept errors."""
    logger.info(f"Fetching common errors for student: {student_id}")

    client = await get_neo4j_client()

    try:
        errors = await client.get_common_errors(student_id, limit=limit)
        return {"errors": errors}
    except Exception as e:
        logger.error(f"Error fetching errors: {e}", exc_info=True)
        raise


# ============ Recommendations Routes ============


@app.get("/recommendations/next-module/{student_id}")
async def get_next_module(student_id: str, req: Request = None):
    """Get recommended next learning module."""
    logger.info(f"Getting recommendations for student: {student_id}")

    client = await get_neo4j_client()

    try:
        module = await client.get_recommended_next_module(student_id)

        if not module:
            return {
                "recommendation": None,
                "reason": "No recommendation available yet",
            }

        return {
            "recommendation": module,
            "reason": "Based on learning velocity and skill gaps",
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise


# ============ Chat Routes (Legacy) ============


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, req: Request):
    """Simple chat endpoint for custom frontends (legacy)."""
    logger.info(f"Chat request from student: {message.student_id}")

    if not message.message or not message.message.strip():
        raise ValidationError("message cannot be empty")

    graph = await get_tutor_graph()

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


@app.on_event("shutdown")
async def shutdown():
    """Clean up resources on shutdown."""
    if _neo4j_client:
        await _neo4j_client.close()
    logger.info("Application shutdown complete")
