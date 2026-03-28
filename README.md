# ItalianOllama 🤖🇮🇹

LLM-powered Italian language learning workflow using hellmholtz, Neo4j, and OpenWebUI.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)

## Features

- **AI Language Tutor** - Conversational Italian learning with adaptive difficulty (beginner/intermediate/advanced)
- **Knowledge Graph** - Neo4j-powered persistent vocabulary storage and learning history
- **Multi-Provider LLM** - Blablador (Helmholtz), Ollama, OpenAI, Anthropic support
- **Web Interface** - User-friendly chat UI via OpenWebUI
- **Vocabulary & Grammar** - Topic-based organization with related word suggestions
- **Session Tracking** - Track learning progress across sessions

## Quick Start

```bash
# 1. Create secrets directory
mkdir -p secrets

# 2. Generate secure passwords
openssl rand -base64 32 > secrets/neo4j_password.txt
openssl rand -base64 32 > secrets/webui_secret_key.txt

# 3. Configure environment
cp config.env.example .env
# Edit .env with your BLABLADOR_API_KEY and other settings

# 4. Start all services
docker compose up -d

# 5. Verify services
docker compose ps
curl http://localhost:8000/health
```

### Access Points

| Service | Port | URL |
|---------|------|-----|
| OpenWebUI | 8080 | http://localhost:8080 |
| API | 8000 | http://localhost:8000 |
| Neo4j Browser | 7474 | http://localhost:7474 |
| Neo4j Bolt | 7687 | bolt://localhost:7687 |
| Ollama | 11434 | http://localhost:11434 |

## Environment Variables

### Required

```bash
BLABLADOR_API_KEY=your_api_key
BLABLADOR_API_BASE=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_MODEL=alias-fast
NEO4J_PASSWORD=your_secure_password
```

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3.2` | Ollama model |
| `TARGET_LANGUAGE` | `italian` | Learning language |
| `DIFFICULTY_LEVEL` | `intermediate` | Difficulty level |
| `API_PORT` | `8000` | API port |

## Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  OpenWebUI   │────►│  Language API   │────►│  LLM Clients │
│  (Port 8080) │     │  (Port 8000)    │     │  (hellmholtz)│
└──────────────┘     └────────┬────────┘     └──────┬───────┘
                              │                     │
                              ▼                     ▼
                      ┌───────────────┐     ┌───────────────┐
                      │   Neo4j       │     │  Blablador    │
                      │ (Knowledge    │     │  Ollama       │
                      │    Graph)     │     │  OpenAI       │
                      └───────────────┘     │  Anthropic    │
                                            └───────────────┘
```

**Components:**
- **Language API** - FastAPI endpoints for chat, vocabulary, sessions
- **Tutor Agent** - AI-powered learning with context management
- **Memory Graph** - Neo4j knowledge graph for vocabulary/grammar storage

## Project Structure

```
ItalianOllama/
├── src/italianollama/      # Main application
│   ├── api/                # FastAPI endpoints
│   ├── agents/             # Language tutor agent
│   ├── llm/                # LLM client wrapper
│   └── memory/             # Neo4j knowledge graph
├── config/                 # Configuration files
├── docs/                   # Documentation
├── docker-compose.yml      # Docker orchestration
└── pyproject.toml          # Python dependencies
```

## Development Setup

```bash
# Clone and setup
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
git checkout feature/llm-language-learning-workflow

# Install dependencies
poetry install
poetry shell

# Run tests
poetry run pytest
```

## Documentation

- [Installation](docs/installation.md) - Detailed setup guide
- [Architecture](docs/architecture.md) - System design
- [Configuration](docs/configuration.md) - All config options
- [API Reference](docs/api.md) - REST endpoints
- [Model Management](docs/models.md) - Available models
- [Troubleshooting](docs/troubleshooting.md) - Common issues

## License

MIT License - See [LICENSE](LICENSE) for details.
