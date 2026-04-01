# Improved Semantic Data Model for Italian Tutor

## Overview
This document outlines an enhanced, semantically-rich data model for the Italian learning platform built on Neo4j. The model follows best practices for educational knowledge graphs and learning analytics.

## Design Principles

### 1. **Semantic Richness**
- Every relationship has meaningful semantics (e.g., `:TESTS`, `:PREREQUISITE_FOR`, `:BELONGS_TO`)
- Entities are first-class objects (not just properties on Student)
- Enables complex queries and reasoning about learning paths

### 2. **Temporal Awareness**
- Sessions, Attempts, and Performance records track changes over time
- Enables analytics on learning velocity, improvement trends, retention curves
- Supports spaced repetition algorithms

### 3. **Skill Taxonomy**
- Separate Skill nodes (speaking, writing, listening, reading, grammar, vocabulary)
- Exercises tagged with skill alignment and proficiency requirements
- Students gain experience points in each skill independently

### 4. **Learning Paths**
- CEFR levels as first-class entities with specific requirements
- Prerequisites and learning dependencies explicit
- Modules/Topics organize content into coherent units

### 5. **Detailed Analytics**
- Attempt/Performance nodes store fine-grained metrics
- Composite KPIs derived from atomic measurements
- Supports both real-time dashboards and retrospective analysis

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          STUDENT HUB                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Student                                                         │
│    ├─→ [:ENROLLED_IN] → Session (active session)               │
│    ├─→ [:ACHIEVED] → CEFRLevel (current level: A1-C2)          │
│    ├─→ [:WORKING_ON] → Module (current module)                 │
│    ├─→ [:COMPLETED] → Module (completed modules)               │
│    ├─→ [:KNOWS] → Vocabulary (learned words)                   │
│    ├─→ [:UNDERSTANDS] → Concept (grammar/linguistic concepts)  │
│    ├─→ [:EXPERIENCED] → Skill (reading, writing, etc.)         │
│    ├─→ [:MADE_ATTEMPT] → Attempt (exercise history)            │
│    ├─→ [:HAS_PERFORMANCE] → Performance (KPI aggregates)       │
│    └─→ [:ACTIVE: true] → User (optional user profile)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CURRICULUM STRUCTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CEFRLevel (A1, A2, B1, B2, C1, C2)                            │
│    ├─→ [:REQUIRES] → Module (entry-level modules)              │
│    └─→ [:UNLOCKS] → CEFRLevel (next level)                     │
│                                                                  │
│  Module (e.g., "Greetings & Introduction")                     │
│    ├─→ [:PREREQUISITE_FOR] → Module                            │
│    ├─→ [:PART_OF] → CEFRLevel                                  │
│    ├─→ [:CONTAINS] → Topic                                     │
│    ├─→ [:USES_SKILL] → Skill (required skills)                 │
│    ├─→ [:TEACHES] → Concept                                    │
│    └─→ [:EMPLOYS] → ExerciseTemplate                           │
│                                                                  │
│  Topic (e.g., "Food & Dining vocabulary")                      │
│    ├─→ [:PART_OF] → Module                                     │
│    ├─→ [:CONTAINS] → Vocabulary                                │
│    └─→ [:COVERS] → Concept                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE ENTITIES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Vocabulary (word lemma)                                         │
│    ├─→ [:SYNONYM_OF] → Vocabulary                              │
│    ├─→ [:ANTONYM_OF] → Vocabulary                              │
│    ├─→ [:IS_FORM_OF] → Vocabulary (verb conjugations, etc.)    │
│    ├─→ [:BELONGS_TO] → Topic                                   │
│    ├─→ [:TAUGHT_AT] → CEFRLevel                                │
│    └─→ [:EXPRESSES] → Concept                                  │
│                                                                  │
│  Concept (grammar rule, linguistic concept)                     │
│    ├─→ [:GENERALIZES] → Concept (taxonomy)                     │
│    ├─→ [:RELATED_TO] → Concept                                 │
│    ├─→ [:EXEMPLIFIED_BY] → Vocabulary                          │
│    ├─→ [:TAUGHT_IN] → Module                                   │
│    └─→ [:REQUIRED_FOR] → CEFRLevel                             │
│                                                                  │
│  Skill (reading, writing, listening, speaking, etc.)           │
│    ├─→ [:COMPOSED_OF] → Skill (sub-skills)                    │
│    └─→ [:ASSESSED_BY] → ExerciseTemplate                       │
│                                                                  │
│  ExerciseTemplate (flashcard, MC, translation, etc.)           │
│    ├─→ [:ASSESSES] → Skill                                     │
│    ├─→ [:REQUIRES] → Concept                                   │
│    ├─→ [:USES] → Vocabulary                                    │
│    ├─→ [:TESTS_LEVEL] → CEFRLevel                              │
│    └─→ [:PART_OF] → Module                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE TRACKING                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Session (study session)                                        │
│    ├─→ [:FOR_STUDENT] → Student                                │
│    ├─→ [:IN_MODULE] → Module (optional, context)               │
│    └─→ [:CONTAINS] → Attempt (multiple attempts in session)    │
│                                                                  │
│  Attempt (single exercise attempt)                              │
│    ├─→ [:PART_OF] → Session                                    │
│    ├─→ [:USES_TEMPLATE] → ExerciseTemplate                     │
│    ├─→ [:ON_VOCABULARY] → Vocabulary (if vocab exercise)       │
│    ├─→ [:TESTS_CONCEPT] → Concept (if grammar exercise)        │
│    ├─→ [:GAINS] → Experience (XP gained)                       │
│    └─→ [:RESULT] → Performance                                 │
│                                                                  │
│  Performance (aggregate metrics for an attempt)                 │
│    ├─→ [:FOR_ATTEMPT] → Attempt                                │
│    ├─→ [:IMPACTS_SKILL] → Skill (updates skill XP)            │
│    └─→ [:IMPACTS_VOCAB] → Vocabulary (updates confidence)      │
│                                                                  │
│  Experience (earned XP)                                         │
│    ├─→ [:FROM_ATTEMPT] → Attempt                               │
│    ├─→ [:TOWARDS_SKILL] → Skill                                │
│    └─→ [:AT_TIME] → datetime                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    VOCABULARY METADATA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  VocabConfidence (student-specific vocab state)                 │
│    ├─→ [:FOR_STUDENT] → Student                                │
│    ├─→ [:OF_WORD] → Vocabulary                                 │
│    ├─→ [:LAST_SEEN] → datetime                                 │
│    ├─→ [:INTERVAL] → spaced repetition interval (days)         │
│    └─→ [:EASE_FACTOR] → SM-2 algorithm ease factor             │
│                                                                  │
│  GrammarError (mistake pattern)                                 │
│    ├─→ [:MADE_BY] → Student                                    │
│    ├─→ [:RELATED_TO] → Concept                                 │
│    ├─→ [:AT_LEVEL] → CEFRLevel                                 │
│    └─→ [:IN_CONTEXT] → ExerciseTemplate                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Node Types & Properties

