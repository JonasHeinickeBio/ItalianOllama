# Vocabulary Learning System Documentation

## Overview

The ItalianOllama vocabulary learning system provides a comprehensive flashcard-based learning experience with Neo4j-powered session tracking and progress analytics.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Vocabulary   │  │ Flashcard    │  │ Progress     │       │
│  │ Browser      │  │ Review       │  │ Dashboard    │       │
│  │ UI           │  │ Sessions     │  │ Analytics    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │                │
│         └──────────────────┴──────────────────┘                │
│                            │                                   │
│                    ┌───────▼───────┐                          │
│                    │ TutorAPIClient│                          │
│                    └───────┬───────┘                          │
└────────────────────────────┼──────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Vocabulary   │  │ Session      │  │ Analytics    │       │
│  │ API          │  │ API          │  │ API          │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │                │
│         └──────────────────┴──────────────────┘                │
│                            │                                   │
│                    ┌───────▼───────┐                          │
│                    │  Neo4j Client │                          │
│                    └───────┬───────┘                          │
└────────────────────────────┼──────────────────────────────────┘
                             │ Bolt Protocol
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Neo4j Graph Database                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Vocabulary   │  │ Session      │  │ Student      │       │
│  │ Nodes        │  │ Nodes        │  │ Nodes        │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │                │
│  Relationships: KNOWS, COMPLETED_SESSION                     │
└─────────────────────────────────────────────────────────────┘
```

## Data Models

### Vocabulary Node

```cypher
CREATE (v:Vocabulary {
    word: STRING,           // Italian word
    definition: STRING,     // English translation
    topic: STRING,          // Category/theme
    part_of_speech: STRING  // noun, verb, adjective, etc.
})
```

### Student-Vocabulary Relationship

```cypher
CREATE (s:Student {student_id: STRING})-[
    rel:KNOWS {
        confidence: FLOAT,      // 0.0 - 1.0 mastery level
        learned_at: DATETIME,   // When word was added
        last_reviewed: DATETIME,
        next_review: DATETIME   // For SRS scheduling
    }
]->(v:Vocabulary)
```

### Session Node

```cypher
CREATE (sess:Session {
    session_type: STRING,         // flashcard_review, practice, etc.
    started_at: DATETIME,
    completed_at: DATETIME,
    words_reviewed: INTEGER,
    correct_answers: INTEGER,
    accuracy: FLOAT,              // Percentage 0-100
    duration_seconds: INTEGER,
    details: JSON
})
```

### Session-Student Relationship

```cypher
CREATE (s:Student)-[
    rel:COMPLETED_SESSION
]->(sess:Session)
```

## API Endpoints

### Vocabulary Endpoints

#### Add Vocabulary

```http
POST /vocabulary
Authorization: Bearer <token>

{
    "student_id": "student_123",
    "italian_word": "gatto",
    "english_translation": "cat",
    "part_of_speech": "noun",
    "cefr_level": "A1",
    "topic": "animals"
}

Response: 200 OK
{
    "status": "success",
    "vocabulary_id": "node_123"
}
```

#### Get Vocabulary

```http
GET /vocabulary/{student_id}?due_for_review=false
Authorization: Bearer <token>

Response: 200 OK
{
    "vocabulary": [
        {
            "vocabulary_id": "node_123",
            "italian_word": "gatto",
            "english_translation": "cat",
            "cefr_level": "A1",
            "topic": "animals",
            "part_of_speech": "noun",
            "confidence_level": 0.75
        }
    ]
}
```

#### Update Confidence

```http
POST /vocabulary/{vocabulary_id}/confidence?confidence=4
Authorization: Bearer <token>

Response: 200 OK
{
    "status": "success",
    "new_confidence": 0.82
}
```

### Session Endpoints

#### Create Session

```http
POST /session/{student_id}
Authorization: Bearer <token>

{
    "session_type": "flashcard_review",
    "details": {
        "num_cards": 10,
        "cefr_level": "A1"
    }
}

