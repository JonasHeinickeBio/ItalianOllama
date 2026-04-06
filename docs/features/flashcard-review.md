# Flashcard Review System

The flashcard review system implements spaced repetition and confidence-based learning with full Neo4j session tracking.

## Overview

The flashcard review system provides:
- **Spaced Repetition** - Algorithm-based review scheduling
- **Confidence Assessment** - Self-reported mastery levels
- **Session Tracking** - Complete progress tracking in Neo4j
- **Analytics Dashboard** - Visual progress visualization

## Components

### 1. Flashcard Review Page (`04_vocabulary.py`)

Located at: `src/italianollama/frontend/streamlit/pages/04_vocabulary.py`

#### Tabs

| Tab | Description | Function |
|-----|-------------|----------|
| **Il Mio Vocabolario** | Vocabulary list with search | `get_vocabulary_items()` |
| **Aggiungi Nuova Parola** | Add new words | `add_vocabulary()` API |
| **Flashcard Review** | Review sessions | `run_flashcard_review()` |
| **Progresso** | Analytics dashboard | Session history display |

#### Vocabulary List (Tab 1)

**Features:**
- CEFR level filtering (A1-C2)
- Search by Italian word
- 3-column responsive grid
- Confidence indicators
- Topic tags

**Code:** `04_vocabulary.py:205-264`

```python
# Get vocabulary with optional filtering
vocabulary = get_vocabulary_items(due_for_review=False, level_filter=level_filter)

# Display in grid
for row in range(rows):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        vocab_idx = row * cols_per_row + col_idx
        if vocab_idx < len(vocabulary):
            word = vocabulary[vocab_idx]
            with cols[col_idx]:
                # Display word card
```

#### Add New Word (Tab 2)

**Features:**
- Italian word & English translation
- Part of speech selection
- CEFR level assignment
- Topic tagging
- Example sentence

**Code:** `04_vocabulary.py:266-337`

```python
with st.form("add_vocab_form", border=True):
    italian = st.text_input("Parola italiana *")
    english = st.text_input("Traduzione inglese *")
    pos = st.selectbox("Parte del discorso *", ["noun", "verb", "adjective"])
    level = st.selectbox("Livello CEFR *", ["A1", "A2", "B1", "B2", "C1", "C2"])
    topic = st.text_input("Argomento")
    example_sentence = st.text_area("Frase di esempio")
```

#### Flashcard Review (Tab 3)

**Features:**
- Select number of cards (5-50)
- Filter by CEFR level
- Random word sampling
- Confidence-based scoring
- Progress tracking

**Code:** `04_vocabulary.py:339-395`

```python
def run_flashcard_review(vocabulary: list[dict], num_cards: int = 10) -> dict:
    """Run flashcard review session and track results."""
    cards = random.sample(vocabulary, min(num_cards, len(vocabulary)))
    
    for i, card in enumerate(cards, 1):
        # Display card
        st.markdown(f"### {i}. {card.get('italian_word')}")
        st.caption(f"**English:** {card.get('english_translation')}")
        
        # Confidence assessment
        confidence = st.radio(
            "",
            options=["❌ Not at all", "🤔 Somewhat", "✅ Confident"],
            key=f"conf_{i}",
            horizontal=True,
        )
        
        # Score calculation
        if confidence == "✅ Confident":
            results["correct"] += 1
        elif confidence == "🤔 Somewhat":
            results["correct"] += 0.5
```

#### Progress Dashboard (Tab 4)

**Features:**
- CEFR level distribution
- Session statistics
- Session history (last 5)
- Recent activity tracking

**Code:** `04_vocabulary.py:397-452`

```python
# CEFR Distribution
for level in sorted(levels_count.keys()):
    count = levels_count[level]
    pct = (count / total_words) * 100
    st.progress(min(pct / 100, 1.0), text=f"{level}: {count} ({pct:.1f}%)")

# Session History
for session in st.session_state.session_history[-5:]:
    st.markdown(f"**{session.get('session_type')}**")
    st.caption(f"📊 {session.get('words_reviewed')} parole | {session.get('accuracy'):.1f}%")
```

### 2. Session Tracking API (`tutor_api.py`)

Located at: `src/italianollama/frontend/streamlit/tutor_api.py`

#### Methods

**`create_session()`** - Create new session in Neo4j
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
```

**`update_session()`** - Update session with metrics
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
```

**`get_session_history()`** - Retrieve session history
```python
def get_session_history(self, student_id: str, limit: int = 10) -> list | None:
    """Get session history for a student."""
```

**Code:** `tutor_api.py:494-554`

### 3. Neo4j Learning Manager (`learning.py`)

Located at: `src/italianollama/memory/learning.py`

#### Session Methods

**`create_session()`** - Create session node
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
```

**`update_session()`** - Update with metrics
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
```

