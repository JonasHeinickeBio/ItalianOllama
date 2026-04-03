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
| **Onboarding Workflow** | ✅ 100% | **P2 COMPLETE**: Streamlit shell + onboarding with professional styling |
| **Dashboard Visuals** | ✅ 100% | **P2 COMPLETE**: 6 pages, Plotly charts, st-link-analysis, placement test |
| **Professional Styling** | ✅ 100% | **P2 COMPLETE**: Custom CSS themes, card-based layouts, responsive design, consistent theming |
| **Code Quality** | ✅ 100% | **P2 COMPLETE**: Fixed login syntax, updated documentation, added signup & placement test |

## Recent Improvements (April 2026)

### ✅ UI/UX Enhancement
- **Fixed syntax error** in `01_login.py:193` (missing indentation after signup button handler)
- **Updated documentation** in `DEVELOPMENT.md` to reflect all 7 Streamlit pages
- **Corrected project structure** to show `app_enhanced.py` as main entry point

### ✅ Professional Styling (P2 COMPLETE)
- **Custom CSS Themes**: Consistent color scheme (primary blue, secondary dark, accent orange, success green, error red)
- **Card-Based Layouts**: Professional hover effects, shadows, and transitions across all pages
- **Responsive Design**: Works well across different screen sizes and devices
- **Consistent Theming**: Unified styling across login, signup, dashboard, chat, vocabulary, settings, and placement test pages

### ✅ Page Documentation
All 7 Streamlit pages are now fully documented and functional:

1. **`01_login.py`** - Login page with professional header and error handling
2. **`01b_signup.py`** - Signup page for new student registration
3. **`02_dashboard.py`** - Main dashboard with learning metrics and analytics
4. **`03_chat.py`** - Chat with Sofia (Chainlit embedded or Streamlit fallback)
5. **`03_placement_test.py`** - Interactive CEFR A1-C1 placement test
6. **`04_vocabulary.py`** - Vocabulary management with spaced repetition (SM-2)
7. **`05_settings.py`** - User settings and profile management

### ✅ Code Quality
- **Simplified duplicate P1 phase** in DEVELOPMENT.md
- **Enhanced documentation** across all files
- **Cleaned up README.md** with correct `app_enhanced.py` reference

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
- [x] **Placement Test**: Interactive CEFR A1-C1 assessment with Neo4j persistence.
- [x] **JWT SSO**: Shared AUTH_SECRET between services.
- [x] **Professional Styling**: Custom CSS themes, card-based layouts, responsive design, consistent color scheme.
- [x] **UI Enhancement**: Fixed login page syntax, added signup page, documented all pages.

### 🟡 Phase P3 — Advanced Features (OPTIONAL)
- [ ] Redis for distributed rate limiting.
- [ ] OpenTelemetry distributed tracing.
- [ ] Real LLM streaming (not mocked).
- [ ] Circuit breaker for external services.
- [ ] Token usage quota tracking.
- [ ] Database connection pooling optimization.

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