Response: 200 OK
{
    "status": "success",
    "session_id": "node_456"
}
```

#### Update Session

```http
PUT /session/{session_id}
Authorization: Bearer <token>

{
    "words_reviewed": 10,
    "correct_answers": 8,
    "accuracy": 80.0,
    "duration_seconds": 120
}

Response: 200 OK
{
    "status": "success"
}
```

#### Get Session History

```http
GET /session/history/{student_id}?limit=10
Authorization: Bearer <token>

Response: 200 OK
{
    "sessions": [
        {
            "session_type": "flashcard_review",
            "started_at": "2026-04-03T10:30:00",
            "completed_at": "2026-04-03T10:32:00",
            "words_reviewed": 10,
            "correct_answers": 8,
            "accuracy": 80.0,
            "duration_seconds": 120
        }
    ]
}
```

## Flashcard Review Algorithm

### Confidence Scoring

The system uses a simplified spaced repetition algorithm:

| Confidence Level | Score | Confidence Update |
|-----------------|-------|-------------------|
| ❌ Not at all   | 0.0   | ↓ Decrease        |
| 🤔 Somewhat     | 0.5   | → Slight increase |
| ✅ Confident    | 1.0   | ↑ Increase        |

### Session Flow

1. **Random Sampling**: Select random vocabulary cards based on CEFR filter
2. **Card Display**: Show Italian word + English translation
3. **Confidence Assessment**: User rates knowledge level
4. **Result Recording**: Log correct/incorrect responses
5. **Statistics Calculation**: Compute accuracy and metrics
6. **Session Tracking**: Save to Neo4j graph database

### Progress Metrics

- **Total Words Reviewed**: Count of unique words in session
- **Correct Answers**: Sum of confident responses
- **Accuracy**: (Correct / Total) × 100
- **Session Duration**: Time from start to completion

## Streamlit Frontend Components

### Page Structure

```
04_vocabulary.py (455 lines)
├── Tab 1: "📖 Il Mio Vocabolario"
│   ├── Vocabulary grid display
│   ├── CEFR level filter
│   ├── Search functionality
│   └── Confidence bars
│
├── Tab 2: "➕ Aggiungi Nuova Parola"
│   ├── Italian word input
│   ├── English translation
│   ├── Part of speech selector
│   ├── CEFR level selector
│   └── Topic input
│
├── Tab 3: "🃏 Flashcard Review"
│   ├── Level selection dropdown
│   ├── Number of cards slider
│   ├── Flashcard session UI
│   ├── Confidence rating
│   └── Progress bar
│
└── Tab 4: "📊 Progresso"
    ├── Total words learned
    ├── CEFR distribution
    ├── Recent session stats
    └── Session history
```

### Key Functions

#### `get_vocabulary_items(due_for_review, level_filter)`

Fetches vocabulary with caching:

```python
@st.cache_data(ttl=120)
def get_vocabulary_items(due_for_review: bool = False, level_filter: str = None):
    """Fetch vocabulary with caching."""
    vocabulary = api.get_vocabulary(student_id, due_for_review=due_for_review)
    if level_filter and level_filter != "All":
        vocabulary = [w for w in vocabulary if w.get("cefr_level") == level_filter]
    return vocabulary
```

#### `track_session(session_type, details)`

Tracks sessions in Neo4j:

```python
def track_session(session_type: str, details: dict):
    """Track session in Neo4j via TutorAPIClient."""
    result = api.create_session(student_id, session_type, details)
    if result:
        st.session_state.last_session = session_data
        st.session_state.session_history = api.get_session_history(student_id, limit=10)
```

#### `run_flashcard_review(vocabulary, num_cards)`

Main flashcard review logic:

```python
def run_flashcard_review(vocabulary: list[dict], num_cards: int = 10) -> dict:
    """Run flashcard review session and track results."""
    cards = random.sample(vocabulary, min(num_cards, len(vocabulary)))
    results = {
        "total": len(cards),
        "correct": 0,
        "incorrect": 0,
        "session_words": [],
    }
    # Display cards, collect confidence ratings
    # Calculate accuracy, track session
    return results