### Core Entities

#### Student
```yaml
label: Student
unique_id: student_id
properties:
  student_id: string (unique)
  name: string
  email: string (optional)
  created_at: datetime
  last_active: datetime
  native_language: string (e.g., "English", "German")
  learning_goal: string (optional, e.g., "business", "travel", "certification")
  total_xp: integer (cached aggregate)
  current_streak: integer (days)
  preferred_exercise_type: string (optional)
  notes: string (optional tutor notes)
```

#### Session
```yaml
label: Session
unique_id: (student_id, started_at)
properties:
  session_id: string (uuid)
  student_id: string (reference)
  started_at: datetime
  ended_at: datetime (null if ongoing)
  duration_minutes: integer
  total_xp_earned: integer
  exercise_count: integer
  module_context: string (optional, which module they were working on)
  device: string (optional, "web", "mobile")
```

#### Attempt
```yaml
label: Attempt
unique_id: (session_id, attempt_seq)
properties:
  attempt_id: string (uuid)
  session_id: string (reference)
  exercise_type: enum [flashcard, multiple_choice, translation, free_writing, listening, speaking]
  started_at: datetime
  completed_at: datetime
  duration_seconds: integer
  response_time_ms: integer (time to first response)
  is_correct: boolean
  confidence: float [0.0-1.0] (student's self-assessed confidence)
  score: float [0.0-1.0] (automated or manual scoring)
  xp_earned: integer
  hints_used: integer
  retries: integer (attempts before success)
  feedback: string (AI-generated or template feedback)
```

