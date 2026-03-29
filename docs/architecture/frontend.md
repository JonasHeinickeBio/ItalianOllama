# Frontend Architecture

ItalianOllama uses a dual-frontend approach with Chainlit for the chat interface and Streamlit for the analytics dashboard.

## Dual-Frontend Concept

| Frontend | Tool | Purpose | User Flow |
|----------|------|---------|-----------|
| **Chat** | Chainlit | Learning conversations | Primary interaction |
| **Dashboard** | Streamlit | Progress analytics | Secondary insight |

Both frontends share the same FastAPI backend but provide different user experiences optimized for their specific tasks.

## Chainlit (Chat Interface)

### Overview

Chainlit provides the main learning interface where students interact with Sofia, the Italian tutor.

**Location:** `frontend/chainlit/`

### Key Features

- **Real-time Streaming** - SSE-based response streaming
- **Interactive Components** - Flashcards, quizzes, writing reviews
- **OAuth2 Authentication** - Google login integration
- **Session Management** - Student profile on startup

### File Structure

```
frontend/chainlit/
├── chainlit_app.py           # Main application entry
├── config.py                 # Pydantic settings
├── requirements.txt          # Dependencies
├── Dockerfile                # Container image
├── .chainlit/
│   └── config.toml           # Chainlit configuration
├── api/
│   └── client.py             # FastAPI client + SSE parser
├── auth/
│   └── oauth.py              # Google OAuth2 + JWT
└── components/
    ├── __init__.py           # Component registry
    ├── base.py               # BaseComponent abstract class
    ├── drill_card.py         # Flashcard component
    ├── grammar_feedback.py   # Grammar correction
    ├── score_badge.py        # Results display
    ├── placement_quiz.py     # MCQ component
    └── writing_review.py     # Writing feedback
```

### Component System

The component system allows interactive UI elements in chat:

```python
COMPONENT_REGISTRY = {
    "drill": DrillCard,
    "grammar": GrammarFeedback,
    "score": ScoreBadge,
    "quiz": PlacementQuiz,
    "review": WritingReview,
}
```

**SSE Token Format:**
```
data: {"choices": [{"delta": {"content": "Hello"}}]}
data: __COMPONENT__:drill_card|{"word": "ciao", "translation": "hello"}
data: [DONE]
```

### Authentication Flow

```
User → Chainlit OAuth → Google → Callback → JWT → Session
                                                        ↓
                                              Dashboard Link (with JWT)
```

## Streamlit (Dashboard)

### Overview

Streamlit provides the analytics dashboard for tracking learning progress.

**Location:** `frontend/streamlit/`

### Key Features

- **Multi-Page App** - 5 analytics pages
- **JWT Authentication** - Session from Chainlit link
- **Visual Analytics** - Charts, tables, KPIs
- **Real-time Data** - Cached Neo4j queries

### File Structure

```
frontend/streamlit/
├── app.py                    # Main entry + sidebar
├── config.py                 # Pydantic settings
├── requirements.txt          # Dependencies
├── Dockerfile                # Container image
├── auth/
│   └── session.py            # JWT → session → email
├── api/
│   └── client.py             # Typed API client + caching
├── components/
│   ├── kpi_row.py            # KPI cards
│   ├── confidence_table.py   # Sortable results
│   └── radar_chart.py        # Skill radar
└── pages/
    ├── 1_progress.py         # CEFR level & milestones
    ├── 2_vocabulary.py       # Vocab insights
    ├── 3_grammar.py          # Grammar patterns
    ├── 4_knowledge_graph.py  # Neo4j visualization
    └── 5_test_readiness.py   # Exam scores
```

### Dashboard Pages

| Page | Description |
|------|-------------|
| **Progress** | CEFR level, total vocab, milestones |
| **Vocabulary** | Confidence breakdown, spaced reps |
| **Grammar** | Error patterns, rule violations |
| **Knowledge Graph** | Neo4j visualization |
| **Test Readiness** | Exam simulation scores |

### Authentication Flow

```
User clicks dashboard link → Extract JWT → Validate → Session → Access
```

3-Layer Auth:
1. **JWT Validation** - Verify token signature & expiration
2. **Session Cache** - Store validated session
3. **Email Gate** - Check student email exists

## Nginx Reverse Proxy

### Overview

Nginx provides the single entry point for all services.

**Location:** `frontend/nginx.conf`

### Routes

| Path | Service | Features |
|------|---------|----------|
| `/chat/` | Chainlit:8000 | WebSocket, 300s timeout |
| `/dashboard/` | Streamlit:8501 | X-Script-Name |
| `/api/` | FastAPI:8000 | REST API |
| `/health` | Aggregated | Health checks |

### WebSocket Support

```nginx
location /chat/ {
    proxy_pass http://chainlit:8000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Shared Authentication

### JWT SSO

Both frontends share authentication via JWT:

```python
# Chainlit: Create token
token = jwt.encode(
    {"student_id": student_id, "exp": expiry},
    AUTH_SECRET,
    algorithm="HS256"
)

# Streamlit: Validate token
payload = jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
```

### AUTH_SECRET

Generate a secure secret:
```bash
AUTH_SECRET=$(openssl rand -hex 32)
```

## Development vs Production

### Development (Direct Access)

```
http://localhost:8000  # Chainlit
http://localhost:8501  # Streamlit
http://localhost:8000/docs  # API
```

### Production (Nginx)

```
http://localhost/chat/      # Chainlit
http://localhost/dashboard/ # Streamlit
http://localhost/api/       # API
```

## Related Documentation

- [Chat Interface Features](../features/chat-interface.md)
- [Dashboard Features](../features/dashboard.md)
- [API Authentication](../api/authentication.md)
- [Nginx Configuration](../deployment/nginx.md)
