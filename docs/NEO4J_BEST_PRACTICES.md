# Best Practices for Italian Tutor Knowledge Graph

## Overview
This guide covers best practices for using the improved semantic knowledge graph in Neo4j, based on established patterns from educational knowledge graphs and learning systems research.

---

## 1. Data Model Design Principles

### ✅ DO: Make Relationships Semantic

**Good:**
```cypher
MATCH (student:Student)-[:UNDERSTANDS {mastery_level: 0.85}]->(concept:Concept)
MATCH (attempt:Attempt)-[:TESTS_CONCEPT]->(concept:Concept)
MATCH (vocab:Vocabulary)-[:EXPRESSES]->(concept:Concept)
```

**Why:** Every relationship edge carries meaning. You can reason about the graph:
- "Which concepts does Maria understand well?" → `UNDERSTANDS {mastery_level > 0.75}`
- "Which exercises test the subjunctive mood?" → `exer-[:REQUIRES]->concept`

### ✅ DO: Create Nodes for Atomic Facts

**Good:**
```cypher
CREATE (s:Session) // Represents one study session
CREATE (a:Attempt) // Represents one exercise attempt
CREATE (exp:Experience) // Represents one XP award
CREATE (perf:Performance) // Represents metrics for one attempt
```

**Avoid:**
```cypher
// BAD: Storing all attempts as array property
SET student.all_attempts = [{...}, {...}, {...}]
```

**Why:**
- Each attempt is queryable independently
- Relationships between attempts (attempts in a session) are explicit
- Temporal ordering via `created_at` is natural
- Analytics queries are efficient

### ✅ DO: Use CEFR Levels as Semantic Boundaries

**Good:**
```cypher
MATCH (a1:CEFRLevel {code: 'A1'})
MATCH (a1)-[:REQUIRES]->(mod:Module)  // A1 entry modules
MATCH (mod)-[:TEACHES]->(concept:Concept)
MATCH (concept)-[:EXEMPLIFIED_BY]->(vocab:Vocabulary)
```

**Why:**
- Levels are semantic milestones, not arbitrary thresholds
- Makes curriculum scaffolding explicit
- Supports competency-based progression

### ✅ DO: Link Content to Multiple Skills

**Good:**
```cypher
MATCH (template:ExerciseTemplate)-[:ASSESSES]->(skill:Skill)
WITH template, collect(skill.skill_id) AS skills
// where skills = ['grammar', 'vocabulary', 'reading']
```

**Why:**
- Real exercises are multi-faceted (reading comprehension requires both vocabulary and grammar)
- Skill breakdown in Performance metrics makes sense
- Supports fine-grained analytics

---

## 2. Query Patterns

### Pattern 1: Personalized Module Recommendations

```cypher
-- "What should Maria learn next?"
MATCH (s:Student {student_id: 'maria_doe_001'})-[:ACHIEVED]->(level:CEFRLevel)
MATCH (level)-[:REQUIRES]->(m:Module)
WHERE NOT (s)-[:COMPLETED]->(m) AND NOT (s)-[:WORKING_ON]->(m)
MATCH (m)-[:CONTAINS]->(topic:Topic)
OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)-[:BELONGS_TO]->(topic)
WITH m, count(DISTINCT v) AS vocab_known, m.vocabulary_count AS vocab_total
RETURN m.module_id, m.title, m.estimated_hours,
       ROUND(100.0 * vocab_known / vocab_total) AS vocab_coverage_pct
ORDER BY vocab_coverage_pct DESC
LIMIT 5
```

**Use case:** Adaptive learning pathway

---

### Pattern 2: Identify Knowledge Gaps

```cypher
-- "Which concepts is Maria struggling with?"
MATCH (s:Student {student_id: 'maria_doe_001'})-[r:UNDERSTANDS]->(c:Concept)
WHERE r.mastery_level < 0.6
MATCH (c)<-[:RELATED_TO]-(e:GrammarError)-[:MADE_BY]->(s)
RETURN c.concept_id, c.title, r.mastery_level, count(DISTINCT e) AS error_count
ORDER BY r.mastery_level ASC, error_count DESC
LIMIT 10
```

**Use case:** Targeted remediation

---

### Pattern 3: Spaced Repetition Queue

```cypher
-- "Which words should Maria review today?"
MATCH (s:Student {student_id: 'maria_doe_001'})-[:KNOWS]->(vc:VocabConfidence)
WHERE vc.next_review <= datetime()
OPTIONAL MATCH (v:Vocabulary {word: vc.word})
OPTIONAL MATCH (s)-[:MADE_ERROR]->(e:GrammarError)-[:RELATED_TO]->(c:Concept),
       (v)-[:EXPRESSES]->(c)
WITH vc, v, count(DISTINCT e) AS error_count
RETURN v.word, v.translation, v.part_of_speech,
       vc.ease_factor, vc.interval_days, vc.confidence_score,
       error_count
ORDER BY error_count DESC, vc.last_seen ASC
LIMIT 10
```

