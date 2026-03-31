# ItalianOllama Technical Documentation & Roadmap

This document contains the detailed technical implementation, architecture, and roadmap for the ItalianOllama platform.

## Architecture Overview

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

## Implementation Status

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
| **Onboarding Workflow** | ✅ 100% | **P2 COMPLETE**: Streamlit shell + onboarding |
| **Dashboard Visuals** | ✅ 100% | **P2 COMPLETE**: 6 pages, Plotly charts, st-link-analysis |

## 10-Step Development Roadmap

### ✅ Phase P0 — Foundation (COMPLETE)
- [x] **Pydantic Configuration Management**: Validated settings, type-checked config.
- [x] **JWT Authentication**: `/auth/token`, `/auth/verify`, HS256 algorithm.
- [x] **Custom Exception Hierarchy**: Trace IDs, structured error responses.
- [x] **Logging & Error Middlewares**: X-Request-ID tracking, global error handling.

### ✅ Phase P1 — Production Features (COMPLETE)
- [x] **Streaming (SSE)**: OpenAI-compatible real-time responses.
- [x] **Rate Limiting**: Multi-tier global and per-student limits.
- [x] **Request Timeouts**: Protection for long-running LLM operations.
- [x] **Prometheus Metrics**: HTTP tracking, LLM latency, Neo4j monitoring.

### ✅ Phase P2 — Frontend Integration (COMPLETE)
- [x] **Chainlit Update**: Student_id support in query params, SSE parsing.
- [x] **Streamlit Shell**: Personalized onboarding, 7-step UX flow.
- [x] **Dashboard Suite**: 6 interactive analytics and chat pages.
- [x] **JWT SSO**: Shared AUTH_SECRET between services.

### 🟡 Phase P3 — Advanced Features (OPTIONAL)
- [ ] Redis for distributed rate limiting.
- [ ] OpenTelemetry distributed tracing.
- [ ] Real LLM streaming (not mocked).
- [ ] Circuit breaker for external services.
- [ ] Token usage quota tracking.
- [ ] Database connection pooling optimization.

---

## Technical Details

### Backend API (P0 & P1)

#### Configuration Management
All configuration is validated at startup using Pydantic Settings.

```bash
# Required Environment Variables
AUTH_SECRET=your-secret-key  # JWT signing
NEO4J_URI=neo4j+s://...      # Neo4j URI
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
```

#### JWT Authentication
Generate tokens for students or frontends via `/auth/token`.

```bash
# Example Token Generation
curl -X POST http://localhost:8000/auth/token 
  -H "Content-Type: application/json" 
  -d '{"student_id": "alice@example.com"}'
```

#### Streaming Responses
Real-time response streaming via SSE.

```bash
# Streaming (SSE)
curl -X POST http://localhost:8000/v1/chat/completions 
  -d '{"messages":[{"role":"user","content":"Ciao!"}],"stream":true}' -N
```

### Neo4j Schema & Spaced Repetition

```cypher
# Student node with CEFR level
(:Student {student_id, name, created_at})-[:HAS_LEVEL]->(:CEFRLevel {code, confidence})

# Vocabulary with spaced repetition
(:Student)-[:KNOWS]->(:Vocabulary {word, translation, topic, level, confidence, last_practiced})

# Grammar error tracking
(:Student)-[:MADE_ERROR]->(:GrammarError {original, corrected, rule, level, seen_count})

# Exercise history
(:Student)-[:COMPLETED]->(:Exercise {type, score, level, content, completed_at})
```

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

## LLM Providers

