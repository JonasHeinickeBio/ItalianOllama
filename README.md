# Italian Tutor - AI-Powered Italian Language Learning

> An intelligent Italian language tutor built with LangGraph, Neo4j, and LiteLLM

## Overview

Italian Tutor is an AI-powered language learning application that provides personalized Italian lessons through conversation. It uses a graph-based state management system (LangGraph) to orchestrate different exercise types and tracks student progress in Neo4j.

### Architecture

The Italian Tutor uses a **dual-frontend architecture** with a shared FastAPI backend:

```
┌──────────────────────────────────────────────────────────────────┐
│                          Browser                                 │
├──────────────────────────────────────────────────────────────────┤
│   /chat/       Route A       /dashboard/       Route B          │
│      │                              │                            │
│      ▼                              ▼                            │
│ ┌─────────────┐            ┌──────────────────┐                 │
│ │  Chainlit   │            │   Streamlit      │                 │
│ │  :8000      │            │   :8501          │                 │
│ │ (Learning)  │            │ (Analytics)      │                 │
│ └──────┬──────┘            └────────┬─────────┘                 │
└────────┼───────────────────────────┼──────────────────────────────┘
         │                           │
         └───────────────┬───────────┘
                         │
            ┌────────────▼────────────┐
            │   Nginx Reverse Proxy   │ (Single entry point)
            │   WebSocket routing     │
            └────────────┬────────────┘
                         │
            ┌────────────▼────────────┐
            │   FastAPI Backend       │
            │   /v1/chat/completions  │ (Chainlit)
            │   /api/student/*        │ (Streamlit)
            └────────────┬────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌────────┐    ┌────────────┐   ┌─────────┐
    │LangGraph   │  LiteLLM    │   │  Neo4j  │
    │ Workflow   │ (Blablador) │   │ (Memory)│
    └────────┘    └────────────┘   └─────────┘
```

**Layer Responsibilities:**
- **Chainlit** — Real-time tutor chat, streaming responses, interactive components
- **Streamlit** — Dashboard with analytics, progress tracking, vocab/grammar/test insights
- **FastAPI** — Shared backend orchestrating LangGraph workflow
- **LangGraph** — Multi-node routing: placement → drills → exercises
- **LiteLLM** — Unified interface to LLMs (Blablador, Ollama, OpenAI, Anthropic)
- **Neo4j** — Persistent student profiles, vocabulary confidence, grammar errors

## Features

- 🤖 **AI Tutor** - Conversational Italian learning with adaptive difficulty
- 📊 **Progress Tracking** - Neo4j stores student progress, vocabulary, and errors
- 🔄 **Multiple Exercise Types** - Grammar, vocabulary, translation, writing, exam prep
- 🎯 **CEFR Level Assessment** - Automatic placement test (A1-C2)
- 🌍 **Multi-Provider LLM** - Supports Ollama, Blablador, OpenAI, Anthropic via LiteLLM
- ☁️ **Cloud-Ready** - Works with Neo4j Aura (production) or local Neo4j

---

## Backend Implementation Status

### 📊 Current Progress

| Component | Status | Details |
|-----------|--------|---------|
| **Core FastAPI** | ✅ 100% | 8 endpoints (6 API + /auth/token + /auth/verify + /metrics) |
| **LangGraph Workflow** | ✅ 100% | All 7 nodes (router, chat, placement, grammar, vocab, translation, writing, niveau) |
| **Neo4j Integration** | ✅ 100% | Full CRUD: students, vocabulary, grammar errors, exercises |
| **LLMClient** | ✅ 100% | Async LiteLLM wrapper with system prompts |
| **Docker & Deployment** | ✅ 100% | Multi-stage Dockerfile, docker-compose, Aura overlay |
| **Middleware Stack** | ✅ 100% | **P0+P1 COMPLETE**: Logging, Auth, Error Handlers, Rate Limit, Timeout, Metrics |
| **Streaming Responses** | ✅ 100% | **P1 COMPLETE**: SSE endpoint, Chainlit-ready, component support |
| **JWT Authentication** | ✅ 100% | **P0 COMPLETE**: /auth/token, /auth/verify, 4h tokens with HS256 |
| **Configuration Management** | ✅ 100% | **P0 COMPLETE**: Pydantic Settings, startup validation, type-safe config |
| **Advanced Error Handling** | ✅ 100% | **P0 COMPLETE**: Custom exceptions, trace_ids, structured responses |
| **Rate Limiting** | ✅ 100% | **P1 COMPLETE**: Global + per-student limits, 429 responses, sliding window |
| **Request Timeout** | ✅ 100% | **P1 COMPLETE**: Per-endpoint timeouts, 408 responses, configurable |
| **Observability** | ✅ 100% | **P1 COMPLETE**: Prometheus metrics, /metrics endpoint, HTTP/LLM/DB tracking |

### ✅ What's Fully Implemented

**API Endpoints:**
- `GET /` — Root info endpoint
- `GET /health` — Full service health check (Neo4j + LiteLLM status)
- `POST /v1/chat/completions` — OpenAI-compatible format (returns single response)
- `POST /chat` — Simple chat endpoint
- `POST /students` — Create student
- `GET /students/{student_id}` — Get student + progress

**Core Infrastructure:**
- Global singleton pattern for Neo4j client & LangGraph
- Startup/shutdown event handlers for resource cleanup
- Error handling with HTTPException on all endpoints
- CORS middleware (unrestricted, needs refinement)

**LangGraph Workflow:**
- Router node determines next exercise based on user input
- 7 fully functional nodes: chat, placement, vocabulary, grammar, translation, free_writing, niveau_test
- All nodes loop back to router for multi-turn conversation
- TutorState TypedDict manages conversation state