```

## Neo4j Integration

### Learning Manager Methods

#### `create_session()`

```python
async def create_session(
    self,
    student_id: str,
    session_type: str,
    details: dict | None = None,
) -> str:
    """Create a new learning session in Neo4j."""
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

#### `update_session()`

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
    """
```

#### `get_session_history()`

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

## PDF Vocabulary Extraction

### Source PDFs

| PDF | Words | Level | Description |
|-----|-------|-------|-------------|
| Auf_jeden_Fall_A1.1.pdf | 402 | A1.1 | Beginner 1 |
| Auf_jeden_Fall_A1.2.pdf | 409 | A1.2 | Beginner 2 |
| Auf_jaten_Fall_A2.1.pdf | 361 | A2.1 | Elementary 1 |
| Auf_jaten_Fall_A2.2.pdf | 361 | A2.2 | Elementary 2 |
| Auf_jaten_Fall__B1.1.pdf | ~500 | B1.1 | Intermediate 1 |
| Auf_jaten_Fall__B1.2.pdf | ~500 | B1.2 | Intermediate 2 |

### Extraction Process

```python
# scripts/extract_pdf_vocabulary.py
import pdfplumber

def extract_tables_from_pdf(pdf_path: str) -> list:
    """Extract tables from PDF using pdfplumber."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.extend(table)
    return tables
```

### Output Format

```json
[
    {
        "italian_word": "gatto",
        "german_word": "Katze",
        "cefr_level": "A1.1",
        "topic": "animals",
        "part_of_speech": "noun"
    }
]
```

## Usage Examples

### Start Vocabulary Learning Session

1. **Navigate** to the Vocabulary page in Streamlit dashboard
2. **Select** "🃏 Flashcard Review" tab
3. **Choose** CEFR level filter (optional)
4. **Select** number of flashcards (5-50)
5. **Click** "Inizia Sessione Flashcard"
6. **Review** each card and rate confidence
7. **View** session statistics and progress

### Track Progress Over Time

1. **Navigate** to "📊 Progresso" tab
2. **View** total words learned
3. **Check** CEFR distribution balance
4. **Review** last 5 sessions in history
5. **Monitor** accuracy trends

### Add New Vocabulary

1. **Navigate** to "➕ Aggiungi Nuova Parola" tab
2. **Enter** Italian word and English translation
3. **Select** part of speech
4. **Choose** CEFR level
5. **Add** topic (optional)
6. **Submit** to add to vocabulary database

## Performance Considerations

### Caching Strategy

- **Vocabulary data**: 120-second cache TTL
- **CEFR levels**: 300-second cache TTL
- **Student profile**: 3600-second cache TTL

### Query Optimization

- Use indexed queries on `student_id`
- Limit result sets for large vocabularies
- Use COALESCE for null-safe aggregations
- Order by timestamp for session history

### Scalability

- Support for 10,000+ vocabulary items
- Session history retention: 100 sessions per student
- Concurrent session support: Unlimited

## Troubleshooting

### Common Issues

**Issue**: Session not tracking in Neo4j
- **Solution**: Check Neo4j connection and credentials
- **Solution**: Verify session node creation query

**Issue**: Flashcard review empty
- **Solution**: Add vocabulary words first
- **Solution**: Check student ID session state

**Issue**: Slow page load
- **Solution**: Check database indexes
- **Solution**: Clear cache with `st.cache_data.clear()`

## Future Enhancements

- [ ] Implement full SM-2 spaced repetition algorithm
- [ ] Add Italian-Italian definitions
- [ ] Include example sentences per word
- [ ] Add pronunciation audio recordings
- [ ] Create practice quizzes per CEFR level
- [ ] Add daily review scheduling
- [ ] Implement gamification (XP, badges, achievements)
- [ ] Add word categories and subcategories
- [ ] Create proficiency tests per CEFR level
- [ ] Support image-based flashcards
