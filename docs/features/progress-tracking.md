# Progress Tracking

ItalianOllama tracks student progress across multiple dimensions using Neo4j graph database.

## Overview

Progress tracking provides:
- **CEFR Level** - Current proficiency level
- **Vocabulary** - Words learned with confidence
- **Grammar** - Error patterns and improvements
- **Exercises** - Completion history and scores
- **Streaks** - Daily practice consistency

## Data Stored in Neo4j

### Student Profile

```cypher
(:Student {
    student_id: "uuid",
    name: "John",
    email: "john@example.com",
    created_at: datetime,
    current_cefr: "B1",
    total_sessions: 15
})
```

### CEFR Level

```cypher
(:Student)-[:HAS_LEVEL]->(:CEFRLevel {
    code: "B1",
    confidence: 0.75,
    assessed_at: datetime
})
```

### Vocabulary

```cypher
(:Student)-[:KNOWS {
    confidence: 0.85,
    last_practiced: datetime,
    times_correct: 10,
    times_incorrect: 2
}]->(:Vocabulary {
    word: "ciao",
    translation: "hello",
    topic: "greetings",
    level: "A1"
})
```

### Grammar Errors

```cypher
(:Student)-[:MADE_ERROR {
    seen_count: 3,
    last_seen: datetime
}]->(:GrammarError {
    original: "Io sono andato",
    corrected: "Io sono andata",
    rule: "gender_agreement",
    level: "A2"
})
```

### Exercise History

```cypher
(:Student)-[:COMPLETED]->(:Exercise {
    type: "vocabulary",
    score: 85,
    level: "B1",
    duration_seconds: 300,
    completed_at: datetime
})
```

## Metrics Tracked

### Vocabulary Metrics

| Metric | Description | Calculation |
|--------|-------------|-------------|
| **Total Words** | All learned words | COUNT(vocabulary) |
| **Mastered** | Confidence > 90% | COUNT(confidence > 0.9) |
| **Learning** | Confidence 50-90% | COUNT(confidence 0.5-0.9) |
| **Review Needed** | Confidence < 50% | COUNT(confidence < 0.5) |
| **Due for Review** | Past spaced repetition date | COUNT(next_review <= now) |

### Grammar Metrics

| Metric | Description |
|--------|-------------|
| **Total Errors** | All recorded errors |
| **Unique Rules** | Different rules violated |
| **Most Common** | Top error patterns |
| **Improvement** | Error reduction over time |

### Exercise Metrics

| Metric | Description |
|--------|-------------|
| **Completed** | Total exercises done |
| **Average Score** | Mean score across exercises |
| **Time Spent** | Total learning minutes |
| **Streak** | Consecutive practice days |

## CEFR Progression

### Level Requirements

| Level | Vocabulary | Grammar Errors | Exercises |
|-------|------------|----------------|-----------|
| A1 | 50-100 | < 50 | 10 |
| A2 | 100-300 | < 40 | 30 |
| B1 | 300-700 | < 30 | 60 |
| B2 | 700-1500 | < 20 | 100 |
| C1 | 1500-2500 | < 10 | 150 |
| C2 | 2500+ | < 5 | 200 |

### Level Assessment

Levels are assessed based on:
1. **Placement test** results
2. **Vocabulary size** and confidence
3. **Grammar accuracy**
4. **Exercise scores**

## Spaced Repetition

### Algorithm

```python
def calculate_next_review(confidence: float, correct: bool) -> datetime:
    if correct:
        # Increase interval based on confidence
        days = max(1, int(7 * confidence))
    else:
        # Decrease interval
        days = 1
    
    return datetime.now() + timedelta(days=days)
```

### Review Schedule

| Confidence | Correct | Incorrect |
|------------|---------|-----------|
| 90%+ | 14 days | 1 day |
| 70-89% | 7 days | 1 day |
| 50-69% | 3 days | 1 day |
| <50% | 1 day | 1 day |

## Progress in Chat

### Request Progress

```
User: Mostrami il mio progresso
Sofia: Your Progress:
━━━━━━━━━━━━━━━━━━━━━
CEFR Level: B1 (75%)
Vocabulary: 150 words
- Mastered: 67 (45%)
- Learning: 53 (35%)
- Review: 30 (20%)

Grammar Errors: 23
Exercises: 45 completed
Streak: 5 days 🔥
━━━━━━━━━━━━━━━━━━━━━
```

## Dashboard Visualization

### Progress Page

Shows:
- Current level with progress bar
- Total vocabulary count
- Grammar error count
- Milestone badges
- Session history chart

### Vocabulary Page

Shows:
- Confidence distribution (pie chart)
- Topic breakdown
- Words due for review
- Recent additions

### Grammar Page

Shows:
- Error frequency bar chart
- Rule breakdown
- Improvement trend
- Practice recommendations

## Query Examples

### Get Student Stats

```cypher
MATCH (s:Student {student_id: $id})
OPTIONAL MATCH (s)-[:HAS_LEVEL]->(l:CEFRLevel)
OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
RETURN 
    l.code as level,
    count(DISTINCT v) as vocab_count,
    avg(e.score) as avg_score,
    sum(e.duration_seconds) / 60 as total_minutes
```

### Get Spaced Repetition Queue

```cypher
MATCH (s:Student {student_id: $id})-[r:KNOWS]->(v:Vocabulary)
WHERE v.next_review <= datetime() OR v.next_review IS NULL
RETURN v, r.confidence
ORDER BY r.confidence ASC
LIMIT 20
```

### Get Progress Over Time

```cypher
MATCH (s:Student {student_id: $id})-[:COMPLETED]->(e:Exercise)
WHERE e.completed_at > datetime() - duration({days: 30})
RETURN date(e.completed_at) as day, count(e) as exercises, avg(e.score) as avg_score
ORDER BY day
```

## Milestones

### Available Milestones

| Milestone | Requirement | Badge |
|-----------|-------------|-------|
| First Lesson | Complete 1 exercise | 🎯 |
| 7-Day Streak | Practice 7 days in a row | 🔥 |
| 100 Words | Learn 100 vocabulary | 📚 |
| A2 Level | Reach A2 CEFR | ⭐⭐ |
| Perfect Score | Score 100% on exercise | 🏆 |
| 30-Day Streak | Practice 30 days | 💪 |
| 500 Words | Learn 500 vocabulary | 📖 |
| B1 Level | Reach B1 CEFR | 🌟 |

## Export Progress

### Download Vocabulary

Available in dashboard:
- CSV format
- Includes: word, translation, confidence, topic

### Progress Report

PDF report includes:
- Current level
- Vocabulary stats
- Grammar summary
- Exercise history
- Milestones achieved

## Related Documentation

- [Dashboard Features](dashboard.md)
- [Chat Interface](chat-interface.md)
- [Exercise Types](exercises.md)
- [Database Schema](../architecture/database.md)
