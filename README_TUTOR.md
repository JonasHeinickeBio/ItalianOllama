# Italian Tutor - AI-Powered Italian Language Learning

> An intelligent Italian language tutor built with LangGraph, Neo4j, and LiteLLM

## Overview

Italian Tutor is an AI-powered language learning application that provides personalized Italian lessons through conversation. It uses a graph-based state management system (LangGraph) to orchestrate different exercise types and tracks student progress in Neo4j.

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   OpenWebUI     │────▶│    FastAPI      │────▶│  LiteLLM/       │
│   (Frontend)    │     │    (Backend)    │     │  Blablador      │
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
- Python 3.12+ (for local development)
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

# App Settings
LOG_LEVEL=INFO
WEBUI_SECRET_KEY=change_this_secret
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

## Project Structure

```
italianollama/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app + routes
│   │   ├── graph/
│   │   │   ├── state.py            # TutorState TypedDict
│   │   │   ├── graph.py            # LangGraph builder
│   │   │   └── nodes/
│   │   │       ├── base.py         # LLM client wrapper
│   │   │       ├── placement.py    # Phase 3: CEFR assessment
│   │   │       ├── grammar.py      # Phase 5: Grammar drills
│   │   │       ├── vocabulary.py   # Phase 4: Flashcards
│   │   │       ├── translation.py  # Phase 6: Translation
│   │   │       ├── free_writing.py # Phase 7: Writing
│   │   │       └── niveau_test.py  # Phase 8: Exam prep
│   │   └── memory/
│   │       └── neo4j_client.py     # Neo4j operations
│   ├── litellm/
│   │   └── litellm_config.yaml     # LLM routing config
│   ├── docker-compose.yml
│   ├── docker-compose.aura.yml     # Aura override
│   ├── Dockerfile
│   └── requirements.txt
├── cli.py                          # CLI tool
├── config/                         # Configuration files
├── secrets/                        # API keys (gitignored)
└── docker/                         # Original docker setup
```

---

# Phased Development Roadmap

## Phase 0 — Project Setup ✅ DONE

- [x] Repository structure created
- [x] Docker Compose with 4 services (OpenWebUI, FastAPI, LiteLLM, Neo4j)
- [x] `.gitignore` for secrets
- [x] Base docker-compose.yml

## Phase 1 — Working Skeleton (Free Chat) ✅ DONE

- [x] LiteLLM config with Blablador primary + Ollama fallback
- [x] `backend/app/config.py` - environment loading
- [x] `backend/app/graph/state.py` - TutorState TypedDict
- [x] `backend/app/graph/nodes/respond.py` - Sofia persona
- [x] `backend/app/graph/graph.py` - single node graph
- [x] `backend/app/main.py` - FastAPI with `/v1/chat/completions`
- [x] Docker Compose verified working

## Phase 2 — Neo4j Student Memory 🟡 PARTIAL

- [x] `backend/app/memory/neo4j_client.py` - async Neo4j driver
- [ ] `memory/queries.py` - Cypher functions (integrated in client)
- [x] Student creation and retrieval
- [ ] LangGraph checkpointing (optional enhancement)

## Phase 3 — Placement Test 🟡 PARTIAL

- [x] `nodes/placement.py` - 10 adaptive questions
- [x] CEFR level assignment (A1-C2)
- [x] Routing logic in graph.py
- [x] Neo4j storage for student level

## Phase 4 — Vocabulary Flashcards 🟡 PARTIAL

- [x] `nodes/vocabulary.py` - flashcard loop
- [x] Spaced repetition with confidence scores
- [x] Neo4j vocabulary storage

## Phase 5 — Grammar Drills 🟡 PARTIAL

- [x] `nodes/grammar.py` - grammar exercises
- [ ] Error detection in free chat (optional)

## Phase 6 — Translation Exercises 🟡 PARTIAL

- [x] `nodes/translation.py` - Italian↔English translation
- [x] Scoring system (0-100)