**`get_session_history()`** - Query session history
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
```

**Code:** `learning.py:247-373`

## Data Models

### Session Node Schema

```cypher
(:Session {
    session_type: string,        // flashcard_review, vocabulary_practice
    started_at: datetime,        // Session start time
    completed_at: datetime,      // Session end time
    words_reviewed: int,         // Number of words reviewed
    correct_answers: int,        // Number of correct answers
    accuracy: float,             // Accuracy percentage (0-100)
    duration_seconds: int,       // Session duration
    details: string              // Additional JSON data (stored as string)
})
```

### Relationship

```cypher
(:Student)-[:COMPLETED_SESSION]->(:Session)
```

## Session Tracking Integration

### Flow

```
User clicks "Start Flashcard Review"
    ↓
run_flashcard_review() called
    ↓
Cards displayed one by one
    ↓
User rates confidence for each card
    ↓
Results calculated (correct, incorrect, accuracy)
    ↓
track_session() called
    ↓
api.create_session() creates Neo4j node
    ↓
Results displayed in dashboard
```

### Code Implementation

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

**Code:** `04_vocabulary.py:74-100`

### Flashcard Review Flow

```python
def run_flashcard_review(vocabulary: list[dict], num_cards: int = 10) -> dict:
    """Run flashcard review session and track results."""
    # 1. Select random subset
    cards = random.sample(vocabulary, min(num_cards, len(vocabulary)))
    
    results = {
        "total": len(cards),
        "correct": 0,
        "incorrect": 0,
        "session_words": [],
    }
    
    # 2. Display and assess each card
    for i, card in enumerate(cards, 1):
        with st.container(border=True):
            # Display word and translation
            st.markdown(f"### {i}. {card.get('italian_word')}")
            st.caption(f"**English:** {card.get('english_translation')}")
            
            # Confidence assessment
            confidence = st.radio(
                "",
                options=["❌ Not at all", "🤔 Somewhat", "✅ Confident"],
                key=f"conf_{i}",
                horizontal=True,
            )
            
            # Record result
            if confidence == "✅ Confident":
                results["correct"] += 1
            elif confidence == "🤔 Somewhat":
                results["correct"] += 0.5  # Partial credit
            else:
                results["incorrect"] += 1
            
            results["session_words"].append({
                "word": card.get("italian_word"),
                "level": card.get("cefr_level"),
                "known": confidence == "✅ Confident",
            })
    
    # 3. Calculate accuracy
    accuracy = (results["correct"] / results["total"]) * 100
    
    # 4. Complete session tracking
    session_details = {
        "duration": 0,  # Would track start/end time in real implementation
        "words_reviewed": results["total"],
        "correct_answers": results["correct"],
        "accuracy": round(accuracy, 1),
        "flashcards_shown": results["total"],
    }
    
    track_session("flashcard_review", session_details)
    
    return {
        **results,
        "accuracy": accuracy,
        "session_details": session_details,
    }
```

**Code:** `04_vocabulary.py:102-186`

## Confidence Scoring System

### Levels

| Emoji | Label | Score | Meaning |
|-------|-------|-------|---------|
| ❌ | Not at all | 0% | No knowledge of word |
| 🤔 | Somewhat | 50% | Partial recognition |
| ✅ | Confident | 100% | Fully confident |

### Accuracy Calculation

```python
accuracy = (results["correct"] / results["total"]) * 100

# Example:
# 8 "✅ Confident" + 2 "🤔 Somewhat" = 9.0 out of 10
# accuracy = (8 + 2*0.5) / 10 * 100 = 90%
```

## Session Metrics

### Tracked Data

Each session records:

```python
session_data = {
    "student_id": "uuid",              # Student identifier
    "session_type": "flashcard_review", # Session type
    "started_at": "2024-01-15T10:30:00", # Start timestamp
    "completed_at": "2024-01-15T10:45:00", # End timestamp
    "words_reviewed": 10,              # Number of words
    "correct_answers": 9,              # Correct responses
    "accuracy": 90.0,                  # Percentage
    "duration_seconds": 900,           # Duration in seconds
    "details": {                       # Additional metadata
        "flashcards_shown": 10,
        "level_filter": "B1",
    }
}
```

### Dashboard Display

```python
# CEFR Distribution
for level in sorted(levels_count.keys()):
    count = levels_count[level]
    pct = (count / total_words) * 100
    st.progress(min(pct / 100, 1.0), text=f"{level}: {count} ({pct:.1f}%)")

# Session History (last 5)
for session in st.session_state.session_history[-5:]:
    with st.container(border=True):
        st.markdown(f"**{session.get('session_type')}**")
        st.caption(f"📅 {session.get('started_at')}")
        st.caption(f"📊 {session.get('words_reviewed')} parole | {session.get('accuracy'):.1f}% accuracy")
