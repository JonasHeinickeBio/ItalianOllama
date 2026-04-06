# Session Tracking System

Comprehensive guide to the Neo4j-based session tracking system for monitoring student learning progress.

## Overview

The session tracking system records and analyzes student learning sessions with full integration to Neo4j graph database. Each session captures detailed metrics about vocabulary review, exercises, and practice activities.

### Key Features

- **Complete Session History** - Track all learning activities
- **Real-time Metrics** - Accuracy, words reviewed, duration
- **Analytics Dashboard** - Progress visualization
- **Spaced Repetition Integration** - Review scheduling
- **CEFR Level Correlation** - Progress by proficiency level

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Student Frontend                         │
│  (Streamlit Pages: vocabulary.py, dashboard.py)            │
└─────────────────────────────────────────┬───────────────────┘
                                          │
                                          │ track_session()
                                          │
┌─────────────────────────────────────────▼───────────────────┐
│                  TutorAPIClient                             │
│  - create_session()                                         │
│  - update_session()                                         │
│  - get_session_history()                                    │
└─────────────────────────────────────────┬───────────────────┘
                                          │
                                          │ HTTP Request
                                          │ POST/PUT/GET /session/*
                                          │
┌─────────────────────────────────────────▼───────────────────┐
│                  FastAPI Backend                            │
│  - /session/{student_id} (POST)                             │
│  - /session/{session_id} (PUT)                              │
│  - /session/history/{student_id} (GET)                      │
└─────────────────────────────────────────┬───────────────────┘
                                          │
                                          │ Cypher Queries
                                          │
┌─────────────────────────────────────────▼───────────────────┐
│                  Neo4j Graph Database                       │
│  (:Student)-[:COMPLETED_SESSION]->(:Session)               │
│  - Session nodes with metrics                               │
│  - Relationships to Student nodes                           │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User starts flashcard review
   ↓
2. run_flashcard_review() collects results
   ↓
3. track_session() called with session_type and details
   ↓
4. TutorAPIClient.create_session() POST to /session/{student_id}
   ↓
5. FastAPI creates Session node in Neo4j
   ↓
6. Session ID returned to frontend
   ↓
7. Session stored in st.session_state
   ↓
8. Dashboard displays session history
```

## Data Models

### Session Node

```cypher
(:Session {
    session_id: string,           // Neo4j internal ID
    session_type: string,         // flashcard_review, vocabulary_practice
    started_at: datetime,         // Session start time
    completed_at: datetime,       // Session end time
    words_reviewed: int,          // Number of words reviewed
    correct_answers: int,         // Number of correct answers
    accuracy: float,              // Accuracy percentage (0-100)
    duration_seconds: int,        // Session duration
    details: string               // Additional JSON metadata
})
```

### Relationship

```cypher
(:Student)-[:COMPLETED_SESSION]->(:Session)
```

**Properties on Relationship:** None (all data in Session node)

## Implementation Details

### Neo4j Learning Manager

Located at: `src/italianollama/memory/learning.py:247-373`

#### Create Session

```python
async def create_session(
    self,
    student_id: str,
    session_type: str,
    details: dict | None = None,
) -> str:
    """Create a new learning session."""
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
    
    async with self._driver.session(database=self.database) as session:
        result = await session.run(
            query,
            student_id=student_id,
            session_type=session_type,
            details=str(details) if details else "{}",
        )
        record = await result.single()
        return record["session_id"] if record else None
```

**Notes:**
- Uses `MERGE` to ensure Student node exists
- Creates new Session node with timestamp
- Returns Neo4j internal ID via `elementId()`
- Stores details as string (JSON serialization)

#### Update Session

```python
async def update_session(
    self,
    session_id: str,
    words_reviewed: int = 0,
    correct_answers: int = 0,
    accuracy: float = 0.0,
    duration_seconds: int = 0,
) -> bool:
    """Update session with completion metrics."""
    query = """
    MATCH (sess:Session)
    WHERE elementId(sess) = $session_id
    SET sess.words_reviewed = $words_reviewed,
        sess.correct_answers = $correct_answers,
        sess.accuracy = $accuracy,
        sess.duration_seconds = $duration_seconds,
        sess.completed_at = datetime()
    RETURN sess.session_type
    """
    
    async with self._driver.session(database=self.database) as session:
        result = await session.run(query, **locals())
        return (await result.single()) is not None
```

**Notes:**
- Updates metrics after session completion
- Sets `completed_at` timestamp
- Returns success status

#### Get Session History

```python
async def get_session_history(
    self,
    student_id: str,
    limit: int = 10,
) -> list[dict]:
    """Get session history for a student."""
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
    
    async with self._driver.session(database=self.database) as session:
        result = await session.run(query, student_id=student_id, limit=limit)
        records = await result.data()
        return [dict(r["session"]) for r in records]
```

**Notes:**
- Returns last N sessions (default: 10)
- Orders by `started_at DESC` (most recent first)
- Uses `COALESCE` for null safety

### TutorAPIClient

Located at: `src/italianollama/frontend/streamlit/tutor_api.py:494-554`

#### Create Session

```python
def create_session(
    self,
    student_id: str,
    session_type: str,
    details: dict | None = None,
) -> dict | None:
    """Create a new learning session in Neo4j."""
    result = self._request(
        "POST",
        f"/session/{student_id}",
        json_data={
            "session_type": session_type,
            "details": details or {},
        },
    )
    return result
```

**Usage:**
```python
api = TutorAPIClient()
result = api.create_session(
    student_id="uuid-123",
    session_type="flashcard_review",
    details={"words_reviewed": 10, "accuracy": 85.0}
)
if result:
    session_id = result.get("session_id")
```

#### Update Session

```python
def update_session(
    self,
    session_id: str,
    words_reviewed: int = 0,
    correct_answers: int = 0,
    accuracy: float = 0.0,
    duration_seconds: int = 0,
) -> dict | None:
    """Update session with completion metrics."""
    result = self._request(
        "PUT",
        f"/session/{session_id}",
        json_data={
            "words_reviewed": words_reviewed,
            "correct_answers": correct_answers,
            "accuracy": accuracy,
            "duration_seconds": duration_seconds,
        },
    )
    return result
```

**Usage:**
```python
api.update_session(
    session_id="12345",
    words_reviewed=15,
    correct_answers=12,
    accuracy=80.0,
    duration_seconds=300
)
```

#### Get Session History

```python
def get_session_history(
    self,
    student_id: str,
    limit: int = 10,
) -> list | None:
    """Get session history for a student."""
    result = self._request(
        "GET",
        f"/session/history/{student_id}",
        params={"limit": limit},
    )
    return result.get("sessions") if result else None
```

**Usage:**
```python
history = api.get_session_history("uuid-123", limit=5)
for session in history:
    print(f"{session['session_type']}: {session['accuracy']}%")
```

### Streamlit Frontend Integration

Located at: `src/italianollama/frontend/streamlit/pages/04_vocabulary.py:74-100`

#### Track Session Function

```python
def track_session(session_type: str, details: dict):
    """Track session in Neo4j via TutorAPIClient."""
    try:
        session_data = {
            "student_id": student_id,
            "session_type": session_type,
            "started_at": datetime.now().isoformat(),
            "details": details,
            "duration_seconds": details.get("duration", 0),
            "words_reviewed": details.get("words_reviewed", 0),
            "correct_answers": details.get("correct_answers", 0),
            "accuracy": details.get("accuracy", 0),
        }
        
        # Create session in Neo4j via API
        result = api.create_session(student_id, session_type, details)
        if result:
            session_data["session_id"] = result.get("session_id")
            st.session_state.last_session = session_data
            st.session_state.session_history = api.get_session_history(student_id, limit=10) or []
        else:
            # Fallback to session state if API unavailable
            st.session_state.last_session = session_data
        
    except Exception as e:
        st.debug(f"Session tracking logged (API unavailable): {str(e)}")
```

**Features:**
- Automatic session_id storage
- Updates session history in state
- Graceful fallback when API unavailable
- Error handling with debug logging

### Session Storage in Streamlit

Sessions are stored in `st.session_state`:

```python
# Last completed session
st.session_state.last_session = {
    "student_id": "uuid",
    "session_type": "flashcard_review",
    "started_at": "2024-01-15T10:30:00",
    "duration_seconds": 900,
    "words_reviewed": 10,
    "correct_answers": 9,
    "accuracy": 90.0,
}

# Session history (last 10)
st.session_state.session_history = [
    {
        "session_type": "flashcard_review",
        "started_at": "2024-01-15T10:30:00",
        "words_reviewed": 10,
        "accuracy": 90.0,
        # ... other fields
    },
    # ... more sessions
]
```

## Session Types

### Predefined Types

| Type | Description | Example |
|------|-------------|---------|
| `flashcard_review` | Flashcard practice sessions | `track_session("flashcard_review", details)` |
| `vocabulary_practice` | General vocabulary practice | `track_session("vocabulary_practice", details)` |
| `grammar_drill` | Grammar exercises | `track_session("grammar_drill", details)` |
| `exam_simulation` | Exam preparation | `track_session("exam_simulation", details)` |
| `placement_test` | CEFR placement assessment | `track_session("placement_test", details)` |

### Custom Session Types

```python
# Track custom session
track_session("custom_italian_lesson", {
    "topic": "Restaurant ordering",
    "words_reviewed": 20,
    "accuracy": 85.0,
})
```

## Session Metrics

### Core Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `session_type` | string | Type of session |
| `started_at` | datetime | Session start time |
| `completed_at` | datetime | Session end time |
| `words_reviewed` | int | Number of words/exercises |
| `correct_answers` | int | Number of correct responses |
| `accuracy` | float | Accuracy percentage (0-100) |
| `duration_seconds` | int | Session duration |

### Calculated Metrics

```python
# Average words per session
avg_words = total_words / session_count

# Average accuracy
avg_accuracy = sum(accuracies) / len(accuracies)

# Improvement rate
improvement = (current_accuracy - previous_accuracy) / previous_accuracy * 100

# Time per word
time_per_word = total_duration / total_words
```

## Dashboard Integration

### Session History Display

```python
st.markdown("### 📅 Cronologia Sessioni")

if "session_history" in st.session_state and st.session_state.session_history:
    for session in st.session_state.session_history[-5:]:  # Last 5
        with st.container(border=True):
            st.markdown(f"**{session.get('session_type')}**")
            st.caption(f"📅 {session.get('started_at')}")
            st.caption(f"📊 {session.get('words_reviewed')} parole | {session.get('accuracy'):.1f}% accuracy")
else:
    st.info("La cronologia delle sessioni verrà registrata qui dopo le prime review")
```

### Session Statistics

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Sessioni Totali", len(session_history))
    
with col2:
    avg_accuracy = sum(s.get('accuracy', 0) for s in session_history) / len(session_history)
    st.metric("Accuracy Media", f"{avg_accuracy:.1f}%")
    
with col3:
    total_words = sum(s.get('words_reviewed', 0) for s in session_history)
    st.metric("Parole Totali", total_words)
```

## Neo4j Queries

### Get Student Session Statistics

```cypher
MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
RETURN 
    COUNT(sess) AS total_sessions,
    AVG(sess.words_reviewed) AS avg_words_per_session,
    AVG(sess.accuracy) AS avg_accuracy,
    SUM(sess.duration_seconds) / 3600 AS total_hours,
    MIN(sess.started_at) AS first_session,
    MAX(sess.started_at) AS last_session
```

### Get Session Timeline

```cypher
MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
RETURN 
    date(sess.started_at) as day,
    COUNT(sess) as sessions,
    AVG(sess.accuracy) as avg_accuracy,
    SUM(sess.words_reviewed) as words_reviewed
ORDER BY day
```

### Get Session by Type

```cypher
MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
WHERE sess.session_type = $session_type
RETURN sess
ORDER BY sess.started_at DESC
LIMIT 20
```

### Get Recent Sessions

```cypher
MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
RETURN sess
ORDER BY sess.started_at DESC
LIMIT 10
```

### Calculate Progress Metrics

```cypher
MATCH (s:Student {student_id: $student_id})-[:COMPLETED_SESSION]->(sess:Session)
WHERE sess.started_at > datetime() - duration({days: 30})
WITH 
    COUNT(sessions) as total_sessions,
    AVG(accuracy) as avg_accuracy,
    SUM(words_reviewed) as total_words
RETURN 
    total_sessions,
    round(avg_accuracy, 1) as avg_accuracy,
    total_words,
    CASE 
        WHEN avg_accuracy > 80 THEN 'Excellent'
        WHEN avg_accuracy > 60 THEN 'Good'
        ELSE 'Needs Practice'
    END as performance
```

## Best Practices

### 1. Session Naming

Use lowercase with underscores:

```python
# Good
track_session("flashcard_review", details)
track_session("vocabulary_practice", details)

# Avoid
track_session("FlashcardReview", details)
track_session("vocabulary-practice", details)
```

### 2. Accuracy Calculation

Use float division:

```python
# Good
accuracy = (correct / total) * 100  # e.g., 9/10 = 90.0%

# Avoid
accuracy = (correct // total) * 100  # e.g., 9//10 = 0%
```

### 3. Error Handling

Always wrap session tracking:

```python
try:
    track_session("flashcard_review", session_details)
except Exception as e:
    logger.error(f"Session tracking failed: {e}")
    # Continue with app flow
```

### 4. Session Timing

Track start/end times:

```python
import time

start_time = time.time()
# ... session activities ...
duration = time.time() - start_time

track_session("flashcard_review", {
    "duration": duration,
    "words_reviewed": 10,
    "accuracy": 85.0,
})
```

### 5. Data Validation

Validate session details:

```python
def track_session(session_type: str, details: dict):
    # Validate required fields
    if not details.get("accuracy"):
        details["accuracy"] = 0.0
    if not details.get("words_reviewed"):
        details["words_reviewed"] = 0
    
    # Create session
    result = api.create_session(student_id, session_type, details)
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs API calls
logger = logging.getLogger(__name__)
logger.debug(f"Session tracking: {session_data}")
```

### Check Neo4j Connection

```python
# Verify Neo4j is accessible
result = api.health_check()
if result:
    print("Neo4j connection OK")
else:
    print("Neo4j connection failed")
```

### Verify Session Creation

```cypher
# Check recent sessions
MATCH (s:Student {student_id: 'your-student-id'})-[:COMPLETED_SESSION]->(sess:Session)
RETURN sess
ORDER BY sess.started_at DESC
LIMIT 5
```

## Performance Optimization

### Caching Strategy

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_session_history_cached(student_id: str, limit: int = 10):
    return api.get_session_history(student_id, limit)
```

### Batch Updates

```python
# Update multiple sessions at once
sessions_to_update = [
    {"session_id": "1", "accuracy": 85},
    {"session_id": "2", "accuracy": 90},
    # ...
]

for session in sessions_to_update:
    api.update_session(**session)
```

## Security Considerations

### Student Data Isolation

```python
# Ensure student can only access their own sessions
def get_session_history(student_id: str):
    # Verify user owns this student_id
    if not user_owns_student(student_id):
        raise PermissionError("Access denied")
    
    return api.get_session_history(student_id)
```

### Input Validation

```python
def track_session(session_type: str, details: dict):
    # Validate session type
    valid_types = ["flashcard_review", "vocabulary_practice", "grammar_drill"]
    if session_type not in valid_types:
        raise ValueError(f"Invalid session type: {session_type}")
    
    # Validate accuracy range
    accuracy = details.get("accuracy", 0)
    if not 0 <= accuracy <= 100:
        raise ValueError(f"Accuracy must be 0-100, got {accuracy}")
```

## Troubleshooting

### Common Issues

**Issue:** Sessions not appearing in Neo4j

**Solution:**
1. Check Neo4j connection
2. Verify student_id exists
3. Check for exceptions in logs

**Issue:** Session accuracy shows 0%

**Solution:**
1. Verify correct/total calculations
2. Check session details passed to `track_session()`

**Issue:** Session history empty

**Solution:**
1. Run `api.get_session_history()` to verify data exists
2. Check cache expiration
3. Verify student_id matches

## Future Enhancements

### Planned Features

1. **Real-time Updates** - WebSocket for live session tracking
2. **Analytics Dashboard** - Advanced charts and graphs
3. **Export Functionality** - Download session data
4. **Reminder System** - Email notifications for missed sessions
5. **Mobile App** - Native iOS/Android with offline support
6. **AI Insights** - Automated progress analysis
7. **Social Features** - Share progress with friends
8. **Gamification** - Badges and achievements system

## Related Documentation

- [Flashcard Review](flashcard-review.md) - Flashcard system details
- [Progress Tracking](progress-tracking.md) - Overall progress system
- [Database Schema](../architecture/database.md) - Neo4j data models
- [API Endpoints](../api/endpoints.md) - Backend API reference
