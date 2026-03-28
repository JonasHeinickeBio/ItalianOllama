# API Reference

The ItalianOllama API provides endpoints for language learning interactions.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (for development). Add authentication in production.

## Endpoints

### Health Check

**GET** `/health`

Check API and service status.

**Response:**
```json
{
  "status": "healthy",
  "llm_client": "connected",
  "memory": "connected"
}
```

---

### Chat

**POST** `/chat`

Chat with the language tutor.

**Request Body:**
```json
{
  "message": "Ciao, come stai?",
  "language": "italian",
  "level": "intermediate",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Ciao! Sto bene, grazie. E tu? (Hello! I'm fine, thanks. And you?)",
  "session_id": "abc-123",
  "vocabulary": [
    {"word": "ciao", "translation": "hello", "topic": "greetings"}
  ],
  "grammar_notes": null
}
```

---

### Vocabulary

**POST** `/vocabulary`

Add new vocabulary to the knowledge graph.

**Request Body:**
```json
{
  "word": "grazie",
  "translation": "thank you",
  "examples": ["Grazie mille!", "Grazie per il tuo aiuto."],
  "topic": "daily_conversation",
  "language": "italian"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added 'grazie' to vocabulary",
  "node_id": "5:abc123:456"
}
```

---

**GET** `/vocabulary/{language}`

Get vocabulary for a language.

**Query Parameters:**
- `topic` (optional) - Filter by topic

**Response:**
```json
{
  "vocabulary": [
    {
      "word": "ciao",
      "translation": "hello",
      "examples": ["Ciao, come stai?"],
      "topic": "greetings",
      "language": "italian"
    }
  ]
}
```

---

**GET** `/vocabulary/{language}/stats`

Get vocabulary statistics.

**Response:**
```json
{
  "total": 150,
  "by_topic": {
    "daily_conversation": 45,
    "food_and_dining": 30,
    "travel": 25,
    "healthcare": 20,
    "science": 30
  }
}
```

---

### Sessions

**GET** `/session/{session_id}`

Get session with message history.

**Response:**
```json
{
  "session_id": "abc-123",
  "user_id": "default",
  "language": "italian",
  "level": "intermediate",
  "message_count": 10,
  "created_at": "2024-01-15T10:30:00",
  "messages": [
    {"role": "user", "content": "Ciao!"},
    {"role": "assistant", "content": "Ciao! Come posso aiutarti?"}
  ]
}
```

---

### Topics

**GET** `/topics`

Get all available topics.

**Response:**
```json
{
  "topics": [
    {"name": "daily_conversation", "vocab_count": 45},
    {"name": "food_and_dining", "vocab_count": 30}
  ]
}
```

---

### LLM

**POST** `/llm/generate`

Direct LLM generation.

**Request Body:**
```json
{
  "prompt": "Translate to Italian: Hello, how are you?",
  "model": "alias-fast"
}
```

**Response:**
```json
{
  "response": "Ciao, come stai?"
}
```

---

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message description"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

## OpenAPI Schema

The full OpenAPI schema is available at:

```
http://localhost:8000/openapi.json
```

Interactive API docs (Swagger UI):

```
http://localhost:8000/docs
```