```

## Error Handling

### Graceful Degradation

```python
def track_session(session_type: str, details: dict):
    try:
        result = api.create_session(student_id, session_type, details)
        if result:
            # Success - store session_id
            session_data["session_id"] = result.get("session_id")
            st.session_state.last_session = session_data
        else:
            # Fallback to session state if API unavailable
            st.session_state.last_session = session_data
    except Exception as e:
        st.debug(f"Session tracking logged (API unavailable): {str(e)}")
```

### User Feedback

```python
if results["accuracy"] < 50:
    st.warning("💡 Consiglio: Ripassa queste parole più spesso")
elif results["accuracy"] < 80:
    st.info("👍 Buon lavoro! Rivedi le parole sconosciute")
else:
    st.balloons()
    st.success("🌟 Eccellente! Continuate così")
```

## Advanced Features

### CEFR Level Filtering

```python
def get_vocabulary_items(due_for_review: bool = False, level_filter: str = None):
    """Fetch vocabulary with caching."""
    vocabulary = api.get_vocabulary(student_id, due_for_review=due_for_review)
    
    if level_filter and level_filter != "All":
        vocabulary = [w for w in vocabulary if w.get("cefr_level") == level_filter]
    
    return vocabulary
```

### Random Sampling

```python
def run_flashcard_review(vocabulary: list[dict], num_cards: int = 10) -> dict:
    # Select random subset
    cards = random.sample(vocabulary, min(num_cards, len(vocabulary)))
    
    # Process cards...
```

### Search Functionality

```python
search_term = st.text_input("🔍 Cerca una parola...", placeholder="Search by Italian word...")

if search_term:
    vocabulary = [
        w for w in vocabulary 
        if search_term.lower() in w.get("italian_word", "").lower()
    ]
```

## Neo4j Query Examples

### Get Session History

```cypher
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
LIMIT 10
```

### Get Session by ID

```cypher
MATCH (sess:Session)
WHERE elementId(sess) = $session_id
RETURN sess.session_type,
       sess.words_reviewed,
       sess.correct_answers,
       sess.accuracy,
       sess.completed_at
```

### Update Session

```cypher
MATCH (sess:Session)
WHERE elementId(sess) = $session_id
SET sess.words_reviewed = $words_reviewed,
    sess.correct_answers = $correct_answers,
    sess.accuracy = $accuracy,
    sess.duration_seconds = $duration_seconds,
    sess.completed_at = datetime()
RETURN sess.session_type
```

## Best Practices

### 1. Session Naming Convention

Use snake_case for session types:
- `flashcard_review` - Flashcard practice
- `vocabulary_practice` - General vocabulary practice
- `grammar_drill` - Grammar exercises
- `exam_simulation` - Exam preparation

### 2. Accuracy Calculation

Always use float division:
```python
accuracy = (correct / total) * 100  # Not: (correct // total) * 100
```

### 3. Error Handling

Always wrap session tracking in try-except:
```python
try:
    result = api.create_session(...)
except Exception as e:
    logger.warning(f"Session tracking failed: {e}")
```

### 4. Data Consistency

Update session immediately after review completion:
```python
session_details = {
    "words_reviewed": results["total"],
    "correct_answers": results["correct"],
    "accuracy": round(accuracy, 1),
}
track_session("flashcard_review", session_details)
```

## Future Enhancements

### Planned Features

1. **Time Tracking** - Start/end timestamps for accurate duration
2. **Spaced Repetition Algorithm** - SM-2 based scheduling
3. **Audio Pronunciation** - Text-to-speech for Italian words
4. **Sentence Context** - Example sentences with words
5. **Image Association** - Visual learning with images
6. **Mobile Optimization** - Touch-friendly interface
7. **Offline Mode** - Session caching for offline practice
8. **Analytics Dashboard** - Advanced progress visualization

## Troubleshooting

### Common Issues

**Issue:** Sessions not appearing in dashboard
- **Solution:** Check Neo4j connection and API availability
- **Fix:** Verify `NEO4J_URI` and `NEO4J_PASSWORD` environment variables

**Issue:** Flashcard review not loading
- **Solution:** Check vocabulary exists for selected level
- **Fix:** Add vocabulary words or select "All" level filter

**Issue:** Accuracy calculation incorrect
- **Solution:** Verify confidence scoring logic
- **Fix:** Check `run_flashcard_review()` accuracy calculation

## Related Documentation

- [Progress Tracking](progress-tracking.md) - Overall progress tracking system
- [Dashboard Features](dashboard.md) - Analytics dashboard
- [Database Schema](../architecture/database.md) - Neo4j data models
- [API Endpoints](../api/endpoints.md) - Backend API reference