### Blablador (Recommended)
```bash
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_key
BLABLADOR_MODEL=alias-fast
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

## Module Details

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
| `memory/neo4j_client.py` | Neo4j operations for student data & stats |

## Project Structure

```
ItalianOllama/
├── frontend/                          # Integrated frontend architecture
│   ├── chainlit/                      # Chat UI (Sofia tutor)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── config.py                 # Pydantic settings
│   │   ├── chainlit_app.py           # Main chat app
│   │   ├── api/
│   │   │   └── client.py             # FastAPI SSE parser
│   │   └── ui/                       # Modular UI components
│   │
│   └── streamlit/                     # Dashboard UI (Analytics)
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app.py                    # Main dashboard + onboarding
│       ├── config.py                 # Pydantic settings
│       ├── auth/
│       │   └── session.py            # JWT → session → email gate
│       └── pages/                    # Multi-page dashboard
│
├── src/italianollama/                 # Main package
│   ├── api/                           # FastAPI backend
│   ├── cli/                           # CLI service management
│   ├── graph/                         # LangGraph orchestration
│   │   ├── state.py                  # TutorState TypedDict
│   │   ├── graph.py                  # Graph builder & router
│   │   └── nodes/                    # 7 specialized exercise nodes
│   └── memory/                        # Neo4j client & stats
│
├── tests/                             # Comprehensive test suite
├── pyproject.toml                     # Poetry configuration
└── DEVELOPMENT.md                     # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | - |
| `AUTH_SECRET` | Secret for JWT signing | - |
| `LITELLM_BASE_URL` | LiteLLM API URL | `http://litellm:4000` |
| `BACKEND_URL` | API endpoint for frontend | `http://localhost:8000` |
| `CHAINLIT_URL` | Chat endpoint for Streamlit | `http://localhost:8501` |

## Deployment & Production

### 1. Unified CLI Management
The built-in CLI handles the orchestration of all services. You can override ports using environment variables if there are conflicts (e.g., with SSH tunnels):

```bash
# Optional: Override default ports if 8000, 8501, or 8502 are busy
export API_PORT=8001
export CHAINLIT_PORT=8503
export STREAMLIT_PORT=8504

poetry run italianollama service start all
poetry run italianollama service status
poetry run italianollama service logs api
```

### 2. Docker Stack
For production, use the multi-stage Docker setup:
```bash
cd backend
docker compose up -d
```

### 3. Nginx Configuration (Recommended)
Use Nginx as a reverse proxy to unify the routes:
- `/chat/` -> `chainlit:8501`
- `/dashboard/` -> `streamlit:8502`
- `/api/` -> `api:8000`

---

## 10-Step GraphRAG Implementation Plan

Sofia's grammar knowledge is grounded in a GraphRAG knowledge graph built from Italian grammar rules:

1.  **Source Materials**: Ingest Sensini Grammatica Italiana and CEFR descriptors.
2.  **Graph Schema**: Nodes for `GrammarRule`, `Example`, `Exception`, `CEFRLevel`.
3.  **Ingestion Pipeline**: Text splitters + LLM entity extractors to build the graph.
4.  **Constraints**: Full-text and vector indexes for hybrid search.
5.  **Hybrid Retriever**: Vector search finds rules, Cypher traversal pulls related examples.
6.  **LangGraph Integration**: The `grammar_node` retrieves book context to eliminate hallucinations.
7.  **API Support**: Endpoint for structured grammar lookups.
8.  **Dashboard Integration**: Live "Grammar Book" search in the Streamlit UI.
9.  **Docker Profile**: One-time ingestion service via Docker.
10. **Verification**: Automated Cypher queries to confirm rule coverage.

---

## Troubleshooting & FAQ

### Backend Services
- **Check status**: `docker compose ps`
- **View logs**: `docker compose logs -f api`
- **Test Neo4j**: `docker compose exec neo4j cypher-shell -u neo4j -p password "RETURN 1"`

### Chainlit Embed Issues
- If the chat doesn't load student profile, ensure `CHAINLIT_URL` environment variable includes `student_id` parameter or Streamlit is correctly passing it.

### Auth Issues
- Ensure `AUTH_SECRET` is identical across all three services (API, Chainlit, Streamlit).

---

## Contributing
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request following the module structure.

## License
MIT License.