**Use case:** SM-2 spaced repetition

---

### Pattern 4: Learning Velocity & Progress

```cypher
-- "How is Maria progressing? XP earned/hour this week per skill?"
MATCH (s:Student {student_id: 'maria_doe_001'})-[:ENROLLED_IN]->(sess:Session)
WHERE sess.started_at > datetime() - duration('P7D')
MATCH (sess)-[:CONTAINS]->(a:Attempt)
MATCH (a)-[:GAINS]->(exp:Experience)-[:TOWARDS_SKILL]->(skill:Skill)
WITH skill.skill_id AS skill_id,
     sum(exp.amount) AS total_xp,
     sum(sess.duration_minutes) AS total_minutes
WHERE total_minutes > 0
RETURN skill_id, total_xp,
       ROUND((total_xp * 60.0) / total_minutes, 2) AS xp_per_hour,
       ROUND(total_minutes / 60.0, 1) AS hours_studied
ORDER BY xp_per_hour DESC
```

**Use case:** Dashboard KPIs

---

### Pattern 5: Curriculum Sequencing

```cypher
-- "What's the dependency graph for B1 level? (prerequisites)"
MATCH (b1:CEFRLevel {code: 'B1'})
MATCH p=shortestPath((b1)-[:REQUIRES*1..5]->(m:Module))
WITH nodes(p) AS path_nodes
UNWIND path_nodes AS node
WITH node,
     CASE labels(node)[0]
       WHEN 'CEFRLevel' THEN node.code
       WHEN 'Module' THEN node.module_id
       ELSE null
     END AS id,
     CASE labels(node)[0]
       WHEN 'CEFRLevel' THEN node.title
       WHEN 'Module' THEN node.title
       ELSE null
     END AS title
RETURN id, title, labels(node)[0] AS type
```

**Use case:** Curriculum design & prerequisite tracking

---

### Pattern 6: Semantic Concept Relationships

```cypher
-- "Concepts related to 'subjunctive mood' + their example vocabulary"
MATCH (c1:Concept {concept_id: 'subjunctive_mood'})
MATCH (c1)-[:RELATED_TO|GENERALIZES*1..2]->(related:Concept)
MATCH (related)<-[:EXPRESSES]-(v:Vocabulary)
OPTIONAL MATCH (err:GrammarError)-[:RELATED_TO]->(related)
RETURN related.concept_id, related.title, related.difficulty_level,
       collect(DISTINCT v.word) AS example_words,
       collect(DISTINCT err.original_example) AS common_mistakes
```

**Use case:** Related content discovery

---

### Pattern 7: Attempt-Level Analytics

```cypher
-- "Maria's session today: detailed attempt breakdown"
MATCH (s:Student {student_id: 'maria_doe_001'})-[:ENROLLED_IN]->(sess:Session)
WHERE DATE(sess.started_at) = DATE()
MATCH (sess)-[:CONTAINS]->(a:Attempt)
MATCH (a)-[:RESULT]->(p:Performance)
OPTIONAL MATCH (a)-[:ON_VOCABULARY]->(v:Vocabulary)
OPTIONAL MATCH (a)-[:TESTS_CONCEPT]->(c:Concept)
RETURN a.exercise_type, a.is_correct, a.score, a.xp_earned,
       a.duration_seconds, a.response_time_ms, a.confidence,
       v.word, c.concept_id,
       a.completed_at
ORDER BY a.completed_at ASC
```

**Use case:** Session review, real-time dashboards

---

## 3. Performance Optimization

### Index Strategy

```cypher
-- Essential indexes for common queries
CREATE INDEX student_id_idx FOR (s:Student) ON (s.student_id);
CREATE INDEX session_student_idx FOR (s:Session) ON (s.student_id);
CREATE INDEX session_id_idx FOR (s:Session) ON (s.session_id);
CREATE INDEX attempt_session_idx FOR (a:Attempt) ON (a.session_id);
CREATE INDEX vocab_level_idx FOR (v:Vocabulary) ON (v.difficulty_level);
CREATE INDEX concept_level_idx FOR (c:Concept) ON (c.difficulty_level);
CREATE INDEX vocab_conf_review_idx FOR (vc:VocabConfidence) ON (vc.next_review);
CREATE INDEX module_level_idx FOR (m:Module) ON (m.level);
```

### Caching Nodes vs. Computing Aggregates