**Neo4j Client:**
- Full async driver with connection pooling
- Student management: create, get, set level
- Vocabulary: add, retrieve, update confidence (spaced repetition)
- Grammar: record errors, retrieve error history
- Exercise tracking: record completions, get stats
- Connectivity verification

**Docker & DevOps:**
- Multi-stage Dockerfile (production-ready, non-root)
- Health check definition
- docker-compose.yml with Neo4j + LiteLLM services
- docker-compose.aura.yml overlay for Neo4j Aura cloud
- Environment variable configuration

### ✅ Phase P0 - Foundation (COMPLETE)

Infrastructure layer providing production-grade configuration, authentication, error handling, and logging.

**Files Implemented:**
- `src/italianollama/api/config.py` (200 lines) — Pydantic Settings with validation
- `src/italianollama/api/exceptions.py` (130 lines) — Custom exception hierarchy with trace_ids
- `src/italianollama/api/streaming.py` (100 lines) — SSE format helpers
- `src/italianollama/api/middleware/logging.py` (120 lines) — Request logging with X-Request-ID
- `src/italianollama/api/middleware/errors.py` (110 lines) — Global exception handlers
- `src/italianollama/api/middleware/auth.py` (160 lines) — JWT management (create/verify)
- `src/italianollama/api/main.py` (modified +150 lines) — Middleware integration, auth endpoints

**Features:**
✅ **Configuration Management** — Pydantic Settings with type validation, startup checks
✅ **JWT Authentication** — `/auth/token` generates 4h tokens, `/auth/verify` validates
✅ **Custom Exceptions** — 9 exception types with trace_id for debugging
✅ **Request Logging** — X-Request-ID header, method/path/status/duration tracking
✅ **Error Handling** — Global handlers catch all exceptions, return structured responses
✅ **SSE Foundation** — Helper functions for streaming response formatting

**Example Usage:**
```python
# Configuration with validation
settings = get_settings()  # Fails at startup if AUTH_SECRET missing

# JWT token generation
token = create_access_token("alice@example.com")  # 4h expiration

# Custom exceptions with trace_id
raise NotFoundError("Student", "Student 123 not found")
# Returns: {"error": "not_found", "trace_id": "req-abc123", "message": "..."}

# Streaming format
yield 'data: {"choices":[{"delta":{"content":"Ciao"}}]}\n\n'
```

### ✅ Phase P1 - Production Features (COMPLETE)

Production-ready features enabling streaming responses, rate limiting, timeouts, and observability.

**Files Implemented:**
- `src/italianollama/api/stream_adapter.py` (100 lines) — Streaming adapter for LangGraph output
- `src/italianollama/api/middleware/rate_limit.py` (180 lines) — Rate limiting middleware
- `src/italianollama/api/middleware/timeout.py` (90 lines) — Request timeout protection
- `src/italianollama/api/middleware/metrics.py` (250 lines) — Prometheus metrics collection
- `test_p1.py` (400 lines) — Comprehensive test suite
- `src/italianollama/api/main.py` (modified +80 lines) — P1 middleware registration

**Features:**

#### 1. Streaming Endpoint (SSE)
✅ **Real-time responses** — `/v1/chat/completions?stream=true` yields tokens incrementally
✅ **OpenAI-compatible** — Standard SSE format for Chainlit compatibility
✅ **Component support** — `__COMPONENT__:` prefix for interactive UI elements
✅ **Backwards compatible** — `stream=false` still returns single response

**Example:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -d '{"messages":[{"role":"user","content":"Ciao!"}],"stream":true}' \
  -N  # No buffering for real-time chunks

