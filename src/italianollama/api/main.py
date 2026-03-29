"""FastAPI application - Italian Tutor Backend.

This module provides the REST API for the Italian Tutor application.
It exposes endpoints for chat, student management, and health checks.
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from italianollama.graph.graph import create_tutor_graph
from italianollama.memory.neo4j_client import Neo4jClient

app = FastAPI(
    title="Italian Tutor API",
    description="AI-powered Italian language tutor with LangGraph",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global graph instance
_tutor_graph = None
_neo4j_client = None


def get_neo4j_client() -> Neo4jClient:
    """Get or create Neo4j client."""
    global _neo4j_client
    if _neo4j_client is None:
        _neo4j_client = Neo4jClient(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", ""),
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
        )
    return _neo4j_client


def get_tutor_graph():
    """Get or create tutor graph."""
    global _tutor_graph
    if _tutor_graph is None:
        _tutor_graph = create_tutor_graph(get_neo4j_client())
    return _tutor_graph


# ============ Data Models ============


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


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    neo4j: str
    litellm: str


# ============ Routes ============


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "Italian Tutor API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    # Check Neo4j
    neo4j_status = "disconnected"
    try:
        client = get_neo4j_client()
        if await client.verify_connectivity():
            neo4j_status = "connected"
    except Exception:
        pass

    # Check LiteLLM (simplified)
    litellm_status = "unknown"
    litellm_url = os.getenv("LITELLM_BASE_URL", "http://litellm:4000")
    try:
        import httpx

        response = httpx.get(f"{litellm_url}/health", timeout=5)
        if response.status_code == 200:
            litellm_status = "connected"
    except Exception:
        litellm_status = f"unreachable ({litellm_url})"

    return HealthResponse(
        status="ok" if neo4j_status == "connected" else "degraded",
        neo4j=neo4j_status,
        litellm=litellm_status,
    )


@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """OpenAI-compatible chat endpoint.

    This allows Open WebUI to connect directly.
    """
    # Extract messages from request
    messages = request.get("messages", [])

    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    # Get student info from messages or use defaults
    student_id = "default"
    for msg in messages:
        if msg.get("role") == "system":
            # Check for student_id in system prompt
            if "student_id" in msg.get("content", ""):
                import re

                match = re.search(r"student_id[:\s]+([\w-]+)", msg.get("content", ""))
                if match:
                    student_id = match.group(1)

    # Get last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    # Run tutor graph
    graph = get_tutor_graph()

    try:
        # Run the graph
        result = await graph.ainvoke(
            {
                "student_id": student_id,
                "messages": [({"role": "user", "content": user_message})],
                "current_level": None,
                "exercise_type": None,
                "exercise_state": {},
            }
        )

        # Get last assistant message
        response_text = "Ciao! Sono il tuo tutore di italiano. Come posso aiutarti oggi?"
        for msg in reversed(result.get("messages", [])):
            if msg.get("role") == "assistant":
                response_text = msg.get("content", response_text)
                break

        # OpenAI-compatible response
        return {
            "id": f"chatcmpl-{os.urandom(12).hex()}",
            "object": "chat.completion",
            "created": int(os.time()),
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Simple chat endpoint for custom frontends."""
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

        # Get assistant response
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/students")
async def create_student(student: StudentCreate):
    """Create a new student."""
    client = get_neo4j_client()

    try:
        await client.create_student(student.student_id, student.name)
        return {"status": "created", "student_id": student.student_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/students/{student_id}")
async def get_student(student_id: str):
    """Get student info and progress."""
    client = get_neo4j_client()

    try:
        student = await client.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup():
    """Initialize connections on startup."""
    print("Starting Italian Tutor API...")

    # Test Neo4j connection
    try:
        client = get_neo4j_client()
        await client.verify_connectivity()
        print("✓ Neo4j connected")
    except Exception as e:
        print(f"⚠ Neo4j not available: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    global _neo4j_client
    if _neo4j_client:
        await _neo4j_client.close()
    print("Italian Tutor API stopped")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
