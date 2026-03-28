# Installation Guide

This guide covers setting up ItalianOllama for development and production.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Poetry (Python package manager)
- Neo4j (optional, for local development)

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
git checkout feature/llm-language-learning-workflow
```

### 2. Install Dependencies

```bash
# Install Poetry if not present
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 3. Configure Environment

```bash
# Copy example environment file
cp config.env.example .env

# Edit .env with your settings
nano .env
```

Required variables:
```bash
BLABLADOR_API_KEY=your_api_key
BLABLADOR_API_BASE=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_MODEL=alias-fast
NEO4J_PASSWORD=your_secure_password
```

### 4. Verify Installation

```bash
# Run tests
poetry run pytest

# Check available models
poetry run hellm models
```

## Docker Setup (Recommended)

### Quick Start

```bash
# Create secrets directory and generate passwords
mkdir -p secrets
openssl rand -base64 32 > secrets/neo4j_password.txt
openssl rand -base64 32 > secrets/webui_secret_key.txt

# Start all services
docker compose up -d
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| OpenWebUI | 8080 | Web interface |
| Neo4j | 7474/7687 | Graph database |
| Ollama | 11434 | Local LLM |
| Language API | 8000 | Python API |

### Verification

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f

# Test API health
curl http://localhost:8000/health
```

## Production Deployment

### Security Considerations

1. **Secrets Management**: Never commit secrets to version control
2. **Network Isolation**: Services run in isolated Docker network
3. **Resource Limits**: Memory and CPU limits configured for all containers
4. **Non-root Users**: Language service runs as non-root (UID 1000)

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BLABLADOR_API_KEY` | Helmholtz Blablador API key | Yes |
| `BLABLADOR_API_BASE` | Blablador API URL | Yes |
| `BLABLADOR_MODEL` | Default model | No (default: alias-fast) |
| `NEO4J_PASSWORD` | Neo4j password | Yes |
| `WEBUI_SECRET_KEY` | OpenWebUI secret | Yes |

### Updating

```bash
# Pull latest code
git pull origin feature/llm-language-learning-workflow

# Rebuild containers
docker compose build

# Restart services
docker compose up -d
```

## Troubleshooting

See [Troubleshooting Guide](troubleshooting.md) for common issues.