# Response (SSE):
data: {"choices":[{"delta":{"content":"Ciao"}}]}
data: {"choices":[{"delta":{"content":"!"}}]}
data: __COMPONENT__:drill_card|{"word":"ciao"}
data: [DONE]
```

#### 2. Rate Limiting (Multi-tier)
✅ **Global limits** — Per-endpoint limits (e.g., 100 req/min for LLM)
✅ **Per-student limits** — Extracted from JWT token (e.g., 50 req/hour for expensive ops)
✅ **Sliding window** — Fair algorithm, not fixed buckets
✅ **Proper responses** — 429 status with `Retry-After` header

**Configuration:**
```python
/auth/token: 10 req/min (brute force protection)
/v1/chat/completions: 100 req/min (global), 50 req/hour (per-student)
/chat: 100 req/min (global), 50 req/hour (per-student)
/students: 50 req/min (global), 100 req/hour (per-student)
Default: 1000 req/min (unrestricted)
```

#### 3. Request Timeout Protection
✅ **Per-endpoint configuration** — Different timeouts for different operations
✅ **Prevents hanging** — Returns 408 when exceeded
✅ **asyncio-based** — Non-blocking timeout wrapper

**Configuration:**
```python
/v1/chat/completions: 300s (LLM expensive)
/chat: 300s
/students: 30s
/health, /: 5s
Default: 30s
```

#### 4. Prometheus Metrics
✅ **HTTP tracking** — Request count, duration (min/avg/max), errors
✅ **LLM tracking** — Request count, latency
✅ **Neo4j tracking** — Query count by type, duration
✅ **/metrics endpoint** — Standard Prometheus text format

**Example Queries:**
```
sum by (path) (http_request_total)  # Requests per endpoint
rate(http_request_total[1m])        # Request rate
http_request_duration_ms            # Latency per endpoint
http_error_total                    # Errors by type
active_connections                  # Current connections
```

### 🟡 What Remains (Nice to Have)

| Issue | Current | Recommended |
|-------|---------|-------------|
| **In-memory Rate Limiting** | ✅ Works | Redis for distributed systems |
| **Metrics Persistence** | ✅ In-memory | Prometheus scraping + Grafana |
| **CORS** | ✅ Allowed | Add origin whitelist |
| **Router Logic** | ✅ String matching | Intent detection + keywords |
| **LLM Fallback** | None | Fallback to direct provider APIs |
| **Token Counting** | Not implemented | Track token usage for quota |

---

## Implementation Roadmap

### ✅ Phase P0 — Foundation (COMPLETED)

**Pydantic Configuration Management**
- ✅ Created `src/italianollama/api/config.py` with validated settings
- ✅ All env vars validated at startup
- ✅ Type-checked configuration with defaults
- ✅ Required vars fail early

**JWT Authentication**
- ✅ Created `src/italianollama/api/middleware/auth.py`
- ✅ `/auth/token` endpoint generates 4h JWT tokens
- ✅ `/auth/verify` endpoint validates tokens
- ✅ HS256 algorithm with shared AUTH_SECRET

**Custom Exception Hierarchy**
- ✅ Created `src/italianollama/api/exceptions.py`
- ✅ 9 exception types (400, 401, 403, 404, 409, 429, 503, 500)
- ✅ All include trace_id for debugging
- ✅ Structured error responses

**Request Logging Middleware**
- ✅ Created `src/italianollama/api/middleware/logging.py`
- ✅ X-Request-ID header on all requests
- ✅ Logs method/path/status/duration/client-ip
- ✅ Comprehensive coverage

**Error Handling Middleware**
- ✅ Created `src/italianollama/api/middleware/errors.py`
- ✅ Global exception catching
- ✅ No internal error leaks to frontend
- ✅ Proper HTTP status codes

### ✅ Phase P1 — Production Features (COMPLETED)

**Streaming Response Support**
- ✅ Created `src/italianollama/api/stream_adapter.py`
- ✅ `/v1/chat/completions?stream=true` returns SSE
- ✅ OpenAI-compatible format
- ✅ Token-by-token streaming
- ✅ Component support (`__COMPONENT__:` prefix)
- ✅ Chainlit integration ready

**Rate Limiting Middleware**
- ✅ Created `src/italianollama/api/middleware/rate_limit.py`
- ✅ Global per-endpoint limits configured
- ✅ Per-student limits for expensive operations
- ✅ Sliding window algorithm
- ✅ 429 responses with Retry-After header
- ✅ Extracting student_id from JWT or request

**Request Timeout Middleware**
- ✅ Created `src/italianollama/api/middleware/timeout.py`
- ✅ Per-endpoint timeout configuration
- ✅ 408 responses when exceeded
- ✅ Prevents resource exhaustion

**Prometheus Metrics Collection**
- ✅ Created `src/italianollama/api/middleware/metrics.py`
- ✅ `/metrics` endpoint with Prometheus format
- ✅ HTTP request tracking (count, duration, errors)
- ✅ LLM latency tracking
- ✅ Neo4j query tracking
- ✅ Active connection count

**Comprehensive Testing**
- ✅ Created `test_p1.py` test suite
- ✅ 5 test categories
- ✅ 15+ test scenarios
- ✅ Automated + manual procedures
- ✅ Example curl commands

### 🟡 Phase P2 — Frontend Integration (READY TO START)

**Chainlit Frontend**
- [ ] `frontend/chainlit/config.py` — Pydantic settings
- [ ] `frontend/chainlit/api/client.py` — SSE stream parser
- [ ] `frontend/chainlit/chainlit_app.py` — Chat interface
- [ ] `frontend/chainlit/components/` — Interactive components
- [ ] OAuth2 with Google (dev mode without credentials)

**Streamlit Dashboard**
- [ ] `frontend/streamlit/config.py` — Pydantic settings
- [ ] `frontend/streamlit/auth/session.py` — 3-layer auth
- [ ] `frontend/streamlit/api/client.py` — Typed API client
- [ ] `frontend/streamlit/pages/` — 5 analytics pages
- [ ] Metrics dashboard with Plotly charts

**Nginx Reverse Proxy**
- [ ] Named upstreams for chainlit and streamlit
- [ ] WebSocket upgrade headers
- [ ] 300s timeout configuration
- [ ] Health check aggregation

### 🟠 Phase P3 — Advanced Features (OPTIONAL)

- [ ] Redis for distributed rate limiting
- [ ] OpenTelemetry distributed tracing
- [ ] Real LLM streaming (not mocked)
- [ ] Circuit breaker for external services
- [ ] Token usage quota tracking
- [ ] Database connection pooling optimization

---

## Backend Features Guide (P0 & P1)

### Phase P0 Features — Configuration & Authentication

#### Configuration Management

All configuration is validated at startup using Pydantic Settings:

```python
# File: src/italianollama/api/config.py
# Automatically loads and validates environment variables

from italianollama.api.config import get_settings

settings = get_settings()
# Fails immediately if required vars missing (AUTH_SECRET, etc)
```

**Required Environment Variables:**
```bash
AUTH_SECRET=your-secret-key  # Required for JWT signing
NEO4J_URI=neo4j+s://...      # Required
NEO4J_USER=neo4j             # Required
NEO4J_PASSWORD=...           # Required
```

**Optional Configuration:**
```bash
LOG_LEVEL=INFO               # Default: INFO
JWT_EXPIRATION_HOURS=4       # Default: 4
CORS_ORIGINS=localhost:3000  # Default: localhost:3000,8000,8501
```

#### JWT Authentication

Generate tokens for students or frontends:

```bash
# Generate a token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"student_id": "alice@example.com"}'

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 14400  # 4 hours in seconds
}