#### Performance
```yaml
label: Performance
unique_id: (attempt_id)
properties:
  performance_id: string (uuid)
  attempt_id: string (reference)
  skill_breakdown: {reading: 0.85, writing: 0.70, grammar: 0.90}
  difficulty_rating: float [1.0-5.0] (perceived difficulty)
  engagement_score: float [0.0-1.0] (from response confidence + time spent)
  learning_gain: float [0.0-1.0] (estimated improvement from this attempt)
  concept_coverage: [list of concept_ids tested]
  timestamp: datetime
```

#### Module
```yaml
label: Module
unique_id: module_id
properties:
  module_id: string (e.g., "a1_greetings", "b1_business")
  title: string (human-readable name)
  description: string
  level: enum [A1, A2, B1, B2, C1, C2]
  learning_objectives: [list of strings]
  estimated_hours: float
  vocabulary_count: integer (metadata)
  exercise_count: integer (metadata)
  created_at: datetime
  last_updated: datetime
```

#### Topic
```yaml
label: Topic
unique_id: topic_id
properties:
  topic_id: string (e.g., "food_dining", "business_email")
  title: string
  description: string
  vocabulary_count: integer
  icon_url: string (optional)
  difficulty_hint: string (optional)
```

#### CEFRLevel
```yaml
label: CEFRLevel
unique_id: code
properties:
  code: enum [A1, A2, B1, B2, C1, C2]
  title: string (e.g., "Elementary")
  description: string
  vocab_range: integer (e.g., "500-1000 words")
  grammar_focus: [list of concepts]
  assessment_score_passing: float [0.7-0.9] (threshold to pass)
  typical_hours: integer (hours to reach from previous level)
```

#### Vocabulary
```yaml
label: Vocabulary
unique_id: (word, language)
properties:
  word: string (lemma form in Italian)
  language: enum ["italian"]
  translation: string (English)
  part_of_speech: enum [noun, verb, adjective, adverb, preposition, pronoun, article, conjunction]
  gender: enum [m, f, n] (for Italian nouns)
  plural_form: string (if noun)
  conjugations: map[tense -> form] (if verb)
  example_sentence_italian: string
  example_sentence_english: string
  etymology: string (optional, "from Latin...")
  difficulty_level: enum [A1, A2, B1, B2, C1, C2]
  frequency_rank: integer (1=most common in Italian)
  tags: [list of tags, e.g., "food", "informal", "slang"]
  ipa_pronunciation: string (e.g., /ˈtʃaːo/)
  created_at: datetime
  confidence_decays_after_days: integer (spaced repetition window)
  related_domain: string (semantic domain, e.g., "restaurant", "family")
```

#### Concept (Grammar/Linguistic)
```yaml
label: Concept
unique_id: concept_id
properties:
  concept_id: string (e.g., "present_perfect_tense", "subjunctive_mood")
  title: string (human-readable)
  description: string (detailed explanation)
  grammar_category: enum [tense, mood, aspect, voice, gender, number, case, etc.]
  difficulty_level: enum [A1, A2, B1, B2, C1, C2]
  explanation_md: string (markdown with examples)
  common_mistakes: [list of strings]
  min_vocab_requirement: integer (approx. words needed to practice)
  uses_vocabulary: [list of vocab_ids] (common words using this concept)
  prerequisites_concepts: [list of concept_ids] (must learn before)
  created_at: datetime
```

#### Skill
```yaml
label: Skill
unique_id: skill_id
properties:
  skill_id: enum [reading, writing, listening, speaking, grammar, vocabulary, pronunciation, listening_comprehension, verbal_fluency, written_clarity]
  title: string
  description: string
  parent_skill: string (optional, for sub-skills)
  xp_required_per_level: integer (to reach next CEFR level)
  assessment_exercise_types: [list of exercise types that test this]
```