**Good for caching on nodes:**
```cypher
-- Recompute after session ends
MATCH (s:Session {session_id: $id})
SET s.total_xp_earned = (
  MATCH (s)-[:CONTAINS]->(a:Attempt) RETURN sum(a.xp_earned)
),
    s.exercise_count = (
  MATCH (s)-[:CONTAINS]->(a:Attempt) RETURN count(a)
)
```

**Good for on-the-fly computation:**
```cypher
-- Query via relationships when data changes frequently
MATCH (s:Student {student_id: $id})-[:ENROLLED_IN]->(sess:Session)
WITH sum(sess.duration_minutes) AS total_minutes
RETURN total_minutes / 60.0 AS total_hours
```

---

## 4. Spaced Repetition Integration (SM-2)

### SM-2 Algorithm in Python

After each review, compute:
```python
def update_sm2(correct, ease_factor, interval):
    """SM-2 spaced repetition algorithm."""
    # Easiness Factor
    ef = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    # Next interval
    if correct:
        if interval == 0:
            interval = 1
        elif interval == 1:
            interval = 3
        else:
            interval = round(interval * ef)
    else:
        interval = 1

    return ef, interval
```

### Update Neo4j After Review

```cypher
MATCH (s:Student {student_id: $id})-[:KNOWS]->(vc:VocabConfidence {word: $word})
SET vc.ease_factor = $new_ef,
    vc.interval_days = $new_interval,
    vc.next_review = datetime() + duration({days: $new_interval}),
    vc.last_seen = datetime(),
    vc.review_count = vc.review_count + 1,
    vc.correct_count = CASE WHEN $correct THEN vc.correct_count + 1 ELSE vc.correct_count END
```

---

## 5. Analytics Dashboards

### KPI: Weekly Learning Velocity

```cypher
-- Total XP, hours, exercises per week
MATCH (s:Student {student_id: $id})-[:ENROLLED_IN]->(sess:Session)
WHERE sess.started_at > datetime() - duration('P7D')
RETURN DATE(sess.started_at) AS day,
       count(DISTINCT sess.session_id) AS sessions,
       sum(sess.total_xp_earned) AS xp,
       sum(sess.duration_minutes) AS minutes,
       sum(sess.exercise_count) AS exercises
ORDER BY day DESC
```

### KPI: Skill Breakdown

```cypher
-- XP per skill
MATCH (s:Student {student_id: $id})-[:GAINS]->(exp:Experience)-[:TOWARDS_SKILL]->(skill:Skill)
RETURN skill.skill_id AS skill, sum(exp.amount) AS total_xp
ORDER BY total_xp DESC
```

### KPI: Retention Curve

```cypher
-- Vocabulary confidence distribution (retention curve)
MATCH (s:Student {student_id: $id})-[:KNOWS]->(vc:VocabConfidence)
RETURN
  apoc.math.round(vc.confidence_score * 10) / 10 AS confidence_band,
  count(DISTINCT vc.word) AS vocab_count,
  avg(vc.ease_factor) AS avg_ease
ORDER BY confidence_band DESC
```

---

## 6. Data Migration Strategy

### Phase 1: Back-Filling Existing Data

If migrating from old schema:

```cypher
-- Migrate Exercise nodes to Attempt nodes
MATCH (s:Student)-[:COMPLETED]->(e:Exercise)
CREATE (a:Attempt {
  attempt_id: randomUUID(),
  exercise_type: CASE e.type
    WHEN 'vocab' THEN 'flashcard'
    WHEN 'grammar' THEN 'multiple_choice'
    ELSE e.type
  END,
  score: e.score,
  is_correct: e.score >= 0.7,
  xp_earned: ROUND(e.score * 50),
  completed_at: e.completed_at
})
MERGE (s)<-[:CONTAINS]-(sess:Session)
CREATE (sess)-[:CONTAINS]->(a)
```

### Phase 2: Concurrent Dual-Write

Keep old schema updated while writing to new:
```python
# In application layer during transition period
await neo4j_client.record_exercise_attempt(...)  # New
await neo4j_client.record_exercise(...)  # Old (legacy)
```

### Phase 3: Validate & Sunset

```cypher
-- Verify counts match between old and new schema
MATCH (s:Student)-[:COMPLETED]->(e:Exercise)
WITH count(e) AS old_count
MATCH (s2:Student)-[:ENROLLED_IN]->()-[:CONTAINS]->(a:Attempt)
WITH old_count, count(a) AS new_count
RETURN old_count, new_count, old_count - new_count AS difference
```

---

## 7. Common Pitfalls & Solutions

### ❌ Pitfall: Denormalized Properties

```cypher
// BAD: Storing list of words on student
SET student.known_words = ['ciao', 'grazie', ...]
SET student.error_patterns = [{...}, {...}, ...]
```

**Problem:** Can't query "words known at A2 level" without loading entire student