# Verify token
curl -X POST http://localhost:8000/auth/verify \
  -H "Authorization: Bearer {token}"

# Response:
{
  "valid": true,
  "student_id": "alice@example.com",
  "exp": 1711800123
}
```

**Token Usage:**
```python
# In Chainlit
async def authenticate_student(student_id: str):
    response = await client.post(
        "http://localhost:8000/auth/token",
        json={"student_id": student_id}
    )
    token = response.json()["access_token"]
    return token

# In Streamlit (session management)
cl.user_session.set("token", token)
```

#### Error Handling

All errors return structured responses with trace IDs:

```python
# Example request that fails
curl -X POST http://localhost:8000/v1/chat/completions \
  -d '{"no":"messages"}'

# Response (400 Bad Request):
{
  "detail": {
    "error": "validation_error",
    "message": "No messages provided",
    "trace_id": "req-12345678"  # Use for debugging
  }
}
```

**Error Types:**
- `400` — Validation error (bad input)
- `401` — Unauthorized (bad JWT)
- `403` — Forbidden (no access)
- `404` — Not found (resource missing)
- `429` — Rate limited
- `408` — Request timeout
- `500` — Server error

### Phase P1 Features — Streaming, Rate Limiting, Metrics

#### Streaming Responses

Enable real-time response streaming for Chainlit:

```bash
# Non-streaming (default)
curl -X POST http://localhost:8000/v1/chat/completions \
  -d '{"messages":[{"role":"user","content":"Ciao!"}]}'

# Returns full response in one chunk:
{"choices":[{"message":{"content":"Ciao! Come stai?","role":"assistant"}}]}


# Streaming (new in P1)
curl -X POST http://localhost:8000/v1/chat/completions \
  -d '{"messages":[{"role":"user","content":"Ciao!"}],"stream":true}' \
  -N  # -N disables buffering for real-time chunks

# Returns Server-Sent Events (SSE):
data: {"choices":[{"delta":{"content":"Ciao"}}]}
data: {"choices":[{"delta":{"content":"!"}}]}
data: {"choices":[{"delta":{"content":" Come"}}]}
data: {"choices":[{"delta":{"content":" stai"}}]}
data: {"choices":[{"delta":{"content":"?"}}]}
data: [DONE]
```

**Chainlit Integration:**

```python
import httpx
import json

async def stream_from_tutor(message: str):
    async with httpx.AsyncClient() as client:
        with client.stream(
            "POST",
            "http://localhost:8000/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": message}],
                "stream": True  # Enable streaming
            },
            timeout=300,
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        token = chunk["choices"][0]["delta"].get("content", "")
                        if token:
                            yield token
                    except:
                        pass
```

#### Rate Limiting

API is rate-limited to prevent abuse:

```bash
# Making requests beyond the limit returns 429:
curl -X POST http://localhost:8000/auth/token \
  -d '{"student_id":"test"}' \
  -w "\nStatus: %{http_code}\n"

# Response (after limit):
# Status: 429
{
  "detail": {
    "error": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "retry_after": 60
  }
}
```

**Current Limits:**

| Endpoint | Global Limit | Per-Student Limit |
|----------|-------------|------------------|
| `/auth/token` | 10 req/min | — |
| `/auth/verify` | 50 req/min | — |
| `/v1/chat/completions` | 100 req/min | 50 req/hour |
| `/chat` | 100 req/min | 50 req/hour |
| `/students` | 50 req/min | 100 req/hour |
| Others | 1000 req/min | — |

**Handling Rate Limits (Client-side):**

```python
import asyncio
import httpx

async def call_with_retry(endpoint, data, max_retries=3):
    for attempt in range(max_retries):
        response = await client.post(endpoint, json=data)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:
            error = response.json()['detail']
            retry_after = error['retry_after']

            if attempt < max_retries - 1:
                await asyncio.sleep(retry_after)
            else:
                raise Exception(f"Rate limited after {max_retries} attempts")
        else:
            raise Exception(f"Server error: {response.status_code}")
```

#### Request Timeout

Long-running requests are automatically terminated:

```bash
# LLM endpoints timeout after 300 seconds
# Regular endpoints timeout after 30 seconds
# Health check times out after 5 seconds

# If timeout exceeded:
# Status: 408
{
  "detail": {
    "error": "request_timeout",
    "message": "Request exceeded timeout of 300 seconds",
    "timeout": 300,
    "path": "/v1/chat/completions"
  }
}
```

#### Prometheus Metrics

Metrics are collected and exposed at `/metrics` endpoint:

```bash
# Get all metrics
curl http://localhost:8000/metrics | head -20

# Output (Prometheus format):
# HELP http_request_total Total HTTP requests
# TYPE http_request_total counter
http_request_total{path="/auth/token",status="200"} 5
http_request_total{path="/auth/token",status="429"} 2

# HELP http_request_duration_ms HTTP request duration in milliseconds
# TYPE http_request_duration_ms gauge
http_request_duration_ms{path="/auth/token",quantile="avg"} 12.50
http_request_duration_ms{path="/auth/token",quantile="min"} 8.20
http_request_duration_ms{path="/auth/token",quantile="max"} 18.90
```

**Common Queries:**

```bash
# Track request rate per endpoint
curl -s http://localhost:8000/metrics | grep "http_request_total{path"

# Get LLM latency
curl -s http://localhost:8000/metrics | grep "llm_request_duration"

# Check error rates
curl -s http://localhost:8000/metrics | grep "http_error_total"