#### ExerciseTemplate
```yaml
label: ExerciseTemplate
unique_id: template_id
properties:
  template_id: string (e.g., "vocab_flashcard_basic", "grammar_mc_conditional")
  title: string
  description: string
  exercise_type: enum [flashcard, multiple_choice, translation, free_writing, listening, speaking, cloze, arrangement]
  difficulty_level: enum [A1, A2, B1, B2, C1, C2]
  estimated_time_seconds: integer
  instructions: string
  success_criteria: string (e.g., ">0.8 accuracy")
  skills_assessed: [skill_ids]
  concepts_required: [concept_ids]
  vocabulary_range: {min_level: "A1", max_level: "B1"}
```

#### GrammarError
```yaml
label: GrammarError
unique_id: error_id
properties:
  error_id: string (uuid)
  pattern: string (regex or description, e.g., "incorrect past participle agreement")
  original_example: string (user's error)
  corrected_example: string (fix)
  explanation: string (why it's wrong)
  related_concept: concept_id
  frequency: integer (count of this mistake by all students)
  severity: enum [minor, moderate, major] (impact on comprehension)
  level: enum [A1, A2, B1, B2, C1, C2]
```

#### VocabConfidence
```yaml
label: VocabConfidence
unique_id: (student_id, word)
properties:
  student_id: string
  word: string
  confidence_score: float [0.0-1.0]
  last_seen: datetime
  next_review: datetime (spaced repetition)
  review_count: integer
  correct_count: integer
  incorrect_count: integer
  ease_factor: float (SM-2 algorithm: 1.3-2.5)
  interval_days: integer (SM-2 interval before next review)
  tags: string (e.g., "active", "mature", "forgotten", "new")
```

---

## Relationship Types & Semantics

### Student Learning Path
| Relationship | From | To | Properties | Semantics |
|---|---|---|---|---|
| `:ENROLLED_IN` | Student | Session | `joined_at`, `is_active` | Student is currently in or was in this session |
| `:ACHIEVED` | Student | CEFRLevel | `confirmed_at`, `confidence` | Student has demonstrated mastery of this level |
| `:WORKING_ON` | Student | Module | `started_at`, `progress_percent` | Currently studying this module |
| `:COMPLETED` | Student | Module | `completed_at`, `score` | Finished this module |
| `:KNOWS` | Student | Vocabulary | `since`, `confidence` | Can use/recognize this word |
| `:UNDERSTANDS` | Student | Concept | `since`, `mastery_level` | Grasps this grammar/linguistic concept |
| `:MADE_ATTEMPT` | Student | Attempt | `order_in_session` | Performed this exercise attempt |
| `:MADE_ERROR` | Student | GrammarError | `count`, `last_occurrence` | This student made this type of error |

### Curriculum & Content
| Relationship | From | To | Properties | Semantics |
|---|---|---|---|---|
| `:PART_OF` | Module/Topic | CEFRLevel/Module | `sequence`, `weight` | Belongs to parent container |
| `:PREREQUISITE_FOR` | Module | Module | `required`, `min_score` | Must complete this first |
| `:CONTAINS` | Module/ExerciseTemplate | Topic/Vocabulary | `order` | Contains these elements |
| `:TAUGHT_AT` | Vocabulary/Concept | CEFRLevel | `is_focus` | First introduced at this level |
| `:USES_SKILL` | Module | Skill | `emphasis` | Requires this skill |
| `:TEACHES` | Module | Concept | `primary` | Covers this concept |
| `:EMPLOYS` | Module | ExerciseTemplate | `sequence`, `required` | Uses this exercise template |

### Knowledge Graph
| Relationship | From | To | Properties | Semantics |
|---|---|---|---|---|
| `:SYNONYM_OF` | Vocabulary | Vocabulary | null | Same meaning, different word |
| `:ANTONYM_OF` | Vocabulary | Vocabulary | null | Opposite meaning |
| `:IS_FORM_OF` | Vocabulary | Vocabulary | `form_type`: verb form, plural, etc. | Derived form of base word |
| `:EXPRESSES` | Vocabulary | Concept | null | This word demonstrates this concept |
| `:GENERALIZES` | Concept | Concept | null | Concept hierarchy |
| `:RELATED_TO` | Concept | Concept | `relation_type` | Thematically or logically related |
| `:REQUIRES` | ExerciseTemplate | Concept | `min_mastery` | Must understand this concept first |
| `:ASSESSES` | ExerciseTemplate | Skill | `weight` | Tests this skill |

