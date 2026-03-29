# Italian Tutor - AI-Powered Italian Language Learning

> An intelligent Italian language tutor built with LangGraph, Neo4j, and LiteLLM

## Overview

Italian Tutor is an AI-powered language learning application that provides personalized Italian lessons through conversation. It uses a graph-based state management system (LangGraph) to orchestrate different exercise types and tracks student progress in Neo4j.

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   OpenWebUI     │────▶│    FastAPI      │────▶│     LiteLLM     │
│   (Frontend)    │     │    (Backend)    │     │  (Blablador)    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │     Neo4j       │
                        │   (Memory)      │
                        └─────────────────┘
```

## Features

- 🤖 **AI Tutor** - Conversational Italian learning with adaptive difficulty
- 📊 **Progress Tracking** - Neo4j stores student progress, vocabulary, and errors
- 🔄 **Multiple Exercise Types** - Grammar, vocabulary, translation, writing, exam prep
- 🎯 **CEFR Level Assessment** - Automatic placement test (A1-C2)
- 🌍 **Multi-Provider LLM** - Supports Ollama, Blablador, OpenAI, Anthropic via LiteLLM
- ☁️ **Cloud-Ready** - Works with Neo4j Aura (production) or local Neo4j

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)
- Neo4j Aura instance (or local Neo4j)
- LLM API access (Blablador, OpenAI, or local Ollama)

### 1. Clone & Configure

```bash
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
```

Create `.env` file:

```bash
# Neo4j Aura (Cloud) - RECOMMENDED
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=your_username
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
USE_AURA=true

# Or Local Neo4j
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_password
# USE_AURA=false

# Blablador (Helmholtz LLM) - RECOMMENDED
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_api_key
BLABLADOR_MODEL=alias-fast

# Or Ollama (local)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2

# LiteLLM Settings
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy

# App Settings
LOG_LEVEL=INFO
```

### 2. Start Services

**With Neo4j Aura + Blablador (Production):**
```bash
cd backend
docker compose -f docker-compose.yml -f docker-compose.aura.yml up -d
```

**With Local Neo4j:**
```bash
cd backend
docker compose up -d
```

### 3. Access

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| OpenWebUI | http://localhost:3000 |

---

## Project Structure

```
italianollama/
├── src/italianollama/          # Main package
│   ├── __init__.py             # Package init
│   ├── api/                    # FastAPI application
│   │   ├── __init__.py
│   │   └── main.py             # API endpoints & routes
│   ├── cli/                    # CLI commands
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── main.py
│   ├── graph/                  # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── state.py            # TutorState TypedDict
│   │   ├── graph.py            # Graph builder & router
│   │   └── nodes/              # LangGraph nodes
│   │       ├── __init__.py
│   │       ├── base.py         # LLMClient wrapper
│   │       ├── placement.py    # CEFR placement test
│   │       ├── vocabulary.py   # Flashcard exercises
│   │       ├── grammar.py      # Grammar drills
│   │       ├── translation.py  # Translation practice
│   │       ├── free_writing.py # Writing exercises
│   │       └── niveau_test.py  # Exam prep (TELC/Goethe)
│   └── memory/                 # Neo4j client
│       ├── __init__.py
│       └── neo4j_client.py     # Database operations
├── backend/                    # Docker services
│   ├── docker-compose.yml
│   ├── docker-compose.aura.yml
│   ├── Dockerfile
│   ├── litellm/
│   └── requirements.txt
├── tests/                      # Test suite
├── pyproject.toml              # Poetry config
└── README_TUTOR.md             # This file
```

### Module Details

| Module | Description |
|--------|-------------|
| `api/main.py` | FastAPI app with chat, student, and health endpoints |
| `graph/graph.py` | LangGraph builder with router node |
| `graph/state.py` | TutorState TypedDict defining conversation state |
| `graph/nodes/base.py` | LLMClient for LiteLLM communication |
| `graph/nodes/placement.py` | CEFR level assessment (A1-C2) |
| `graph/nodes/vocabulary.py` | Flashcard system with spaced repetition |
| `graph/nodes/grammar.py` | Grammar exercises with error detection |
| `graph/nodes/translation.py` | Italian↔English translation practice |
| `graph/nodes/free_writing.py` | Open writing prompts with feedback |
| `graph/nodes/niveau_test.py` | TELC/Goethe-style exam simulation |
| `memory/neo4j_client.py` | Neo4j operations for student data |

---

## LangGraph Workflow

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

---

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 0 | ✅ DONE | Project setup & Docker |
| Phase 1 | ✅ DONE | Working skeleton with Sofia |
| Phase 2 | ✅ DONE | Neo4j client with student memory |
| Phase 3 | ✅ DONE | Placement test node |
| Phase 4 | ✅ DONE | Vocabulary flashcards |
| Phase 5 | ✅ DONE | Grammar drills |
| Phase 6 | ✅ DONE | Translation exercises |
| Phase 7 | ✅ DONE | Free writing |
| Phase 8 | ✅ DONE | Niveau test prep |
| Phase 9 | 🔴 PENDING | Production hardening |

**Legend:**
- ✅ DONE - Fully implemented
- 🔴 PENDING - Not yet implemented

---

## Neo4j Schema

```cypher
# Student node with CEFR level
(:Student {student_id, name, created_at})-[:HAS_LEVEL]->(:CEFRLevel {code, confidence})

# Vocabulary with spaced repetition
(:Student)-[:KNOWS]->(:Vocabulary {word, translation, topic, level, confidence, last_practiced})

# Grammar error tracking
(:Student)-[:MADE_ERROR]->(:GrammarError {original, corrected, rule, level, seen_count})

# Exercise history
(:Student)-[:COMPLETED]->(:Exercise {type, score, level, content, completed_at})

# Niveau test results
(:Student)-[:READY_FOR]->(:NiveauTest {test_type, level, readiness, skill_scores, completed_at})
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check (Neo4j, LiteLLM) |
| `/v1/chat/completions` | POST | OpenAI-compatible chat |
| `/chat` | POST | Simple chat with student_id |
| `/students` | POST | Create student |
| `/students/{id}` | GET | Get student info & progress |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | - |
| `NEO4J_DATABASE` | Neo4j database | `neo4j` |
| `LITELLM_BASE_URL` | LiteLLM API URL | `http://litellm:4000` |
| `LITELLM_MODEL` | Model name | `tutor` |
| `LITELLM_API_KEY` | API key | `dummy` |

## LLM Providers

### Blablador (Recommended)
```bash
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_key
```

### Ollama (Local)
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### OpenAI
```bash
OPENAI_API_KEY=sk-...
```

## Troubleshooting

### Check services
```bash
docker compose ps
docker compose logs -f
```

### Neo4j connection
```bash
# Test Neo4j
docker compose exec neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

### LiteLLM health
```bash
curl http://localhost:4000/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the module structure
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file

## Credits

- [LangGraph](https://langchain-ai.github.io/langgraph/) - Graph-based agent orchestration
- [Neo4j](https://neo4j.com/) - Graph database
- [LiteLLM](https://litellm.ai/) - Unified LLM interface
- [Open WebUI](https://openwebui.com/) - User-friendly UI