# Active connections
curl -s http://localhost:8000/metrics | grep "active_connections"
```

**Integration with Prometheus/Grafana:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'italian-tutor'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)
- Neo4j Aura instance (or local Neo4j)
- LLM API access (Blablador, OpenAI, or local Ollama)

### 1. Clone & Configure

```bash
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
```

Create `.env` file:

```bash
# Neo4j Aura (Cloud) - RECOMMENDED
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=your_username
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
USE_AURA=true

# Or Local Neo4j
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_password
# USE_AURA=false

# Blablador (Helmholtz LLM) - RECOMMENDED
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_api_key
BLABLADOR_MODEL=alias-fast

# Or Ollama (local)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2

# LiteLLM Settings
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy

# App Settings
LOG_LEVEL=INFO
```

### 2. Start Services

**With Neo4j Aura + Blablador (Production):**
```bash
cd backend
docker compose -f docker-compose.yml -f docker-compose.aura.yml up -d
```

**With Local Neo4j:**
```bash
cd backend
docker compose up -d
```

### 3. Access

| Service | URL | Purpose |
|---------|-----|---------|
| **Chat** | http://localhost/chat | Sofia tutor (Chainlit) |
| **Dashboard** | http://localhost/dashboard | Progress & analytics (Streamlit) |
| **API** | http://localhost/api/docs | Backend documentation |
| **Nginx** | http://localhost:80 | Main entry point |

**Development URLs (without Nginx):**
- Chainlit: http://localhost:8000
- Streamlit: http://localhost:8501
- FastAPI: http://localhost:8000/docs

---

## Project Structure

```
ItalianOllama/
├── frontend/                          # ✨ NEW: Dual frontend architecture
│   ├── chainlit/                      # Chat UI (Sofia tutor)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .chainlit/
│   │   │   └── config.toml
│   │   ├── config.py                 # Pydantic settings
│   │   ├── chainlit_app.py           # Main chat app
│   │   ├── api/
│   │   │   └── client.py             # FastAPI SSE parser
│   │   ├── auth/
│   │   │   └── oauth.py              # Google OAuth2 + JWT
│   │   └── components/               # Interactive elements
│   │       ├── __init__.py           # Component registry
│   │       ├── base.py               # BaseComponent class
│   │       ├── drill_card.py         # Flashcard with buttons
│   │       ├── grammar_feedback.py   # Annotated corrections
│   │       ├── score_badge.py        # Graded results
│   │       ├── placement_quiz.py     # MCQ with progress bar
│   │       └── writing_review.py     # Corrected text display
│   │
│   └── streamlit/                     # Dashboard UI (Analytics)
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app.py                    # Main dashboard + sidebar
│       ├── config.py                 # Pydantic settings
│       ├── auth/
│       │   └── session.py            # JWT → session → email gate
│       ├── api/
│       │   └── client.py             # Typed API client + caching
│       ├── components/               # Reusable UI components
│       │   ├── kpi_row.py            # KPI cards (CEFR, vocab, etc)
│       │   ├── confidence_table.py   # Sortable drill results
│       │   └── radar_chart.py        # Skill radar profile
│       └── pages/                    # Streamlit multi-page app
│           ├── 1_progress.py         # CEFR level & milestones
│           ├── 2_vocabulary.py       # Vocab insights & spaced reps
│           ├── 3_grammar.py          # Error patterns & rules
│           ├── 4_knowledge_graph.py  # Student memory graph
│           └── 5_test_readiness.py   # Exam simulation results
│
├── backend/                           # Existing backend services
│   ├── docker-compose.yml             # Local Neo4j + LiteLLM
│   ├── docker-compose.aura.yml        # Neo4j Aura overlay
│   ├── Dockerfile (non-root, multi-stage)
│   ├── litellm/
│   │   └── litellm_config.yaml
│   └── requirements.txt
│
├── src/italianollama/                 # Main package
│   ├── __init__.py
│   ├── api/                           # FastAPI endpoints
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── main.py                   # /chat, /students, /health
│   ├── cli/                           # CLI commands
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── main.py
│   ├── graph/                         # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── state.py                  # TutorState TypedDict
│   │   ├── graph.py                  # Graph builder & router
│   │   └── nodes/                    # LangGraph nodes (5 exercise types)
│   │       ├── __init__.py
│   │       ├── base.py               # LLMClient wrapper
│   │       ├── placement.py          # CEFR A1-C2 placement test
│   │       ├── vocabulary.py         # Flashcard drills
│   │       ├── grammar.py            # Grammar error detection
│   │       ├── translation.py        # IT↔EN translation practice
│   │       ├── free_writing.py       # Open writing + feedback
│   │       └── niveau_test.py        # TELC/Goethe exam prep
│   └── memory/                        # Neo4j client
│       ├── __init__.py
│       └── neo4j_client.py           # CRUD operations
│
├── tests/                             # Test suite
│   └── __init__.py
│
├── pyproject.toml                     # Poetry config
├── poetry.toml                        # Poetry local settings
├── requirements.txt                   # Main dependencies
├── docker-compose.yml                 # Complete stack
├── Dockerfile                         # Main app image (non-root)
├── LICENSE
├── README.md                          # Project overview
├── README_TUTOR.md                    # This file
├── cli.py                             # CLI entry point
└── secrets/                           # API keys (git-ignored)
    ├── neo4j_aura_*                   # Neo4j Aura credentials
    ├── openai_api_key.txt
    ├── anthropic_api_key.txt
    └── ...
