# ItalianOllama Documentation

Welcome to the ItalianOllama documentation - an LLM-based language learning workflow using hellmholtz, Neo4j, and OpenWebUI.

## Quick Links

- [Installation](installation.md)
- [Architecture](architecture.md)
- [API Reference](api.md)
- [Configuration](configuration.md)
- [Docker Setup](docker.md)
- [Model Management](models.md)
- [Troubleshooting](troubleshooting.md)

## Overview

ItalianOllama is a comprehensive language learning application that combines:

- **LLM-powered tutoring** via hellmholtz (multi-provider LLM support)
- **Knowledge graph memory** using Neo4j for storing vocabulary and learning history
- **Web interface** via OpenWebUI
- **Local inference** via Ollama

## Features

### 🤖 AI Language Tutor
- Conversational Italian learning
- Adaptive difficulty levels (beginner, intermediate, advanced)
- Vocabulary and grammar instruction
- Quiz generation

### 🧠 Knowledge Graph
- Persistent vocabulary storage
- Learning session tracking
- Topic-based organization
- Related word suggestions

### 🔧 Multi-Provider LLM Support
- **Blablador** (Helmholtz) - Default provider
- **Ollama** - Local inference
- **OpenAI** - GPT models
- **Anthropic** - Claude models

## Getting Started

```bash
# Quick start with Docker
docker compose up -d

# Access the application
OpenWebUI: http://localhost:8080
API: http://localhost:8000
Neo4j: http://localhost:7474
```

See [Installation](installation.md) for detailed setup instructions.

## Project Structure

```
ItalianOllama/
├── src/italianollama/      # Main application code
│   ├── api/                # FastAPI endpoints
│   ├── agents/             # Language tutor agent
│   ├── llm/                # LLM client wrapper
│   ├── memory/             # Neo4j knowledge graph
│   └── utils/              # Utilities
├── config/                 # Configuration files
├── docs/                   # Documentation
├── docker-compose.yml      # Docker orchestration
├── Dockerfile.language-service  # Python API container
└── pyproject.toml          # Python dependencies
```

## License

MIT License - See LICENSE file for details.
