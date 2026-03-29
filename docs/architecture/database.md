# Database Schema

ItalianOllama uses Neo4j as its graph database to store student profiles, vocabulary, grammar errors, and learning progress.

## Overview

Neo4j is ideal for this application because:
- **Graph structure** naturally represents relationships between words, rules, and concepts
- **Efficient queries** for traversing student knowledge networks
- **Flexible schema** for evolving data models
- **Aura cloud** support for production deployments

## Node Types

### Student Node

Represents a learner in the system.

```cypher
(:Student {
    student_id: string,
    name: string,
    email: string,
    created_at: datetime,
    current_cefr: string,
    total_sessions: int
})
```

**Properties:**
| Property | Type | Description |
|----------|------|-------------|
| `student_id` | string | Unique identifier (UUID) |
| `name` | string | Student's display name |
| `email` | string | Email for authentication |
| `created_at` | datetime | Account creation timestamp |
| `current_cefr` | string | Current CEFR level (A1-C2) |
| `total_sessions` | int | Number of learning sessions |

### CEFR Level Node

Stores CEFR (Common European Framework of Reference) level information.

```cypher
(:CEFRLevel {
    code: string,
    name: string,
    confidence: float
})
```

**Levels:**
| Code | Name | Description |
|------|------|-------------|
| A1 | Beginner | Can understand and use familiar expressions |
| A2 | Elementary | Can communicate in simple tasks |
| B1 | Intermediate | Can deal with most situations likely to arise |
| B2 | Upper Intermediate | Can interact with fluency and spontaneity |
| C1 | Advanced | Can express ideas fluently without searching |
| C2 | Mastery | Can understand virtually everything heard or read |

### Vocabulary Node

Stores vocabulary items the student is learning.

```cypher
(:Vocabulary {
    word: string,
    translation: string,
    topic: string,
    level: string,
    confidence: float,
    last_practiced: datetime,
    next_review: datetime
})
```

### Grammar Error Node

Tracks grammar errors made by the student.

```cypher
(:GrammarError {
    original: string,
    corrected: string,
    rule: string,
    level: string,
    seen_count: int,
    last_seen: datetime
})
```

### Exercise Node

Records completed exercises.

```cypher
(:Exercise {
    type: string,
    score: int,
    level: string,
    content: string,
    completed_at: datetime,
    duration_seconds: int
})
```

**Types:**
| Type | Description |
|------|-------------|
| `placement` | CEFR level assessment |
| `vocabulary` | Flashcard practice |
| `grammar` | Grammar drills |
| `translation` | Translation exercises |
| `free_writing` | Writing with feedback |
| `niveau_test` | Exam simulation |

### Niveau Test Node

Stores exam preparation test results.

```cypher
(:NiveauTest {
    test_type: string,
    level: string,
    readiness: float,
    skill_scores: map,
    completed_at: datetime
})
```

**Test Types:**
| Type | Description |
|------|-------------|
| `TELC` | The European Language Certificates |
| `Goethe` | Goethe-Institut exams |
| `CILS` | Certificazione di Italiano come Lingua Straniera |
| `CELI` | Certificato di Conoscenza della Lingua Italiana |

## Relationship Types

### HAS_LEVEL

```cypher
(:Student)-[:HAS_LEVEL]->(:CEFRLevel)
```

Links a student to their current CEFR level.

### KNOWS

```cypher
(:Student)-[:KNOWS]->(:Vocabulary)
```

Links a student to vocabulary they have learned.
Confidence level is stored on the relationship.

### MADE_ERROR

```cypher
(:Student)-[:MADE_ERROR]->(:GrammarError)
```

Tracks grammar errors made by the student.

### COMPLETED

```cypher
(:Student)-[:COMPLETED]->(:Exercise)
```

Records exercise completion history.

### READY_FOR

```cypher
(:Student)-[:READY_FOR]->(:NiveauTest)
```

Indicates readiness for specific exam types.

### RELATES_TO

```cypher
(:Vocabulary)-[:RELATES_TO]->(:Vocabulary)
(:GrammarError)-[:RELATES_TO]->(:GrammarError)
```

Links related vocabulary or grammar concepts.

## Example Queries

### Get Student Profile with Progress

```cypher
MATCH (s:Student {student_id: $student_id})
OPTIONAL MATCH (s)-[:HAS_LEVEL]->(l:CEFRLevel)
OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
OPTIONAL MATCH (s)-[:COMPLETED]->(e:Exercise)
OPTIONAL MATCH (s)-[:MADE_ERROR]->(g:GrammarError)
RETURN s, l, 
       collect(DISTINCT v) as vocabulary,
       collect(DISTINCT e) as exercises,
       collect(DISTINCT g) as errors
```

### Update Vocabulary Confidence

```cypher
MATCH (s:Student {student_id: $student_id})-[r:KNOWS]->(v:Vocabulary {word: $word})
SET r.confidence = $new_confidence,
    v.last_practiced = datetime(),
    v.next_review = datetime() + duration({days: $days})
```

### Get Spaced Repetition Queue

```cypher
MATCH (s:Student {student_id: $student_id})-[r:KNOWS]->(v:Vocabulary)
WHERE v.next_review <= datetime() OR v.next_review IS NULL
RETURN v, r.confidence
ORDER BY r.confidence ASC
LIMIT 20
```

### Get Grammar Error Patterns

```cypher
MATCH (s:Student {student_id: $student_id})-[:MADE_ERROR]->(g:GrammarError)
RETURN g.rule, count(*) as frequency
ORDER BY frequency DESC
LIMIT 10
```

### Get CEFR Progress Stats

```cypher
MATCH (s:Student {student_id: $student_id})-[:HAS_LEVEL]->(l:CEFRLevel)
MATCH (s)-[:KNOWS]->(v:Vocabulary)
MATCH (s)-[:COMPLETED]->(e:Exercise)
RETURN l.code as level,
       count(DISTINCT v) as vocabulary_count,
       count(DISTINCT e) as exercises_completed,
       avg(e.score) as avg_score
```

## Indexes and Constraints

```cypher
# Create indexes for performance
CREATE INDEX student_id_idx FOR (s:Student) ON (s.student_id);
CREATE INDEX vocabulary_word_idx FOR (v:Vocabulary) ON (v.word);
CREATE INDEX vocab_review_idx FOR (v:Vocabulary) ON (v.next_review);

# Create constraints
CREATE CONSTRAINT student_email_unique FOR (s:Student) REQUIRE s.email IS UNIQUE;
```

## Neo4j Aura (Cloud)

### Connect to Aura

```python
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=your_username
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
USE_AURA=true
```

### Local Development

```bash
# Start local Neo4j
docker run -d \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_PASSWORD=password \
  neo4j

# Connect
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
USE_AURA=false
```

## Data Backup

### Export Data

```bash
# Using cypher-shell
docker exec neo4j cypher-shell -u neo4j -p password \
  "CALL apoc.export.json.all('backup.json', {})"
```

### Import Data

```bash
docker exec neo4j cypher-shell -u neo4j -p password \
  "CALL apoc.import.json('backup.json', {})"
```

## Related Documentation

- [Backend Architecture](backend.md)
- [Neo4j Client Code](../development/debugging.md#neo4j)
- [Troubleshooting](troubleshooting/common-issues.md)