```

### Module Details

| Module | Description |
|--------|-------------|
| `api/main.py` | FastAPI app with chat, student, and health endpoints |
| `graph/graph.py` | LangGraph builder with router node |
| `graph/state.py` | TutorState TypedDict defining conversation state |
| `graph/nodes/base.py` | LLMClient for LiteLLM communication |
| `graph/nodes/placement.py` | CEFR level assessment (A1-C2) |
| `graph/nodes/vocabulary.py` | Flashcard system with spaced repetition |
| `graph/nodes/grammar.py` | Grammar exercises with error detection |
| `graph/nodes/translation.py` | Italian↔English translation practice |
| `graph/nodes/free_writing.py` | Open writing prompts with feedback |
| `graph/nodes/niveau_test.py` | TELC/Goethe-style exam simulation |
| `memory/neo4j_client.py` | Neo4j operations for student data |

---

## LangGraph Workflow

```
┌─────────────┐
│   router    │ ← Entry point - determines next node
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌────────┐ │
│  │placement │  │vocabulary │  │ grammar │  │  chat  │ │
│  │  (CEFR)  │  │(flashcard)│  │ (drills)│  │ (free) │ │
│  └────┬─────┘  └─────┬─────┘  └────┬────┘  └────┬───┘ │
│       │              │             │            │     │
│       └──────────────┴─────────────┴────────────┘     │
│                         │                              │
└─────────────────────────┼──────────────────────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │   router    │ ← Loops back
                    └─────────────┘
```

---

## Development Phases

### Backend Phases (Core LangGraph Workflow)

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 0 | ✅ DONE | Project setup & Docker |
| Phase 1 | ✅ DONE | FastAPI skeleton with Sofia |
| Phase 2 | ✅ DONE | Neo4j client with student memory |
| Phase 3 | ✅ DONE | Placement test node (CEFR A1-C2) |
| Phase 4 | ✅ DONE | Vocabulary flashcards + spaced repetition |
| Phase 5 | ✅ DONE | Grammar drills + error detection |
| Phase 6 | ✅ DONE | Translation exercises (IT↔EN) |
| Phase 7 | ✅ DONE | Free writing with feedback |
| Phase 8 | ✅ DONE | Niveau test prep (TELC/Goethe) |

### Frontend Phases (Chainlit Chat + Streamlit Dashboard)

| Phase | Status | Description |
|-------|--------|-------------|
| **F1** | 🔴 PENDING | **Chainlit Skeleton** — `config.py`, `api/client.py` SSE parser, `chainlit_app.py` fetches student profile on start, non-root multi-stage Dockerfile |
| **F2** | 🔴 PENDING | **Component System** — `BaseComponent` abstract class, `COMPONENT_REGISTRY` dict, dispatch on `__COMPONENT__:` token prefix. All 5 components (DrillCard, GrammarFeedback, ScoreBadge, PlacementQuiz, WritingReview) |
| **F3** | 🔴 PENDING | **OAuth2 Auth** — `auth/oauth.py`, `make_dashboard_token()` (4h JWT), `@cl.oauth_callback`, dev mode works without credentials |
| **F4** | 🔴 PENDING | **Streamlit Skeleton** — `config.py`, `auth/session.py` (3-layer: JWT → session → email), `api/client.py` with typed `_get()` and `@st.cache_data(ttl=...)` |
| **F5** | 🔴 PENDING | **All 5 Pages** — Progress, Vocabulary, Grammar, Knowledge Graph, Test Readiness. All require `require_student()` auth. Shared components: `kpi_row`, `confidence_table`, `radar_chart` |
| **F6** | 🔴 PENDING | **Nginx** — Named upstreams, 300s timeout, WebSocket upgrade, `/health` endpoint |
| **F7** | 🔴 PENDING | **JWT SSO** — Shared `AUTH_SECRET`, dashboard link in Chainlit greeting with token, single login |

### Phase Details and Features

**Phase F1 — Chainlit Skeleton**
- `config.py` with Pydantic settings + env override
- `api/client.py`: SSE stream parser that handles `data:` lines, `[DONE]`, malformed JSON
- `chainlit_app.py`: Fetches student profile from FastAPI on session start, displays CEFR greeting
- Non-root Dockerfile with Alpine base + multi-stage build

**Phase F2 — Component System**
- `BaseComponent` abstract class with `render()` interface
- `COMPONENT_REGISTRY` dict maps mode names to class constructors
- `chainlit_app.py` detects `__COMPONENT__:` prefix in token stream, stops text rendering, dispatches to right component
- **Adding a new exercise = 1 file + 1 registry entry**
- All 5 components fully interactive:
  - `DrillCard` — Flashcard reveal/correct/wrong buttons, live Neo4j confidence update
  - `GrammarFeedback` — Annotated correction with inline error list
  - `ScoreBadge` — Graded (Excellent/Good/Fair/Keep going) with breakdown
  - `PlacementQuiz` — Progress bar + MCQ buttons + FastAPI answer recording
  - `WritingReview` — Corrected text + highlights + extracted vocab

**Phase F3 — OAuth2 Auth**
- `auth/oauth.py` with Google OAuth provider config
- `make_dashboard_token()` creates 4h expiring JWT
- `@cl.oauth_callback` stores token in session
- `on_start` appends dashboard link only when auth enabled — **dev mode works without Google credentials**

**Phase F4 — Streamlit Skeleton**
- `config.py` with Pydantic settings
- `auth/session.py` with 3-layer auth: JWT validation → session cache → email gate
- `api/client.py` with typed `_get()` helper + `@st.cache_data(ttl=...)` on all 5 endpoints
- `app.py` main entry with sidebar logout button

**Phase F5 — All 5 Pages**
- Every page calls `require_student()` at top — auth guaranteed regardless of direct URL
- Shared components for consistency: `kpi_row` (KPI cards), `confidence_table` (sortable), `radar_chart` (skills)
- All handle empty states gracefully with `st.stop()`
- Pages: Progress (milestones), Vocabulary (insights), Grammar (error patterns), Knowledge Graph (Neo4j viz), Test Readiness (exam sim)

**Phase F6 — Nginx**
- Named upstreams for chainlit:8000 and streamlit:8501
- 300s timeout for long-running requests
- WebSocket upgrade headers for both services
- `/health` endpoint aggregates both service checks

**Phase F7 — JWT SSO**
- Shared `AUTH_SECRET` between services (bash command to generate)
- Student never sees second login
- Dashboard link in Chainlit greeting carries token

**Legend:**
- ✅ DONE — Fully implemented & tested
- 🔴 PENDING — Not yet implemented

---

## Frontend Architecture

### Dual-Frontend Approach

The Italian Tutor separates concerns into two independent frontends sharing a single FastAPI backend:

| Layer | Tool | Port | Purpose | Tech Stack |
|-------|------|------|---------|-----------|
| **Chat** | Chainlit | 8000 | Real-time Sofia tutor | Python, Chainlit, SSE streams |
| **Dashboard** | Streamlit | 8501 | Analytics & progress | Python, Streamlit, Plotly |
| **Reverse Proxy** | Nginx | 80/443 | Single entry point, routing | Nginx, WebSocket support |
| **API** | FastAPI | 8000 (internal) | Shared backend | Python, FastAPI, LangGraph |

### Chainlit (Chat Interface)

**Location:** `frontend/chainlit/`

**Key Features:**
- LangGraph-native streaming with `async` support
- Component system for rendering interactive UI (flashcards, quizzes, reviewed text)
- OAuth2 integration with Google
- SSE client for parsing streamed responses from FastAPI

**Component Registry:**
```python
COMPONENT_REGISTRY = {
    "drill": DrillCard,
    "grammar": GrammarFeedback,
    "score": ScoreBadge,
    "quiz": PlacementQuiz,
    "review": WritingReview,
}
```

**Flow:**
1. Student authenticates via OAuth (or dev mode)
2. Fetch student profile on session start → display CEFR greeting
3. Stream response from `/v1/chat/completions` → parse SSE
4. Detect `__COMPONENT__:` prefix → dispatch to component
5. Component renders interactive UI + updates Neo4j on user action

### Streamlit (Dashboard)

**Location:** `frontend/streamlit/`

**Key Features:**
- Multi-page analytics dashboard
- 3-layer authentication: JWT → session cache → email gate
- Typed API client with `@st.cache_data()` for 5 shared endpoints
- Shared components: KPI row, confidence table, radar chart

**Pages:**
1. **Progress** — CEFR level, total vocab, grammar errors, milestones
2. **Vocabulary** — Confidence breakdown, spaced repetition schedule, topic clouds
3. **Grammar** — Top error patterns, rules violated, practice recommendations
4. **Knowledge Graph** — Neo4j visualization, student memory nodes, relationship explorer
5. **Test Readiness** — Exam simulation scores, skill gaps, TELC/Goethe readiness

**Auth Flow:**
- Dashboard link in Chainlit greeting carries 4h JWT token
- `session.py` validates JWT → stores session → gates by email
- Dev mode works without Google credentials

### API Endpoints (Shared Backend)

**Chat Endpoints:**
```
POST /v1/chat/completions          (OpenAI-compatible, for Chainlit)
POST /chat                          (Simple wrapper)
GET  /students/{id}                 (Fetch student + progress)
POST /students                      (Create student)
GET  /health                        (Both services)
```

**Stream Format (from `/v1/chat/completions`):**
```
data: {"choices": [{"delta": {"content": "Hello,"}}]}
data: {"choices": [{"delta": {"content": " hello"}}]}
data: __COMPONENT__:drill_card|{"word": "ciao", "translation": "hello"}
data: [DONE]
```

---

## Neo4j Schema

```cypher
# Student node with CEFR level
(:Student {student_id, name, created_at})-[:HAS_LEVEL]->(:CEFRLevel {code, confidence})