## Phase 7 — Free Writing 🟡 PARTIAL

- [x] `nodes/free_writing.py` - open prompts
- [x] Correction and feedback

## Phase 8 — Niveau Test Prep 🟡 PARTIAL

- [x] `nodes/niveau_test.py` - TELC/Goethe-style tests
- [x] Readiness scoring per skill

## Phase 9 — Production Hardening 🔴 PENDING

- [ ] Swap to Neo4j Aura (already supported via docker-compose.aura.yml)
- [ ] Add authentication to FastAPI
- [ ] Rate limiting
- [ ] Observability (Langfuse/LiteLLM dashboard)
- [ ] GitHub Actions CI
- [ ] Complete README

---

## Implementation Status Summary

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 0 | ✅ DONE | Project setup & Docker |
| Phase 1 | ✅ DONE | Working skeleton with Sofia |
| Phase 2 | 🟡 PARTIAL | Neo4j client done, queries integrated |
| Phase 3 | ✅ DONE | Placement test node |
| Phase 4 | ✅ DONE | Vocabulary flashcards |
| Phase 5 | ✅ DONE | Grammar drills |
| Phase 6 | ✅ DONE | Translation exercises |
| Phase 7 | ✅ DONE | Free writing |
| Phase 8 | ✅ DONE | Niveau test prep |
| Phase 9 | 🔴 PENDING | Production hardening |

**Legend:**
- ✅ DONE - Fully implemented
- 🟡 PARTIAL - Core implemented, optional enhancements pending
- 🔴 PENDING - Not yet implemented

---

## Neo4j Schema

```cypher
# Student
(:Student {student_id, name, created_at})-[:HAS_LEVEL]->(:CEFRLevel {code, confidence})

# Vocabulary
(:Student)-[:KNOWS]->(:Vocabulary {word, translation, topic, level, confidence, last_practiced})

# Grammar Errors
(:Student)-[:MADE_ERROR]->(:GrammarError {original, corrected, rule, level, seen_count})

# Exercises
(:Student)-[:COMPLETED]->(:Exercise {type, score, level, content, completed_at})

# Niveau Tests
(:Student)-[:READY_FOR]->(:NiveauTest {test_type, level, readiness, skill_scores, completed_at})
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/v1/chat/completions` | POST | OpenAI-compatible chat |
| `/chat` | POST | Simple chat |
| `/students` | POST | Create student |
| `/students/{id}` | GET | Get student info |

## CLI Commands

```bash
# Start API
python cli.py start api

# Check Neo4j
python cli.py neo4j status
python cli.py neo4j connect

# LLM operations
python cli.py llm list
python cli.py llm test
python cli.py llm chat "Ciao! Come stai?"

# Vocabulary
python cli.py vocab add "ciao" "hello" --topic greetings
python cli.py vocab list
python cli.py vocab stats

# Configuration
python cli.py config show
```

## LLM Providers

### Blablador (Recommended)
```bash
AISUITE_PROVIDER=blablador
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_key
```

### Ollama (Local)
```bash
AISUITE_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### OpenAI
```bash
AISUITE_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### Anthropic
```bash
AISUITE_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
docker compose ps

# View Neo4j logs
docker compose logs neo4j

# Verify Aura credentials
# Wait 60 seconds after creating Aura instance
```

### LLM Connection Issues

```bash
# Test Blablador
curl -H "Authorization: Bearer $BLABLADOR_API_KEY" \
  $BLABLADOR_API_URL/models

# Test Ollama
curl http://localhost:11434/api/tags
```

### OpenWebUI Issues

```bash
# Check if API is reachable from OpenWebUI
docker compose logs openwebui

# Verify API key configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the phase structure
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file

## Credits

- [LangGraph](https://langchain-ai.github.io/langgraph/) - Graph-based agent orchestration
- [Neo4j](https://neo4j.com/) - Graph database
- [LiteLLM](https://litellm.ai/) - Unified LLM interface
- [Open WebUI](https://openwebui.com/) - User-friendly UI
