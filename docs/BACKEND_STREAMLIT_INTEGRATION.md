"""
IMPROVED FASTAPI BACKEND & STREAMLIT INTEGRATION
Version 0.3.0 - Semantic Learning Graph

Overview:
=========

This document describes the enhanced architecture that connects:
1. FastAPI Backend (Enhanced) with semantic endpoints
2. Enhanced Middleware (context injection, auth validation)
3. Streamlit Frontend with token-based auth
4. Neo4j Database with semantic learning graph

KEY IMPROVEMENTS
================

Backend (FastAPI)
-----------------
1. Uses Neo4jClientEnhanced instead of basic client
   - Semantic operations (sessions, attempts, vocabulary, skills)
   - Analytics endpoints (velocity, skill breakdown, errors)
   - Spaced repetition support (get_student_vocabulary with due_for_review)
   - Learning recommendations

2. New Endpoints (25+ total)
   - /sessions/* - Session lifecycle management
   - /attempts/* - Exercise attempt recording with metrics
   - /vocabulary/* - Vocabulary management + spaced rep
   - /analytics/* - Learning velocity, skills, errors
   - /recommendations/* - Personalized learning paths

3. Enhanced Error Handling & Standardized Responses
   - Validation error details
   - Trace IDs for debugging
   - Consistent error format across all endpoints

Middleware
----------
1. ContextMiddleware (NEW)
   - Injects request_id for tracing
   - Extracts student_id from JWT or URL
   - Adds context headers to responses

2. Improved LoggingMiddleware
   - Logs context (student_id, request_id)
   - Tracks performance per student

3. Enhanced RateLimitMiddleware
   - Per-endpoint limits (chat: 100/min, auth: 10/min)
   - Per-student limits (chat: 50/hour per student)
   - Configured via RateLimitConfig class

4. Metrics Collection
   - HTTP request metrics
   - LLM request metrics
   - Neo4j query metrics
   - Prometheus-ready

Streamlit Frontend
------------------
1. TutorAPIClient (NEW)
   - Wrapper for FastAPI endpoints
   - JWT token management (store in session_state)
   - Automatic retry on token expiration
   - Built-in error handling + user feedback
   - Method for each new endpoint

2. Enhanced Streamlit App (app_enhanced.py)
   - Token-based authentication
   - Cached API calls (via @st.cache_data)
   - Dashboard showing:
     * XP, streak, vocabulary count, sessions
     * Learning velocity metrics
     * Skill breakdown with progress bars
     * Common grammar errors
     * Personalized module recommendations
   - Chat interface with history
   - Vocabulary management:
     * View all vocabulary
     * Add new words
     * Spaced repetition queue
   - Settings & profile management

ARCHITECTURE DIAGRAM
====================

┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
├─────────────────────────────────────────────────────────────┤
│                  app_enhanced.py                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           TutorAPIClient (tutor_api.py)            │   │
│  │                                                     │   │
│  │  - JWT token management (session_state)            │   │
│  │  - HTTP client + error handling                    │   │
│  │  - Methods for all endpoints                       │   │
│  │  - Automatic caching via Streamlit                 │   │
│  └──────────────────┬──────────────────────────────────┘   │
│                    │                                       │
│  Dashboard │ Chat │ Vocabulary │ Settings                  │
│                    │                                       │
│           Render metrics and UI                           │
└────────────────────┼───────────────────────────────────────┘
                     │ HTTP + Bearer Token
                     │ (Authorization: Bearer <jwt>)
                     │
┌────────────────────▼───────────────────────────────────────┐
│                   FastAPI Backend                          │
├─────────────────────────────────────────────────────────────┤
│                 main_enhanced.py                           │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Middleware Stack (bottom to top)                  │  │
│  │  1. ContextMiddleware    [inject request_id, sid]  │  │
│  │  2. LoggingMiddleware    [log all requests]        │  │
│  │  3. CORSMiddleware       [allow Streamlit origin]  │  │
│  │  4. RateLimitMiddleware  [per-endpoint limits]     │  │
│  │  5. TimeoutMiddleware    [120s default]           │  │
│  │  6. MetricsMiddleware    [Prometheus metrics]      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Route Groups                                      │  │
│  │  - /auth/*             [JWT token management]      │  │
│  │  - /students/*         [student CRUD + stats]      │  │
│  │  - /sessions/*         [session lifecycle]         │  │
│  │  - /attempts/*         [exercise recording]        │  │
│  │  - /vocabulary/*       [vocab + spaced rep]        │  │
│  │  - /analytics/*        [velocity, skills, errors]  │  │
│  │  - /recommendations/*  [learning paths]            │  │
│  │  - /chat               [legacy endpoint]           │  │
│  └──────────────────┬────────────────────────────────┘  │
│                    │                                    │
└────────────────────┼────────────────────────────────────┘
                     │ Cypher Queries
                     │ (async driver)
                     │
┌────────────────────▼────────────────────────────────────┐
│              Neo4j Database (Enhanced)                 │
├──────────────────────────────────────────────────────────┤
│         neo4j_client_enhanced.py                        │
│                                                         │
│  - Student node + sessions/attempts/vocabulary        │
│  - Semantic relationships                             │
│  - Spaced repetition tracking (VocabConfidence)       │
│  - Performance metrics                                │
│  - Skill XP aggregation                               │
│  - Personalized recommendations queries              │
└──────────────────────────────────────────────────────────┘


WORKFLOW: STUDENT TAKES EXERCISE
=================================

1. Streamlit (Frontend)
   │
   ├─ User confirms exercise in chat or vocabulary UI
   │
   ├─ Call: api.start_session(student_id, topic, exercise_type)
   │    └─ POST /sessions → returns session_id
   │
   ├─ [User takes exercise, gets result]
   │
   └─ Call: api.record_attempt(
        session_id, student_id, exercise_id,
        exercise_type, correct, confidence,
        duration_seconds, hints_used, retries
      )
         └─ POST /attempts

2. FastAPI Backend
   │
   ├─ ContextMiddleware: Injects request_id + student_id from JWT
   │
   ├─ RateLimitMiddleware: Check per-student rate limit (/attempts: 50/hour)
   │
   ├─ Route Handler: record_attempt()
   │    │
   │    └─ client.record_exercise_attempt(
   │         - Creates Attempt node
   │         - Creates Performance node
   │         - Updates Student total_xp
   │         - Updates Session aggregate metrics
   │         - Tracks skill XP
   │         - Returns attempt_id
   │       )
   │
   ├─ Calculate XP reward (50 base + bonuses for confidence/hints)
   │
   └─ Return: {attempt_id, xp_earned, correct, streak_updated}

3. Streamlit (Frontend) cont'd
   │
   ├─ Display: "✅ Correct! +75 XP" or "❌ Incorrect. +10 XP"
   │
   ├─ Update: st.session_state.xp_total += xp_earned
   │
   └─ Cache invalidation: st.cache_data.clear() → refetch stats

4. Neo4j (Database)
   │
   └─ Persisted graph:
      Student(total_xp += 75)
        ├─ Session(xp_total=500)
        │  └─ Attempt(exercise_id, correct, confidence, duration, ...)
        │     └─ Performance(skill_breakdown, engagement, learning_gain)
        └─ Experience(skill=vocabulary, xp=30)


WORKFLOW: STREAMLIT DASHBOARD
=============================

1. User navigates to Dashboard
   │
   ├─ Call: get_profile() [cached 60s]
   │    └─ api.get_student(student_id)
   │       └─ GET /students/{student_id}
   │
   ├─ Call: get_velocity() [cached 300s]
   │    └─ api.get_learning_velocity(student_id, days=7)
   │       └─ GET /analytics/velocity/{student_id}?days=7
   │
   ├─ Call: get_skills() [cached 300s]
   │    └─ api.get_skills(student_id)
   │       └─ GET /analytics/skills/{student_id}
   │
   ├─ Call: get_errors() [cached 300s]
   │    └─ api.get_common_errors(student_id, limit=5)
   │       └─ GET /analytics/errors/{student_id}?limit=5
   │
   └─ Call: get_next_module() [cached 600s]
        └─ api.get_next_module(student_id)
           └─ GET /recommendations/next-module/{student_id}

2. FastAPI routes use enhanced Neo4j client:
   │
   ├─ get_learning_velocity(student_id, days=7)
   │    └─ Query: Sessions within last N days, sum XP/time
   │
   ├─ get_skill_breakdown(student_id)
   │    └─ Query: Experience nodes grouped by skill, total XP per skill
   │
   ├─ get_common_errors(student_id, limit=10)
   │    └─ Query: GrammarError nodes, frequency count, top N concepts
   │
   └─ get_recommended_next_module(student_id)
        └─ Query: User's highest CEFR level, query next difficulty module
                  that teaches skills with XP < threshold

3. Streamlit renders:
   │
   ├─ Metric cards: XP, Streak, Vocabulary count, Sessions
   │
   ├─ Learning velocity: XP/day, sessions/week, avg duration
   │
   ├─ Skill progress bars (top 5 skills with XP)
   │
   ├─ Common errors (top 3 misconceptions)
   │
   └─ Recommended module with reason


VOCABULARY SPACED REPETITION FLOW
==================================

1. Streamlit: Get due for review
   │
   └─ Call: api.get_vocabulary(student_id, due_for_review=True)
      └─ GET /vocabulary/{student_id}?due_for_review=true

2. FastAPI: Query vocabulary due for review
   │
   └─ Route: get_vocabulary(student_id, due_for_review=True)
      └─ client.get_student_vocabulary(student_id, only_due_for_review=True)

3. Neo4j client: Get vocabulary with SM-2 filtering
   │
   └─ Query VocabConfidence nodes where:
      - next_review <= current_timestamp AND
      - confidence_level < 0.95 (not mastered)

   Returns sorted by: next_review (oldest first)

4. Student reviews word (e.g., "Cane" = "Dog")
   │
   ├─ Rate confidence: 1-5 scale
   │
   └─ Call: api.update_vocabulary_confidence(vocab_id, confidence)
      └─ POST /vocabulary/{vocabulary_id}/confidence?confidence=4

5. FastAPI: Update spaced rep metrics
   │
   └─ Route: update_vocabulary_confidence(vocab_id, confidence)
      └─ client.update_vocabulary_confidence(vocab_id, confidence)

6. Neo4j client: Apply SM-2 algorithm
   │
   └─ VocabConfidence:
      OLD:
        - confidence_level: 0.3
        - ease_factor: 2.5
        - interval: 1 day
        - next_review: 2024-04-02

      NEW (confidence=4, quality=0.8):
        - confidence_level: 0.5
        - ease_factor: 2.36  [simplified SM-2]
        - interval: 3 days   [1 * 2.36]
        - next_review: 2024-04-05 [now + interval]

7. Streamlit: Show success
   │
   └─ Display: "✅ Aggiornato!" + next_review date


AUTHENTICATION FLOW
===================

1. Login (Streamlit)
   │
   ├─ User enters student_id
   │
   ├─ Call: api.login(student_id)
   │    └─ POST /auth/token
   │       {student_id, expires_in_hours=4}

2. FastAPI: Issue JWT
   │
   ├─ Route: get_token(request)
   │    └─ create_access_token(student_id, expires_delta)
   │
   ├─ JWT Payload:
   │    {
   │      "sub": "mario.rossi@example.com",
   │      "exp": 1711979264,  [now + 4 hours]
   │      "iat": 1711965864
   │    }
   │
   └─ Signed with: settings.auth_secret (stored in .env)

3. Streamlit: Store Token
   │
   └─ st.session_state._api_token = token
      st.session_state._api_token_expires = datetime (4h from now)

4. Subsequent API Calls
   │
   └─ All requests include:
      Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

5. FastAPI: Validate Token
   │
   ├─ ContextMiddleware:
   │    └─ Extract student_id from JWT payload
   │       request.state.student_id = payload.get("sub")
   │
   └─ Route handlers:
      └─ Use request.state.student_id for all operations

6. Token Expiration (Streamlit)
   │
   └─ TutorAPIClient.is_token_valid() checks:
      - Token exists
      - Current time < expiration time
      - If expired: api.clear_token() + show st.warning("Session expired")

7. Re-auth (Streamlit)
   │
   └─ User clicks "Rinnova Token" button
      └─ api.login(student_id) again
         └─ New token issued


MIGRATION FROM OLD TO NEW
=========================

Option 1: Parallel Deployment
   │
   ├─ Keep old main.py running on port 8000
   ├─ Deploy new main_enhanced.py on port 8001
   ├─ Streamlit config points to 8001
   └─ Gradually migrate traffic

Option 2: Gradual Integration
   │
   ├─ Import Neo4jClientEnhanced alongside old client
   ├─ Update one endpoint at a time
   ├─ Use feature flags to switch between old/new
   └─ Run both models in parallel during transition

Option 3: Feature Flags
   │
   ├─ Add settings.use_enhanced_client = true/false
   ├─ Route handlers check flag
   ├─ If true: use neo4j_client_enhanced
   │  If false: use neo4j_client
   └─ Gradually enable per-route


CONFIGURATION & DEPLOYMENT
===========================

.env Variables (Required)
-----------
NEO4J_URI=neo4j+s://instance-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<encrypted>
NEO4J_DATABASE=neo4j  [or instance-id for Aura]

LITELLM_BASE_URL=http://litellm:4000
LITELLM_API_KEY=sk-...

AUTH_SECRET=<generated via: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=4

CORS_ORIGINS=http://localhost:8501,http://localhost:8000
BACKEND_URL=http://localhost:8000

SENTRY_DSN=https://...  [optional]

Docker Compose + Middleware
----
services:
  fastapi:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      NEO4J_URI: bolt://neo4j:7687
      ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  neo4j:
    image: neo4j:5-enterprise
    ports:
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: "[\\"apoc\\"]"

  streamlit:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      BACKEND_URL: http://fastapi:8000

Rate Limits (Configurable)
---------------
Endpoint Limits:
  /v1/chat/completions - 100 req/min
  /auth/token - 10 req/min
  /students - 50 req/min

Per-Student Limits:
  /chat - 50 req/hour per student
  /attempts - 50 req/hour per student


MONITORING & DEBUGGING
======================

Logs
----
All requests logged with format:
  REQUEST | POST /attempts | request_id=abc123 | student_id=mario
  RESPONSE | POST /attempts | status=201 | duration=45ms

Context Injection
-----------------
Every request has:
  request.state.request_id - for tracing
  request.state.student_id - for user-scoped queries
  Headers: X-Request-ID, X-Student-ID

Metrics (Prometheus)
---------------------
HTTP metrics:
  - http_request_count by path, method, status
  - http_request_duration by path (p50, p95, p99)
  - http_error_count by path, error_type

Neo4j metrics:
  - neo4j_query_count by query_type
  - neo4j_query_duration

LLM metrics:
  - llm_request_count
  - llm_request_duration

Error Tracking (Sentry - Optional)
-----------------------------------
All exceptions tagged with:
  - student_id
  - request_id
  - endpoint
  - error_type


TESTING THE NEW BACKEND
======================

1. Test Health Check
   curl http://localhost:8000/health

2. Test Authentication
   curl -X POST http://localhost:8000/auth/token \
     -H "Content-Type: application/json" \
     -d '{"student_id": "test_user", "expires_in_hours": 4}'

3. Test Student Creation
   curl -X POST http://localhost:8000/students \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"student_id": "mario", "name": "Mario Rossi"}'

4. Test Session + Attempt Flow
   # Create session
   SESSION=$(curl -X POST http://localhost:8000/sessions \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"student_id": "mario", "topic": "greetings"}' | jq '.session_id')

   # Record attempt
   curl -X POST http://localhost:8000/attempts \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "'$SESSION'",
       "student_id": "mario",
       "exercise_template_id": "ex_1",
       "exercise_type": "flashcard",
       "correct": true,
       "confidence": 4,
       "duration_seconds": 15
     }'

5. Test Analytics
   curl http://localhost:8000/analytics/velocity/mario \
     -H "Authorization: Bearer <token>"

6. Test Vocabulary Spaced Rep
   # Get due vocabulary
   curl "http://localhost:8000/vocabulary/mario?due_for_review=true" \
     -H "Authorization: Bearer <token>"


NEXT STEPS
==========

1. Deploy main_enhanced.py as FastAPI backend
2. Deploy app_enhanced.py as Streamlit frontend
3. Load demo data (demo_student_complete_setup.cypher) into Neo4j
4. Test all endpoints per Testing section above
5. Monitor logs and metrics
6. Gradually migrate traffic from old routes
7. Enable Sentry for error tracking (optional)
8. Set up Prometheus for metrics collection (optional)


SUMMARY
=======

This enhanced architecture provides:

✅ Semantic learning graph backed by Neo4j
✅ Rich API endpoints for all learning operations
✅ Token-based authentication via JWT
✅ Context injection for request tracing
✅ Rate limiting per endpoint and per student
✅ Comprehensive metrics & monitoring
✅ Token management in Streamlit
✅ Cached API calls for performance
✅ Spaced repetition for vocabulary
✅ Personalized learning recommendations
✅ Learning velocity analytics
✅ Skill breakdown & tracking
✅ Grammar error detection

The entire system is designed for production deployment with:
- Resilience (error handling, retries)
- Security (JWT auth, rate limits)
- Observability (logging, metrics, context)
- Performance (caching, async operations)
- Scalability (per-student rate limits, async driver)
"""