# Vocabulary with spaced repetition
(:Student)-[:KNOWS]->(:Vocabulary {word, translation, topic, level, confidence, last_practiced})

# Grammar error tracking
(:Student)-[:MADE_ERROR]->(:GrammarError {original, corrected, rule, level, seen_count})

# Exercise history
(:Student)-[:COMPLETED]->(:Exercise {type, score, level, content, completed_at})

# Niveau test results
(:Student)-[:READY_FOR]->(:NiveauTest {test_type, level, readiness, skill_scores, completed_at})
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check (Neo4j, LiteLLM) |
| `/v1/chat/completions` | POST | OpenAI-compatible chat |
| `/chat` | POST | Simple chat with student_id |
| `/students` | POST | Create student |
| `/students/{id}` | GET | Get student info & progress |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | - |
| `NEO4J_DATABASE` | Neo4j database | `neo4j` |
| `LITELLM_BASE_URL` | LiteLLM API URL | `http://litellm:4000` |
| `LITELLM_MODEL` | Model name | `tutor` |
| `LITELLM_API_KEY` | API key | `dummy` |

## LLM Providers

### Blablador (Recommended)
```bash
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_key
```

### Ollama (Local)
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### OpenAI
```bash
OPENAI_API_KEY=sk-...
```

## Deployment

### Production Stack (with Nginx + JWT SSO)

```bash
# Generate secure JWT secret
AUTH_SECRET=$(openssl rand -hex 32)
echo $AUTH_SECRET  # Save this value

# Set environment variables
export AUTH_SECRET=$AUTH_SECRET
export NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
export NEO4J_USER=your_user
export NEO4J_PASSWORD=your_pass
export BLABLADOR_API_KEY=your_key

# Start complete stack with Nginx
cd frontend/
docker compose up -d
```

