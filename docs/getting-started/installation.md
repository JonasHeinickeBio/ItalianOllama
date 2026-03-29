# Installation Guide

This guide will help you set up the ItalianOllama project on your local machine or server.

## Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker | 20.10+ | Required for containerized deployment |
| Docker Compose | 2.0+ | For orchestrating multi-container setup |
| Python | 3.10+ | Only for local development |
| Neo4j | - | Can use Aura cloud or local Docker |

## Clone the Repository

```bash
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
```

## Choose Your Setup

### Option 1: Neo4j Aura (Recommended for Production)

Uses cloud-hosted Neo4j database:

```bash
cd backend
docker compose -f docker-compose.yml -f docker-compose.aura.yml up -d
```

### Option 2: Local Neo4j (Recommended for Development)

Runs Neo4j locally in Docker:

```bash
cd backend
docker compose up -d
```

## Environment Configuration

Create a `.env` file in the root directory:

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

# OpenRouter (Free Models) - RECOMMENDED for development
# Get free API key: https://openrouter.ai/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LITELLM_MODEL=tutor-free

# Or Blablador (Helmholtz LLM) - RECOMMENDED for production
# BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
***REMOVED***=your_api_key
# BLABLADOR_MODEL=alias-fast
# LITELLM_MODEL=tutor

# Or Ollama (local)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2
# LITELLM_MODEL=ollama-local

# LiteLLM Settings
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy

# App Settings
LOG_LEVEL=INFO
```

## Verify Installation

After starting the services, verify everything is working:

```bash
# Check running containers
docker compose ps

# Test API health
curl http://localhost:8000/health

# Test LiteLLM
curl http://localhost:4000/health
```

## Access the Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Chat** | http://localhost/chat | Sofia tutor (Chainlit) |
| **Dashboard** | http://localhost/dashboard | Progress & analytics (Streamlit) |
| **API** | http://localhost/api/docs | Backend documentation |
| **Nginx** | http://localhost:80 | Main entry point |

## Development Setup

For local development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Start Neo4j locally
docker run -d -p 7687:7687 -p 7474:7474 -e NEO4J_PASSWORD=password neo4j

# Run backend
python -m src.italianollama.api

# Run Chainlit (in separate terminal)
cd frontend/chainlit
python -m chainlit run chainlit_app.py

# Run Streamlit (in separate terminal)
cd frontend/streamlit
python -m streamlit run app.py
```

## Next Steps

- [Configuration Guide](configuration.md) - Customize your setup
- [Quick Start](quick-start.md) - Begin using the tutor
- [Architecture Overview](../architecture/overview.md) - Understand the system
