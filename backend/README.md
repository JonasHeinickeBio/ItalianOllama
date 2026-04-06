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

# Or use LiteLLM (local router) - supports OpenRouter free models
# LITELLM_BASE_URL=http://litellm:4000
# LITELLM_API_KEY=dummy
# LITELLM_MODEL=tutor

# OpenRouter API (for free LLM models)
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_HTTP_REFERER=https://your-app.com
OPENROUTER_X_TITLE=ItalianOllama

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
- [x] OpenRouter integration for free LLM models

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
| `POST /v1/chat/completions` | OpenAI-compatible chat (uses LiteLLM) |
| `POST /chat` | Simple chat |
| `POST /students` | Create student |
| `GET /students/{id}` | Get student info |

## Available LLM Models (via LiteLLM)

### Primary
- **Blablador** (`default`): Production model via Helmhotz Blablador API

### Fallback
- **Ollama** (`ollama-local`): Local Ollama instance (llama3.2:3b)

### OpenRouter Free Models (via LiteLLM)
All models support: `model=openrouter/{provider}/{model-id}:free` format

**Qwen Series:**
- `openrouter-qwen3-6-plus-free`: Qwen3 6B (free tier)
- `openrouter-qwen3-next-80b-a3b-instruct-free`: Qwen3 Next 80B (free tier)
- `openrouter-qwen3-coder-free`: Qwen3 Coder (free tier)

**Google Gemma Series:**
- `openrouter-gemini-3-4b-it-free`: Gemma 3 4B (free tier)
- `openrouter-gemini-3-12b-it-free`: Gemma 3 12B (free tier)
- `openrouter-gemini-3-27b-it-free`: Gemma 3 27B (free tier)
- `openrouter-gemini-3n-e2b-it-free`: Gemma 3N E2B (free tier)
- `openrouter-gemini-3n-e4b-it-free`: Gemma 3N E4B (free tier)
- `openrouter-lyria-3-pro-preview`: Lyria 3 Pro (preview)
- `openrouter-lyria-3-clip-preview`: Lyria 3 Clip (preview)

**NVIDIA Nemotron Series:**
- `openrouter-nemotron-3-super-120b-a12b-free`: Nemotron 3 Super 120B (free tier)
- `openrouter-nemotron-3-nano-30b-a3b-free`: Nemotron 3 Nano 30B (free tier)
- `openrouter-nemotron-nano-12b-v2-vl-free`: Nemotron Nano 12B VL (free tier)
- `openrouter-nemotron-nano-9b-v2-free`: Nemotron Nano 9B (free tier)

**Meta Llama Series:**
- `openrouter-llama-3.3-70b-instruct-free`: Llama 3.3 70B (free tier)
- `openrouter-llama-3.2-3b-instruct-free`: Llama 3.2 3B (free tier)
- `openrouter-hermes-3-llama-3.1-405b-free`: Hermes 3 Llama 3.1 405B (free tier)

**OpenAI Series:**
- `openrouter-gpt-oss-120b-free`: GPT-OSS 120B (free tier)
- `openrouter-gpt-oss-20b-free`: GPT-OSS 20B (free tier)

**Other Providers:**
- `openrouter-glm-4.5-air-free`: Zhipu GLM-4.5-Air
- `openrouter-step-3.5-flash-free`: Stepfun Step 3.5 Flash
- `openrouter-minimax-m2.5-free`: MiniMax M2.5
- `openrouter-lfm-2.5-1.2b-thinking-free`: Liquid LFM 2.5 1.2B Thinking
- `openrouter-lfm-2.5-1.2b-instruct-free`: Liquid LFM 2.5 1.2B Instruct
- `openrouter-trinity-large-preview-free`: Arcee AI Trinity Large (preview)
- `openrouter-trinity-mini-free`: Arcee AI Trinity Mini
- `openrouter-dolphin-mistral-24b-venice-free`: CognitiveComputations Dolphin Mistral 24B
- `openrouter-default-free`: OpenRouter default free model

## Usage Examples

### Using OpenRouter Free Models via CLI

List available free models:
```bash
italianollama openrouter list
```

Add all free models to LiteLLM:
```bash
italianollama openrouter add
```

### Using OpenRouter via Python

```python
from italianollama.utils.openrouter import discover_free_models, add_free_models_to_config

# Discover free models
free_models = await discover_free_models()

# Add to LiteLLM config
added = await add_free_models_to_config()
```

### LiteLLM Configuration

Models in config use `os.environ/` prefix for lazy evaluation:
```yaml
model_list:
  - model_name: openrouter-default-free
    litellm_params:
      model: openrouter/openrouter/free
      api_key: os.environ/OPENROUTER_API_KEY
      rpm: 60
      tpm: 100000
      timeout: 120
```

### Start LiteLLM with OpenRouter Models

```bash
# Start LiteLLM proxy with OpenRouter models
litellm --config backend/litellm/litellm_config.yaml

# Or use the full ItalianOllama stack
docker-compose up -d
```

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
