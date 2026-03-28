"""Main FastAPI application for the language learning service."""

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from italianollama.agents.tutor import LanguageTutor
from italianollama.llm.client import LLMClient
from italianollama.memory.graph import MemoryGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting ItalianOllama Language Learning Service")

    # Initialize LLM client
    provider = os.getenv("AISUITE_PROVIDER", "ollama")
    app.state.llm_client = LLMClient(provider=provider)

    # Initialize memory graph
    app.state.memory = MemoryGraph(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", ""),
    )
    await app.state.memory.connect()

    # Initialize tutor agent
    app.state.tutor = LanguageTutor(llm_client=app.state.llm_client, memory=app.state.memory)

    logger.info("All services initialized successfully")

    yield

    # Cleanup
    logger.info("Shutting down ItalianOllama Language Learning Service")
    await app.state.memory.close()


app = FastAPI(
    title="ItalianOllama API",
    description="LLM-based language learning workflow with memory",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    language: str = "italian"
    level: str = "intermediate"
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str
    session_id: str
    vocabulary: list[dict] | None = None
    grammar_notes: list[str] | None = None


class VocabRequest(BaseModel):
    """Request model for vocabulary management."""

    word: str
    translation: str
    examples: list[str]
    topic: str
    language: str = "italian"


class VocabResponse(BaseModel):
    """Response model for vocabulary endpoints."""

    success: bool
    message: str
    node_id: str | None = None


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    status = {"status": "healthy", "llm_client": "unknown", "memory": "unknown"}

    # Check LLM client
    try:
        if hasattr(app.state, "llm_client"):
            status["llm_client"] = "connected"
    except Exception:
        status["llm_client"] = "error"

    # Check memory
    try:
        if hasattr(app.state, "memory"):
            await app.state.memory.verify_connectivity()
            status["memory"] = "connected"
    except Exception:
        status["memory"] = "error"

    if status["llm_client"] == "error" or status["memory"] == "error":
        status["status"] = "degraded"

    return status


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the language tutor."""
    try:
        response = await app.state.tutor.chat(
            message=request.message,
            language=request.language,
            level=request.level,
            session_id=request.session_id,
        )
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Vocabulary endpoints
@app.post("/vocabulary", response_model=VocabResponse)
async def add_vocabulary(request: VocabRequest):
    """Add new vocabulary to the knowledge graph."""
    try:
        node_id = await app.state.memory.add_vocabulary(
            word=request.word,
            translation=request.translation,
            examples=request.examples,
            topic=request.topic,
            language=request.language,
        )
        return VocabResponse(
            success=True, message=f"Added '{request.word}' to vocabulary", node_id=node_id
        )
    except Exception as e:
        logger.error(f"Vocabulary add error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vocabulary/{language}")
async def get_vocabulary(language: str = "italian", topic: str | None = None):
    """Get vocabulary for a language, optionally filtered by topic."""
    try:
        vocab = await app.state.memory.get_vocabulary(language, topic)
        return {"vocabulary": vocab}
    except Exception as e:
        logger.error(f"Vocabulary get error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vocabulary/{language}/stats")
async def get_vocabulary_stats(language: str = "italian"):
    """Get vocabulary statistics."""
    try:
        stats = await app.state.memory.get_vocabulary_stats(language)
        return stats
    except Exception as e:
        logger.error(f"Vocabulary stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Session endpoints
@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session history."""
    try:
        session = await app.state.memory.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session get error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/topics")
async def get_topics():
    """Get all available topics."""
    try:
        topics = await app.state.memory.get_topics()
        return {"topics": topics}
    except Exception as e:
        logger.error(f"Topics get error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# LLM endpoints
@app.post("/llm/generate")
async def generate(prompt: str, model: str | None = None):
    """Direct LLM generation."""
    try:
        result = await app.state.llm_client.generate(prompt, model=model)
        return {"response": result}
    except Exception as e:
        logger.error(f"Generate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
