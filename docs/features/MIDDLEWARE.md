# ItalianOllama Middleware Documentation

## Overview

This document describes the middleware system in the ItalianOllama API and how it integrates with the frontend (Streamlit + Chainlit).

## Middleware Stack

The API uses a layered middleware approach (bottom to top):

```
1. LoggingMiddleware      - Request/response logging with timing
2. ContextMiddleware      - Inject request_id, student_id, session_id
3. CORSMiddleware         - Handle Cross-Origin requests
4. RateLimitMiddleware    - Per-endpoint and per-student rate limits
5. TimeoutMiddleware      - Request timeout enforcement
6. MetricsMiddleware      - Prometheus metrics collection
```

## Middleware Components

### 1. ContextMiddleware (`src/italianollama/api/middleware/context.py`)

Injects request-scoped context into every request:

- **request_id**: Unique identifier for tracing (from X-Request-ID header or generated)
- **student_id**: Extracted from JWT token or URL path
- **session_id**: From cookie or generated new (persists 15 days)

Response headers:
- `X-Request-ID`: The request identifier
- `X-Student-ID`: The authenticated student (if applicable)
- `X-Session-ID`: The session identifier

### 2. Auth Middleware (`src/italianollama/api/middleware/auth.py`)

JWT token management:

- `create_access_token(subject, expires_delta)`: Create JWT token
- `verify_access_token(token)`: Verify and decode JWT token
- `get_current_student(request, credentials)`: FastAPI dependency for protected routes

### 3. RateLimitMiddleware (`src/italianollama/api/middleware/rate_limit.py`)

Implements sliding window rate limiting:

- **Global limits**: Per-endpoint (e.g., `/chat`: 100 req/min)
- **Per-student limits**: Per-user protection (e.g., `/chat`: 50 req/hour)

Response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Window`: Time window in seconds

### 4. TimeoutMiddleware (`src/italianollama/api/middleware/timeout.py`)

Enforces per-endpoint timeouts:

- `/chat`: 300 seconds (5 minutes)
- `/auth/token`: 10 seconds
- Default: 30 seconds

### 5. MetricsMiddleware (`src/italianollama/api/middleware/metrics.py`)

Prometheus metrics at `/metrics` endpoint:

- HTTP request counts and durations
- LLM request metrics
- Neo4j query metrics
- Active connections

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/token` | POST | Get JWT token for student |
| `/auth/verify` | POST | Verify token validity |
| `/auth/refresh` | POST | Refresh expiring token |

### Protected Routes

All these routes require valid JWT token:

- `GET /students/{student_id}` - Get student profile
- `GET /api/student/{student_id}/stats` - Get dashboard stats
- `GET /api/student/{student_id}/vocabulary` - Get vocabulary
- `GET /api/student/{student_id}/grammar-errors` - Get common errors
- `GET /api/student/{student_id}/graph` - Get knowledge graph
- `GET /api/student/{student_id}/test-readiness` - Get test readiness
- `GET /analytics/velocity/{student_id}` - Get learning velocity
- `GET /analytics/skills/{student_id}` - Get skill breakdown
- `GET /analytics/errors/{student_id}` - Get common errors
- `GET /recommendations/next-module/{student_id}` - Get next module

## Streamlit + Chainlit Integration

### Session Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT APP                            │
│  1. User logs in via /pages/01_login.py                    │
│  2. API calls /auth/token to get JWT                       │
│  3. Token saved to:                                         │
│     - st.session_state._api_token (memory)                 │
│     - Browser cookies (persists on reload)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ User navigates to Chat page
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              /pages/03_chat.py                              │
│  - Embeds Chainlit iframe                                   │
│  - Passes via URL query params:                             │
│     ?student_id=...&token=...&session_id=...               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              CHAINLIT (Embedded)                            │
│  - Reads token from query params                            │
│  - Uses token for all API calls                             │
│  - No separate login needed                                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

1. **Shared Authentication**: JWT token passed from Streamlit to Chainlit
2. **Session Continuity**: Same session_id across Streamlit and Chainlit
3. **Cookie Persistence**: Tokens survive page reloads
4. **Auto Token Refresh**: Chainlit refreshes token when expiring

### Frontend Files

| File | Purpose |
|------|---------|
| `streamlit/pages/01_login.py` | Login + get JWT token |
| `streamlit/pages/03_chat.py` | Embed Chainlit with token |
| `streamlit/auth/session.py` | Session management |
| `streamlit/auth/browser_storage.py` | Cookie persistence |
| `frontend/chainlit_app.py` | Chainlit chat app |

## Error Handling

### HTTP Status Codes

| Code | Meaning | Frontend Action |
|------|---------|-----------------|
| 200 | Success | Process response |
| 400 | Bad Request | Show error message |
| 401 | Unauthorized | Refresh token or re-login |
| 408 | Timeout | Retry request |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Show error message |

### Rate Limit Handling

When receiving 429:

```python
retry_after = int(response.headers.get("X-RateLimit-Window", "60"))
# Wait and retry
await asyncio.sleep(retry_after)
```

### Token Expiration

When receiving 401:

```python
# Try to refresh token
response = await client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
if response.status_code == 200:
    new_token = response.json()["access_token"]
    # Retry original request with new token
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | http://localhost:8000 | API base URL |
| `JWT_SECRET` | (required) | Secret for JWT signing |
| `JWT_ALGORITHM` | HS256 | JWT algorithm |
| `JWT_EXPIRATION_HOURS` | 4 | Token validity |

### Rate Limit Config

Edit `RateLimitConfig` in `src/italianollama/api/middleware/rate_limit.py`:

```python
ENDPOINT_LIMITS = {
    "/chat": (100, 60),      # 100 requests per minute
    "/auth/token": (10, 60), # 10 requests per minute
}

PER_STUDENT_LIMITS = {
    "/chat": (50, 3600),     # 50 requests per hour per student
}
```

### Timeout Config

Edit `TimeoutConfig` in `src/italianollama/api/middleware/timeout.py`:

```python
ENDPOINT_TIMEOUTS = {
    "/chat": 300,            # 5 minutes for chat
    "/auth/token": 10,       # 10 seconds for auth
}
```

## Development

### Running the Services

```bash
# Terminal 1: Start FastAPI backend
cd /home/jhe24/ItalianOllama
python -m uvicorn italianollama.api.main:app --reload --port 8000

# Terminal 2: Start Streamlit
cd /home/jhe24/ItalianOllama
streamlit run src/italianollama/frontend/streamlit/app_enhanced.py

# Terminal 3: Start Chainlit (optional, embedded mode)
cd /home/jhe24/ItalianOllama
chainlit run src/italianollama/frontend/chainlit_app.py --port 8001
```

### Testing Middleware

```bash
# Test auth token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"student_id": "testuser"}'

# Test protected route
curl http://localhost:8000/students/testuser \
  -H "Authorization: Bearer <token>"

# Check metrics
curl http://localhost:8000/metrics

# Check health
curl http://localhost:8000/health
```

## Troubleshooting

### "Missing authorization credentials"

- Ensure JWT token is passed in Authorization header
- Token may be expired - try `/auth/refresh`

### "Rate limit exceeded"

- Wait for the retry_after duration
- Check X-RateLimit headers for limits

### "Access denied to this student's data"

- Token student_id doesn't match URL student_id
- User can only access their own data

### Chainlit not loading in Streamlit

- Check Chainlit service is running
- Verify CHAINLIT_URL environment variable
- Check browser console for iframe errors

### Session not persisting

- Ensure streamlit-cookies-manager is installed
- Check browser allows cookies
- Verify cookies are being set in browser dev tools
