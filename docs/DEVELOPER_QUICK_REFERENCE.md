# Flashcard Review & Session Tracking - Developer Quick Reference

## Quick Start

### 1. Run Flashcard Review Session

```python
# In vocabulary page (04_vocabulary.py)

# Get vocabulary for review
due_vocab = get_vocabulary_items(due_for_review=True, level_filter="B1")

# Run flashcard review
results = run_flashcard_review(due_vocab, num_cards=10)

# Results include:
# - total: 10
# - correct: 9
# - incorrect: 1
# - accuracy: 90.0
# - session_details: {words_reviewed, correct_answers, accuracy}
```

### 2. Track Session

```python
# Session tracking is automatic in run_flashcard_review()
# Or manually:

session_details = {
    "duration": 900,  # seconds
    "words_reviewed": 10,
    "correct_answers": 9,
    "accuracy": 90.0,
}

track_session("flashcard_review", session_details)
```

### 3. Access Session History

```python
# From TutorAPIClient
history = api.get_session_history(student_id, limit=10)

# Or from session state
for session in st.session_state.session_history:
    print(f"{session['session_type']}: {session['accuracy']}%")
```

## Key Functions

### Frontend (`04_vocabulary.py`)

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_vocabulary_items()` | Fetch vocabulary with filtering | `list[dict]` |
| `run_flashcard_review()` | Run review session | `dict` with results |
| `track_session()` | Track session in Neo4j | `None` |
| `get_cefr_levels()` | Get available CEFR levels | `list[str]` |

### API Client (`tutor_api.py`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `create_session()` | POST /session/{id} | Create new session |
| `update_session()` | PUT /session/{id} | Update session metrics |
| `get_session_history()` | GET /session/history/{id} | Get session history |

### Neo4j Manager (`learning.py`)

| Method | Purpose |
|--------|---------|
| `create_session()` | Create Session node in Neo4j |
| `update_session()` | Update session metrics |
| `get_session_history()` | Query session history |

## Data Models

### Session Node

```python
{
    "session_type": "flashcard_review",
    "started_at": "2024-01-15T10:30:00",
    "completed_at": "2024-01-15T10:45:00",
    "words_reviewed": 10,
    "correct_answers": 9,
    "accuracy": 90.0,
    "duration_seconds": 900,
    "details": {...}
}
```

### Confidence Scoring

- **❌ Not at all** → 0% accuracy contribution
- **🤔 Somewhat** → 50% accuracy contribution
- **✅ Confident** → 100% accuracy contribution

## Architecture

```
Frontend (Streamlit)
    ↓ track_session()
API Client (TutorAPIClient)
    ↓ HTTP POST/PUT/GET
Backend (FastAPI)
    ↓ Cypher Queries
Neo4j Database
```

## Common Tasks

### Add New Session Type

```python
# 1. Define session type
SESSION_TYPES = ["flashcard_review", "custom_session", ...]

# 2. Track session
track_session("custom_session", {
    "words_reviewed": 5,
    "accuracy": 80.0,
})
```

### Filter Vocabulary by Level

```python
vocabulary = get_vocabulary_items(
    due_for_review=False,
    level_filter="B1"  # or "A1", "A2", "B2", "C1", "C2"
)
```

### Get Session Statistics

```python
if "session_history" in st.session_state:
    total_sessions = len(st.session_state.session_history)
    avg_accuracy = sum(s.get('accuracy', 0) for s in st.session_state.session_history) / total_sessions
```

## Session Tracking Flow

```
User starts flashcard review
    ↓
random.sample(vocabulary, num_cards)
    ↓
Display cards, collect confidence ratings
    ↓
Calculate accuracy
    ↓
track_session("flashcard_review", details)
    ↓
api.create_session(student_id, session_type, details)
    ↓
POST /session/{student_id}
    ↓
LearningManager.create_session()
    ↓
Neo4j: CREATE (sess:Session) + MERGE (s)-[:COMPLETED_SESSION]->(sess)
    ↓
Return session_id
    ↓
Store in st.session_state
```

## Neo4j Queries

### Create Session
```python
query = """
MERGE (s:Student {student_id: $student_id})
CREATE (sess:Session {
    session_type: $session_type,
    started_at: datetime(),
    details: $details,
    completed_at: datetime()
})
MERGE (s)-[:COMPLETED_SESSION]->(sess)
RETURN elementId(sess) AS session_id
"""
```

### Get Session History
```python
query = """
MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
RETURN {
    session_type: sess.session_type,
    started_at: sess.started_at,
    completed_at: sess.completed_at,
    words_reviewed: COALESCE(sess.words_reviewed, 0),
    correct_answers: COALESCE(sess.correct_answers, 0),
    accuracy: COALESCE(sess.accuracy, 0.0),
    duration_seconds: COALESCE(sess.duration_seconds, 0)
} AS session
ORDER BY sess.started_at DESC
LIMIT $limit
"""
```

## Error Handling

```python
try:
    result = api.create_session(student_id, session_type, details)
    if result:
        # Success
    else:
        # Fallback to session state
except Exception as e:
    logger.warning(f"Session tracking failed: {e}")
```

## Best Practices

1. **Always use try-except** for session tracking
2. **Validate accuracy** is between 0-100
3. **Use lowercase session types** with underscores
4. **Cache vocabulary** with `@st.cache_data`
5. **Update session history** after each review

## Testing

### Test Flashcard Review
```bash
poetry run pytest tests/unit/frontend/test_vocabulary.py::test_flashcard_review
```

### Test Session Tracking
```bash
poetry run pytest tests/integration/memory/test_session_tracking.py
```

## API Reference

### TutorAPIClient Methods

```python
# Create session
api.create_session(student_id, session_type, details=None)
# Returns: dict with session_id or None

# Update session
api.update_session(session_id, words_reviewed=0, correct_answers=0, 
                   accuracy=0.0, duration_seconds=0)
# Returns: dict or None

# Get history
api.get_session_history(student_id, limit=10)
# Returns: list[dict] or None
```

### LearningManager Methods

```python
# Create session
await client.create_session(student_id, session_type, details=None)
# Returns: str (session_id)

# Update session
await client.update_session(session_id, words_reviewed=0, correct_answers=0,
                            accuracy=0.0, duration_seconds=0)
# Returns: bool (success)

# Get history
await client.get_session_history(student_id, limit=10)
# Returns: list[dict]
```

## Related Documentation

- [Flashcard Review](features/flashcard-review.md) - Complete feature guide
- [Session Tracking](features/session-tracking.md) - Technical documentation
- [Progress Tracking](features/progress-tracking.md) - Analytics overview
- [Implementation Summary](../IMPLEMENTATION_SUMMARY.md) - System overview
