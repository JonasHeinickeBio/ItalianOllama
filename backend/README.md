# Italian Tutor Backend

## Phase 1: Skeleton

This is the Phase 1 implementation of the Italian Tutor with:
- FastAPI backend with LangGraph orchestration
- Neo4j for memory/state (local or Aura)
- LiteLLM for LLM routing (or direct Blablador)
- OpenWebUI for frontend

## Quick Start

### 1. Configure Environment

Create a `.env` file in the project root:

```bash
# Neo4j (Local or Aura)
NEO4J_URI=bolt://neo4j:7687          # Local
# NEO4J_URI=neo4j+s://xxx.databases.neo4j.io  # Aura
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
USE_AURA=false

# LLM - Direct Blablador (recommended for production)
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_blablador_key
BLABLADOR_MODEL=alias-fast

# Or use LiteLLM (local router)
# LITELLM_BASE_URL=http://litellm:4000
# LITELLM_API_KEY=dummy
# LITELLM_MODEL=tutor

# OpenWebUI
WEBUI_SECRET_KEY=your_secret_key
OPENAI_API_KEY=dummy
```

### 2. Start Services

**With Neo4j Aura + Blablador (recommended):**
```bash
docker compose -f docker-compose.yml -f docker-compose.aura.yml up -d
```

**With local Neo4j + Blablador:**
```bash
docker compose up -d
```

### 3. Access

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **OpenWebUI**: http://localhost:3000

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + routes
│   ├── graph/
│   │   ├── state.py         # TutorState TypedDict
│   │   ├── graph.py         # LangGraph builder
│   │   └── nodes/
│   │       ├── base.py      # LLM client
│   │       ├── placement.py # Phase 2: CEFR assessment
│   │       ├── grammar.py   # Phase 3: Grammar exercises
│   │       ├── vocabulary.py
│   │       ├── translation.py
│   │       ├── free_writing.py
│   │       └── niveau_test.py # Phase 4: Exam prep
│   └── memory/
│       └── neo4j_client.py  # Neo4j operations
├── litellm/
│   └── litellm_config.yaml  # LiteLLM routing config
├── docker-compose.yml       # Main compose
├── docker-compose.aura.yml  # Aura override
├── Dockerfile
└── requirements.txt
```

## Phases

### Phase 1: Skeleton (current)
- [x] FastAPI with OpenAI-compatible `/v1/chat/completions`
- [x] LangGraph with basic chat node (Sofia persona)
- [x] Neo4j for student storage

### Phase 2: Placement Test
- [ ] `placement_node` - 10 questions → CEFR level
- [ ] Write `:Student-[:HAS_LEVEL]->:CEFRLevel`

### Phase 3: Exercise Nodes
- [ ] `grammar_node` - verb conjugations, error detection
- [ ] `vocabulary_node` - flashcards, spaced repetition
- [ ] `translation_node` - Italian↔English with scoring
- [ ] `free_writing_node` - open prompts + correction

### Phase 4: Niveau Test Prep
- [ ] `niveau_test_node` - TELC/Goethe-style tests
- [ ] Readiness scoring per skill

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info |
| `GET /health` | Health check |
| `POST /v1/chat/completions` | OpenAI-compatible chat |
| `POST /chat` | Simple chat |
| `POST /students` | Create student |
| `GET /students/{id}` | Get student info |

## Development

```bash
# Local development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Run tests
pytest
```

## Neo4j Schema

```cypher
(:Student {student_id, name, created_at})-[:HAS_LEVEL]->(:CEFRLevel {code})
(:Student)-[:KNOWS]->(:Vocabulary {word, translation, topic, confidence})
(:Student)-[:MADE_ERROR]->(:GrammarError {original, corrected, rule})
(:Student)-[:COMPLETED]->(:Exercise {type, score, level})
(:Student)-[:READY_FOR]->(:NiveauTest {test_type, readiness})
```
