# Backend Architecture

The backend is built on FastAPI and LangGraph, providing a unified API for both frontend services.

## Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Chainlit   │────▶│   FastAPI   │────▶│  LangGraph  │
│  Streamlit  │     │  Backend    │     │  Workflow   │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   Neo4j     │     │   LiteLLM   │
                    │  (Memory)   │     │    (LLM)    │
                    └─────────────┘     └─────────────┘
```

## FastAPI Backend

### Entry Point

**Location:** `src/italianollama/api/main.py`

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check (Neo4j, LiteLLM) |
| `/v1/chat/completions` | POST | OpenAI-compatible chat |
| `/chat` | POST | Simple chat with student_id |
| `/students` | POST | Create student |
| `/students/{id}` | GET | Get student info & progress |

### OpenAI-Compatible API

The `/v1/chat/completions` endpoint follows OpenAI's API spec:

```python
# Request
{
  "model": "tutor",
  "messages": [
    {"role": "system", "content": "You are Sofia, an Italian tutor..."},
    {"role": "user", "content": "Ciao! Voglio imparare l'italiano."}
  ],
  "stream": true
}

# Response (SSE)
data: {"choices": [{"delta": {"content": "Ciao!"}}]}
data: {"choices": [{"delta": {"content": " Benvenuto"}}]}
data: [DONE]
```

## LangGraph Workflow

### Graph Structure

```
┌─────────────┐
│   router    │ ← Entry point - determines next node
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌────────┐ │
│  │placement │  │vocabulary │  │ grammar │  │  chat  │ │
│  │  (CEFR)  │  │(flashcard)│  │ (drills)│  │ (free) │ │
│  └────┬─────┘  └─────┬─────┘  └────┬────┘  └────┬───┘ │
│       │              │             │            │     │
│       └──────────────┴─────────────┴────────────┘     │
│                         │                              │
└─────────────────────────┼──────────────────────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │   router    │ ← Loops back
                    └─────────────┘
```

### State Management

**Location:** `src/italianollama/graph/state.py`

```python
class TutorState(TypedDict):
    student_id: str
    messages: list[ChatMessage]
    current_exercise: str
    cefr_level: str
    vocabulary: list[VocabularyItem]
    grammar_errors: list[GrammarError]
    exercise_scores: dict[str, int]
```

### Nodes

| Node | Exercise Type | Description |
|------|---------------|-------------|
| `placement` | CEFR Test | Assess student's Italian level (A1-C2) |
| `vocabulary` | Flashcards | Spaced repetition vocabulary practice |
| `grammar` | Drills | Grammar error detection & correction |
| `translation` | Practice | Italian↔English translation |
| `free_writing` | Writing | Open prompts with AI feedback |
| `niveau_test` | Exam Prep | TELC/Goethe style tests |

### Router Node

The router determines which exercise node to execute based on:
- Student input keywords
- Current exercise type
- Time since last exercise
- Spaced repetition schedule

```python
def route_next(state: TutorState) -> str:
    last_message = state["messages"][-1]["content"].lower()
    
    if any(word in last_message for word in ["test", "livello", "cefr"]):
        return "placement"
    if any(word in last_message for word in ["vocab", "flashcard"]):
        return "vocabulary"
    if any(word in last_message for word in ["grammar", "grammatica"]):
        return "grammar"
    # ... etc
    return "chat"
```

## LiteLLM Integration

### Unified Interface

LiteLLM provides a unified interface to multiple LLM providers:

**Location:** `src/italianollama/graph/nodes/base.py`

```python
from litellm import completion

class LLMClient:
    def __init__(self, model: str = "tutor"):
        self.model = model
    
    def chat(self, messages: list[dict], stream: bool = True):
        return completion(
            model=self.model,
            messages=messages,
            stream=stream
        )
```

### Configuration

**Location:** `backend/litellm/litellm_config.yaml`

```yaml
model_list:
  - model_name: tutor
    litellm_params:
      model: openai/fake
      api_base: os.environ/BLABLADOR_API_URL
      api_key: os.environ/BLABLADOR_API_KEY
```

## Neo4j Client

### CRUD Operations

**Location:** `src/italianollama/memory/neo4j_client.py`

```python
class Neo4jClient:
    def create_student(self, name: str, email: str) -> Student
    def get_student(self, student_id: str) -> Student
    def update_progress(self, student_id: str, exercise: dict)
    def add_vocabulary(self, student_id: str, vocab: VocabularyItem)
    def record_grammar_error(self, student_id: str, error: GrammarError)
```

### Queries

```cypher
# Get student with progress
MATCH (s:Student {student_id: $id})
OPTIONAL MATCH (s)-[:HAS_LEVEL]->(l:CEFRLevel)
OPTIONAL MATCH (s)-[:KNOWS]->(v:Vocabulary)
RETURN s, l, collect(v) as vocabulary

# Update vocabulary confidence
MATCH (s:Student)-[:KNOWS]->(v:Vocabulary {word: $word})
SET v.confidence = $new_confidence
```

## CLI Commands

### Available Commands

```bash
# Start the API server
python -m src.italianollama.api

# CLI tools
python cli.py --help
python cli.py student create --name "John" --email "john@example.com"
python cli.py student list
python cli.py student get <student_id>
```

## Related Documentation

- [API Endpoints](../api/endpoints.md)
- [Database Schema](database.md)
- [LLM Providers](llm-providers.md)
- [LangGraph Workflow](../features/exercises.md)
