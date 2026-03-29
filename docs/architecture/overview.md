# Architecture Overview

ItalianOllama is an AI-powered Italian language learning application with a dual-frontend architecture.

## High-Level Architecture

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
    │ Workflow   │ (Blablador) │   │(Memory) │
    └────────┘    └────────────┘   └─────────┘
```

## Core Components

### Frontend Layer

| Component | Technology | Port | Purpose |
|-----------|------------|------|---------|
| **Chainlit** | Python/Chainlit | 8000 | Real-time tutor chat |
| **Streamlit** | Python/Streamlit | 8501 | Analytics dashboard |
| **Nginx** | Reverse Proxy | 80/443 | Routing & WebSocket |

### Backend Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| **FastAPI** | Python/FastAPI | REST API & orchestration |
| **LangGraph** | Python/LangGraph | Workflow state machine |
| **LiteLLM** | Python/LiteLLM | Unified LLM interface |

### Data Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Neo4j** | Graph Database | Student profiles, progress, vocabulary |
| **Aura** | Neo4j Cloud | Production database (optional) |

## Technology Stack

### Programming Languages

- **Python 3.10+** - All backend and frontend code
- **SQL** - Neo4j Cypher queries
- **Nginx Conf** - Reverse proxy configuration

### Key Libraries

| Library | Purpose |
|---------|---------|
| **LangGraph** | Graph-based agent orchestration |
| **FastAPI** | Async web framework |
| **Chainlit** | Chat UI with streaming & components |
| **Streamlit** | Analytics dashboard |
| **LiteLLM** | Unified LLM interface |
| **Neo4j** | Graph database driver |
| **Pydantic** | Data validation |

## Data Flow

### Chat Flow

```
User Input → Chainlit → FastAPI /v1/chat/completions
    ↓
LangGraph Router Node
    ↓
    ├─→ Placement Node (CEFR test)
    ├─→ Vocabulary Node (flashcards)
    ├─→ Grammar Node (drills)
    ├─→ Translation Node
    ├─→ Free Writing Node
    └─→ Niveau Test Node (exam prep)
    ↓
LLM (via LiteLLM)
    ↓
Response + Component Tokens
    ↓
Chainlit UI → User
    ↓
Neo4j (save progress)
```

### Dashboard Flow

```
User Access → Streamlit Dashboard
    ↓
Check Authentication (JWT)
    ↓
Fetch Data from API
    ↓
Neo4j Queries
    ↓
Render Analytics Pages
```

## Design Principles

1. **Dual-Frontend** - Separate chat (learning) and dashboard (analytics)
2. **Graph-Based State** - LangGraph for predictable workflow orchestration
3. **Unified LLM Interface** - LiteLLM for provider flexibility
4. **Persistent Memory** - Neo4j for student progress tracking
5. **Production-Ready** - Docker, Nginx, WebSocket support

## Security

- **JWT Authentication** - Token-based session management
- **OAuth2 (Google)** - Optional social login
- **Non-root Containers** - Docker security best practices
- **Environment Variables** - No hardcoded secrets

## Scalability

The architecture supports:
- Horizontal scaling of frontend services
- Cloud deployment with Neo4j Aura
- Multiple LLM providers via LiteLLM
- WebSocket for real-time chat

## Related Documentation

- [Frontend Architecture](frontend.md)
- [Backend Architecture](backend.md)
- [Database Schema](database.md)
- [LLM Providers](llm-providers.md)
