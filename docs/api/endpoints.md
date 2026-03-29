# API Endpoints

ItalianOllama provides a RESTful API for both the chat interface and analytics dashboard.

## Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com/api
```

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/v1/chat/completions` | POST | OpenAI-compatible chat |
| `/chat` | POST | Simple chat |
| `/students` | POST | Create student |
| `/students/{id}` | GET | Get student |
| `/students/{id}/progress` | GET | Get progress |
| `/students/{id}/vocabulary` | GET | Get vocabulary |
| `/students/{id}/grammar` | GET | Get grammar errors |

## Authentication

### JWT Token

Most endpoints require a JWT token:

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/students/123
```

### Token Structure

```python
{
    "student_id": "uuid",
    "email": "user@example.com",
    "exp": 1234567890  # expiration
}
```

## API Endpoints

### GET /

Returns API information.

```bash
GET /
```

**Response:**
```json
{
  "name": "ItalianOllama API",
  "version": "1.0.0",
  "description": "AI-powered Italian language tutor"
}
```

### GET /health

Health check endpoint for monitoring.

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "neo4j": "connected",
  "litellm": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### POST /v1/chat/completions

OpenAI-compatible chat endpoint for streaming responses.

```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "tutor",
  "messages": [
    {"role": "system", "content": "You are Sofia, an Italian tutor..."},
    {"role": "user", "content": "Ciao! Voglio imparare l'italiano."}
  ],
  "stream": true
}
```

**Response (SSE):**
```
data: {"choices": [{"delta": {"content": "Ciao"}}]}
data: {"choices": [{"delta": {"content": "! Benvenuto"}}]}
data: {"choices": [{"delta": {"content": " nel corso!"}}]}
data: [DONE]
```

**Component Tokens:**
```
data: __COMPONENT__:drill_card|{"word": "ciao", "translation": "hello"}
data: [DONE]
```

### POST /chat

Simple chat endpoint.

```bash
POST /chat
Content-Type: application/json

{
  "student_id": "uuid",
  "message": "Fai vocab"
}
```

**Response:**
```json
{
  "response": "Ecco le tue flashcards per oggi!",
  "component": "drill_card",
  "data": {
    "cards": [
      {"word": "ciao", "translation": "hello"},
      {"word": "grazie", "translation": "thank you"}
    ]
  }
}
```

### POST /students

Create a new student.

```bash
POST /students
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john@example.com",
  "current_cefr": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /students/{id}

Get student profile.

```bash
GET /students/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "student_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john@example.com",
  "current_cefr": "B1",
  "total_sessions": 15,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /students/{id}/progress

Get student progress statistics.

```bash
GET /students/550e8400-e29b-41d4-a716-446655440000/progress
```

**Response:**
```json
{
  "cefr_level": "B1",
  "vocabulary_count": 150,
  "grammar_errors": 23,
  "exercises_completed": 45,
  "total_time_minutes": 120,
  "avg_score": 82,
  "current_streak": 5,
  "milestones": [
    {"name": "First Lesson", "achieved": true, "date": "2024-01-01"},
    {"name": "A2 Level", "achieved": true, "date": "2024-01-15"}
  ]
}
```

### GET /students/{id}/vocabulary

Get student vocabulary.

```bash
GET /students/550e8400-e29b-41d4-a716-446655440000/vocabulary
```

**Response:**
```json
{
  "vocabulary": [
    {
      "word": "ciao",
      "translation": "hello",
      "topic": "greetings",
      "confidence": 0.9,
      "last_practiced": "2024-01-01T00:00:00Z"
    }
  ],
  "due_for_review": [
    {"word": "arrivederci", "translation": "goodbye", "confidence": 0.4}
  ]
}
```

### GET /students/{id}/grammar

Get grammar errors.

```bash
GET /students/550e8400-e29b-41d4-a716-446655440000/grammar
```

**Response:**
```json
{
  "errors": [
    {
      "original": "Io sono andato",
      "corrected": "Io sono andata",
      "rule": "gender agreement",
      "seen_count": 3,
      "last_seen": "2024-01-01T00:00:00Z"
    }
  ],
  "patterns": [
    {"rule": "gender agreement", "count": 5},
    {"rule": "verb conjugation", "count": 3}
  ]
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid request body",
  "detail": "message is required"
}
```

### 401 Unauthorized

```json
{
  "error": "Invalid or expired token"
}
```

### 404 Not Found

```json
{
  "error": "Student not found",
  "student_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "detail": "Database connection failed"
}
```

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/v1/chat/completions` | 60/minute |
| `/chat` | 60/minute |
| `/students/*` | 100/minute |

## Client Examples

### Python

```python
import requests

# Chat request
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "student_id": "550e8400-...",
        "message": "Ciao!"
    }
)
print(response.json())
```

### JavaScript

```javascript
// Chat request
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    student_id: '550e8400-...',
    message: 'Ciao!'
  })
});
const data = await response.json();
```

### cURL

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"student_id": "550e8400-...", "message": "Ciao!"}'
```

## Related Documentation

- [Authentication](authentication.md)
- [Frontend Architecture](../architecture/frontend.md)
- [Troubleshooting](../troubleshooting/common-issues.md)