### Docker Compose Stack

**`frontend/docker-compose.yml`** includes:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs/:/etc/nginx/certs/:ro
    depends_on:
      - chainlit
      - streamlit

  chainlit:
    build: ./chainlit/
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - AUTH_SECRET=${AUTH_SECRET}
      - LITELLM_BASE_URL=http://api:8000
      - BLABLADOR_API_URL=${BLABLADOR_API_URL}
      - BLABLADOR_API_KEY=${BLABLADOR_API_KEY}
    expose:
      - 8000

  streamlit:
    build: ./streamlit/
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - AUTH_SECRET=${AUTH_SECRET}
      - API_BASE_URL=http://api:8000
    expose:
      - 8501

  api:
    build: ../backend/
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - LITELLM_BASE_URL=http://litellm:4000
      - BLABLADOR_API_URL=${BLABLADOR_API_URL}
      - BLABLADOR_API_KEY=${BLABLADOR_API_KEY}
    expose:
      - 8000
```

### Nginx Configuration

**Key features:**
- Named upstreams for service discovery
- 300s timeout for streaming responses
- WebSocket upgrade headers for both services
- Health check aggregation

```nginx
upstream chainlit {
    server chainlit:8000;
}

upstream streamlit {
    server streamlit:8501;
}

upstream api {
    server api:8000;
}

server {
    listen 80;
    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;

    # Chat route
    location /chat/ {
        proxy_pass http://chainlit/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Dashboard route
    location /dashboard/ {
        proxy_pass http://streamlit/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Script-Name /dashboard;
    }

    # API routes
    location /api/ {
        proxy_pass http://api/;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        access_log off;
        proxy_pass http://api/health;
    }

    # Redirect root to chat
    location / {
        return 301 /chat/;
    }
}
```

### Frontend Environment Variables

**`frontend/chainlit/.env`:**
```bash
CHAINLIT_AUTH_SECRET=${AUTH_SECRET}
NEO4J_URI=${NEO4J_URI}
NEO4J_USER=${NEO4J_USER}
NEO4J_PASSWORD=${NEO4J_PASSWORD}
LITELLM_BASE_URL=http://api:8000
BLABLADOR_API_URL=${BLABLADOR_API_URL}
BLABLADOR_API_KEY=${BLABLADOR_API_KEY}
```

**`frontend/streamlit/.env`:**
```bash
STREAMLIT_AUTH_SECRET=${AUTH_SECRET}
NEO4J_URI=${NEO4J_URI}
NEO4J_USER=${NEO4J_USER}
NEO4J_PASSWORD=${NEO4J_PASSWORD}
API_BASE_URL=http://api:8000
```

### Development Mode (Without Nginx)

Run frontends separately for debugging:

```bash
# Terminal 1: Backend
cd backend/
docker compose up -d

# Terminal 2: Chainlit
cd frontend/chainlit/
python -m streamlit run chainlit_app.py --server.port 8000

# Terminal 3: Streamlit
cd frontend/streamlit/
python -m streamlit run app.py --server.port 8501
```

---

## Troubleshooting

### Backend Services
```bash
# Check all services
docker compose ps

# View logs
docker compose logs -f

# Test Neo4j
docker compose exec neo4j cypher-shell -u neo4j -p password "RETURN 1"

# Test LiteLLM
curl http://localhost:4000/health
```

### Chainlit Issues

**Component not rendering?**
- Check if token stream includes `__COMPONENT__:` prefix
- Verify component is registered in `COMPONENT_REGISTRY`
- Check browser console for SSE parsing errors

**OAuth not working?**
```bash
# Dev mode (no Google credentials needed)
export DISABLE_OAUTH=true
python -m chainlit run chainlit_app.py --dev
```

**SSE stream parsing errors?**
```python
# Test SSE parser directly
from api.client import parse_sse_stream
stream = "data: {\"choices\": [{\"delta\": {\"content\": \"test\"}}]}\n\n"
result = parse_sse_stream(stream)
```

### Streamlit Issues

**Auth session not persisting?**
- Check if `AUTH_SECRET` environment variable is set correctly
- Verify JWT token format matches expected schema
- Check session cache TTL in `auth/session.py`

**API calls failing?**
- Verify API upstreams are healthy: `curl http://api:8000/health`
- Check if `API_BASE_URL` matches your deployment
- Ensure `@st.cache_data(ttl=...)` decorators aren't competing

**Dashboard pages not loading?**
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/
rm -rf .streamlit/

# Run in dev mode with verbose logging
streamlit run app.py --logger.level=debug
```

### Nginx Routing

**Frontend not accessible?**
```bash
# Test Nginx config
docker compose exec nginx nginx -t

# Check upstream connectivity
docker compose exec nginx curl -v http://chainlit:8000
docker compose exec nginx curl -v http://streamlit:8501

# View Nginx logs
docker compose logs nginx
```

**WebSocket connection failing?**
- Verify Nginx has `Upgrade` and `Connection` headers for `/chat/` route
- Check if firewall blocks WebSocket (port 443/80)
- Test with: `curl -i -N -H "Connection: Upgrade" http://localhost/chat/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the module structure
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file

## Credits

- [LangGraph](https://langchain-ai.github.io/langgraph/) - Graph-based agent orchestration
- [Neo4j](https://neo4j.com/) - Graph database
- [LiteLLM](https://litellm.ai/) - Unified LLM interface
- [Chainlit](https://chainlit.io/) - Chat UI with components & OAuth
- [Streamlit](https://streamlit.io/) - Analytics dashboard framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern async web framework
- [Nginx](https://nginx.org/) - High-performance reverse proxy