**Solution:** Create nodes instead
```cypher
CREATE (s:Student)-[:KNOWS]->(vc:VocabConfidence)
// Now can query: MATCH (...)-[:KNOWS]->(vc) WHERE vc.next_review < now()
```

### ❌ Pitfall: Duplicate Nodes

```cypher
// BAD: Creating duplicate Vocabulary nodes
CREATE (v:Vocabulary {word: 'ciao'})  // First time
CREATE (v:Vocabulary {word: 'ciao'})  // Second time (creates another!)
```

**Solution:** Use MERGE
```cypher
MERGE (v:Vocabulary {word: 'ciao', language: 'italian'})
SET v.translation = 'hello'
```

### ❌ Pitfall: Over-Parameterization

```cypher
// BAD: Multiple joins for same entity
MATCH (s:Student {student_id: $id})
MATCH (s)-[:ACHIEVED]->(level:CEFRLevel)
MATCH (level)-[:REQUIRES]->(m:Module)
// ... 5 more MATCHES

// GOOD: Batch with WITH
MATCH (s:Student {student_id: $id})-[:ACHIEVED]->(level)-[:REQUIRES]->(m)
MATCH (m)-[:CONTAINS]->(topic)-[:CONTAINS]->(vocab)
// Much more efficient
```

---

## 8. Migrations & Schema Changes

### Adding a New Concept

```cypher
-- Step 1: Create concept
CREATE (c:Concept {
  concept_id: 'reflexive_pronouns',
  title: 'Reflexive Pronouns (mi, ti, si, ci, vi)',
  difficulty_level: 'A2',
  explanation_md: '...'
})

-- Step 2: Link to modules that teach it
MATCH (c:Concept {concept_id: 'reflexive_pronouns'})
MATCH (m:Module {module_id: 'a2_verbs_advanced'})
CREATE (m)-[:TEACHES]->(c)

-- Step 3: Link to example vocabulary
MATCH (c:Concept {concept_id: 'reflexive_pronouns'})
MATCH (v:Vocabulary {word: 'alzarsi'})  // "to get up"
CREATE (v)-[:EXPRESSES]->(c)

-- Step 4: Update exercise templates to require it
MATCH (t:ExerciseTemplate {template_id: 'translation_reflexive'})
MATCH (c:Concept {concept_id: 'reflexive_pronouns'})
CREATE (t)-[:REQUIRES]->(c)

-- Step 5: Tag existing errors with it
MATCH (e:GrammarError {pattern: 'incorrect_reflexive_form'})
MATCH (c:Concept {concept_id: 'reflexive_pronouns'})
CREATE (e)-[:RELATED_TO]->(c)
```

---

## 9. Real-Time Dashboards

### Performance Tracking

```python
# Python async code to update KPIs every 30 seconds

async def update_student_dashboard_kpis(student_id: str):
    """Refresh dashboard metrics."""
    client = Neo4jClient()

    stats = await client.get_student_stats(student_id)
    skills = await client.get_skill_breakdown(student_id)
    velocity = await client.get_learning_velocity(student_id, days=1)

    dashboard = {
        'total_exercises': stats['total_exercises'],
        'avg_score': stats['avg_score'],
        'streak_days': stats['streak_days'],
        'xp_this_week': stats['xp_this_week'],
        'skills': skills,
        'velocity': velocity.get('xp_per_hour', 0)
    }

    # Publish to frontend via WebSocket
    await websocket.send(json.dumps(dashboard))
```

---

## 10. Testing Queries

### Test Framework

```python
import pytest
from italianollama.memory.neo4j_client_enhanced import Neo4jClient

@pytest.mark.asyncio
async def test_vocab_confidence_updates():
    """Verify SM-2 updates work correctly."""
    client = Neo4jClient(database="test_db")
    await client.connect()

    # Setup
    await client.create_student("test_student", "Test")
    await client.add_vocabulary("test_student", "ciao", "hello")

    # Update with correct answer
    await client.update_vocabulary_confidence(
        "test_student", "ciao", is_correct=True,
        ease_factor=2.5, interval_days=1
    )

    # Verify
    vocabs = await client.get_student_vocabulary("test_student")
    assert vocabs[0]['confidence_score'] > 0
    assert vocabs[0]['ease_factor'] == 2.5

    await client.close()
```

---

## Conclusion

This semantic knowledge graph model enables:
✅ **Accurate personalization** through explicit skill/concept tracking
✅ **Research-grade analytics** with fine-grained attempt-level data
✅ **Scalable curricula** as explicit directed graphs
✅ **Spaced repetition** with SM-2 algorithm integration
✅ **Real-time dashboards** via efficient relationship queries
✅ **Adaptive learning paths** based on mastery and gaps
