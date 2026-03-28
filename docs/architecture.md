# Architecture

This document describes the system architecture of ItalianOllama.

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenWebUI (Port 8080)                    │
│                    User Interface / Chat UI                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Language API (Port 8000)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ FastAPI     │  │ Language    │  │ LLM Client              │ │
│  │ Endpoints   │◄─┤ Tutor       │◄─┤ (hellmholtz/aisuite)    │ │
│  └─────────────┘  │ Agent       │  └───────────┬─────────────┘ │
│                   └──────┬──────┘              │               │
│                          │                     │               │
│                   ┌──────▼──────┐              │               │
│                   │ Memory      │              ▼               │
│                   │ Graph       │      ┌───────────────┐       │
│                   │ (Neo4j)     │      │ Blablador     │       │
│                   └─────────────┘      │ Ollama        │       │
│                                         │ OpenAI        │       │
│                                         │ Anthropic     │       │
│                                         └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Language API (`src/italianollama/api/main.py`)

FastAPI application providing REST endpoints:

- **Chat endpoints** (`POST /chat`) - Conversational learning
- **Vocabulary endpoints** - Add/get vocabulary
- **Session endpoints** - Track learning progress
- **Health check** (`GET /health`) - Service status

### 2. Language Tutor Agent (`src/italianollama/agents/tutor.py`)

Core learning agent that:
- Generates AI responses using configured LLM
- Manages conversation context and history
- Extracts vocabulary from conversations
- Provides topic-based lessons and quizzes

### 3. LLM Client (`src/italianollama/llm/client.py`)

Unified interface for multiple LLM providers:
- Uses hellmholtz for multi-provider support
- Falls back to direct API calls if needed
- Handles authentication and routing

Supported providers:
- **Blablador** (Helmholtz) - Primary provider
- **Ollama** - Local models
- **OpenAI** - GPT models
- **Anthropic** - Claude models

### 4. Memory Graph (`src/italianollama/memory/graph.py`)

Neo4j-based knowledge graph storing:

**Nodes:**
- `Vocabulary` - Words, translations, examples
- `GrammarRule` - Grammar rules and explanations
- `Topic` - Learning topics/categories
- `Session` - Learning sessions
- `Message` - Chat messages

**Relationships:**
- `BELONGS_TO` - Vocabulary/Grammar → Topic
- `LEARNED` - Session → Vocabulary
- `HAS_MESSAGE` - Session → Message
- `RELATED_TO` - Vocabulary → Vocabulary

## Data Flow

### Chat Flow

1. User sends message via OpenWebUI
2. API receives request, validates input
3. Language Tutor retrieves session context from Neo4j
4. Tutor builds prompt with vocabulary context
5. LLM Client sends request to configured provider
6. Response stored in Neo4j session
7. Response returned to user

### Vocabulary Learning Flow

1. User asks to learn vocabulary for a topic
2. Tutor fetches relevant vocabulary from memory
3. Tutor generates lesson using LLM
4. New words added to knowledge graph
5. Session updated with learned vocabulary

## Configuration

### Environment Variables

```bash
# LLM Configuration
AISUITE_PROVIDER=ollama
BLABLADOR_API_KEY=...
BLABLADOR_API_URL=...
OLLAMA_MODEL=llama3.2

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=...

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Model Configuration

Models are configured in hellmholtz. See [Model Management](models.md) for details.

## Security

- All containers run with `no-new-privileges` security option
- Non-root user (UID 1000) for language service
- Resource limits (memory/CPU) on all containers
- Isolated bridge network
- Secrets loaded from files, not environment variables in images

## Performance

- Async Neo4j driver for concurrent requests
- LLM response caching (optional)
- Connection pooling for database
- Health checks for service dependencies