### Performance & Analytics
| Relationship | From | To | Properties | Semantics |
|---|---|---|---|---|
| `:FOR_STUDENT` | Session/VocabConfidence | Student | null | Belongs to this student |
| `:IN_MODULE` | Session | Module | null | Contextualized learning in this module |
| `:CONTAINS` | Session | Attempt | `sequence`, `order` | This session includes these attempts |
| `:PART_OF` | Attempt | Session | null | Belongs to this session |
| `:USES_TEMPLATE` | Attempt | ExerciseTemplate | null | Based on this exercise template |
| `:ON_VOCABULARY` | Attempt | Vocabulary | null | Tests this specific word |
| `:TESTS_CONCEPT` | Attempt | Concept | null | Tests this grammar concept |
| `:RESULT` | Attempt | Performance | null | Has these performance metrics |
| `:IMPACTS_SKILL` | Performance | Skill | `xp_gained`, `improvement` | Updates skill experience |
| `:GAINS` | Attempt | Experience | `amount` | Earned this XP |
| `:TOWARDS_SKILL` | Experience | Skill | null | Contributes to this skill |

---

## Query Patterns

### Student Personalization
```cypher
-- Get student's recommended next module
MATCH (s:Student {student_id: $id})-[:ACHIEVED]->(level:CEFRLevel)
MATCH (level)-[:REQUIRES]->(m:Module)
WHERE NOT (s)-[:COMPLETED]->(m)
RETURN m ORDER BY m.sequence LIMIT 1

-- Get high-error concepts for review
MATCH (s:Student {student_id: $id})-[:MADE_ERROR]->(e:GrammarError)-[:RELATED_TO]->(c:Concept)
RETURN c, count(e) AS error_count
ORDER BY error_count DESC LIMIT 5

-- Get words due for spaced repetition review today
MATCH (s:Student {student_id: $id})-[:KNOWS]->(v:Vocabulary)
MATCH (s)-[:KNOWS]->(vc:VocabConfidence {word: v.word})
WHERE vc.next_review <= datetime()
RETURN v, vc ORDER BY vc.next_review LIMIT 10
```

### Analytics
```cypher
-- Learning velocity: XP earned per hour per skill in last 7 days
MATCH (s:Student {student_id: $id})-[:MADE_ATTEMPT]->(a:Attempt)-[:RESULT]->(p:Performance)-[:IMPACTS_SKILL]->(sk:Skill)
WHERE a.completed_at > datetime() - duration('P7D')
WITH sk, sum(a.xp_earned) AS total_xp, sum(a.duration_seconds) AS total_seconds
RETURN sk.skill_id, total_xp / (total_seconds / 3600.0) AS xp_per_hour

-- Identify struggling concepts (low success rate)
MATCH (s:Student {student_id: $id})-[:MADE_ATTEMPT]->(a:Attempt)-[:TESTS_CONCEPT]->(c:Concept)
WITH c, count(a) AS attempts, apoc.math.sum([a WHERE a.is_correct].is_correct) AS correct
WHERE attempts > 3
RETURN c, correct/attempts AS success_rate ORDER BY success_rate LIMIT 10
```

---

## Migration Path

1. **Phase 1**: Create all new node types (Concept, Skill, ExerciseTemplate, Session, Attempt, Performance)
2. **Phase 2**: Create relationships (Module ↔ Concept, ExerciseTemplate ↔ Skill, etc.)
3. **Phase 3**: Populate demo curriculum (A1 greetings module with vocabs/concepts/exercises)
4. **Phase 4**: Create demo student with complete learning journey (10 exercises, 2-3 sessions)
5. **Phase 5**: Update Python client with new methods (query_recommended_modules, get_struggling_concepts, etc.)

---

## Benefits

✅ **Semantic Clarity**: Every relationship has explicit meaning
✅ **Analytics-Ready**: Performance data structured for dashboards and reports
✅ **Scalable Learning Paths**: Curricula are explicit graphs (not hardcoded)
✅ **Personalization**: Easy contextual queries for student recommendations
✅ **Research-Quality**: Supports educational research and adaptive algorithms
✅ **Compliance**: Detailed auditing of student progress and time spent
