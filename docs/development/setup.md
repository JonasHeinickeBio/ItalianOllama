# Development Setup

This guide covers how to set up a local development environment for ItalianOllama.

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Runtime |
| Git | Any | Version control |
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Orchestration |

### Optional Software

| Software | Purpose |
|----------|---------|
| VS Code | IDE (recommended) |
| PyCharm | Alternative IDE |
| Neo4j Desktop | Local database management |
| Postman | API testing |

## Repository Setup

### Clone the Repository

```bash
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
```

### Install Python Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using Poetry (recommended)
poetry install

# Activate virtual environment
poetry shell
```

## Docker Setup

### Start All Services

```bash
cd backend
docker compose up -d
```

### Verify Services

```bash
# Check status
docker compose ps

# Check logs
docker compose logs -f
```

### Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8000/docs | - |
| LiteLLM | http://localhost:4000 | key: dummy |
| Neo4j | http://localhost:7474 | password: password |
| Neo4j Bolt | bolt://localhost:7687 | password: password |

## Environment Configuration

### Create .env File

```bash
# Backend .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
USE_AURA=false

# LLM Provider (choose one)

# Option 1: Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Option 2: Blablador
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_key

# LiteLLM
LITELLM_BASE_URL=http://localhost:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy

# App
LOG_LEVEL=DEBUG
```

## Running Components

### Backend Only (API + Database)

```bash
cd backend
docker compose up -d

# Test API
curl http://localhost:8000/health
```

### Frontend: Chainlit

```bash
# With Docker
cd frontend/chainlit
docker build -t italian-ollama-chainlit .
docker run -p 8000:8000 --env-file .env italian-ollama-chainlit

# Or locally
cd frontend/chainlit
pip install -r requirements.txt
python -m chainlit run chainlit_app.py
```

### Frontend: Streamlit

```bash
# With Docker
cd frontend/streamlit
docker build -t italian-ollama-streamlit .
docker run -p 8501:8501 --env-file .env italian-ollama-streamlit

# Or locally
cd frontend/streamlit
pip install -r requirements.txt
python -m streamlit run app.py
```

## IDE Setup

### VS Code

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
```

### Recommended Extensions

- Python
- Pylance
- Docker
- GitLens
- Prettier

### Debugging

```python
# .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: API",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.italianollama.api.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

## Testing

### Run Tests

```bash
# All tests
pytest

# Specific test
pytest tests/test_graph.py -v

# With coverage
pytest --cov=src tests/
```

### Test Database

Tests use a separate Neo4j instance:

```bash
docker run -d \
  -p 7688:7687 \
  -p 7475:7474 \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_TEST_PASSWORD=testpassword \
  neo4j
```

## Pre-Commit Hooks

The project uses pre-commit for code quality:

```bash
# Install pre-commit
pip install pre-commit

# Enable
pre-commit install

# Run manually
pre-commit run --all-files
```

### Configured Hooks

- trailing-whitespace
- end-of-file-fixer
- check-yaml
- check-added-large-files
- black (formatting)
- isort (imports)
- mypy (type checking)

## Common Issues

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Neo4j Connection Failed

```bash
# Check Neo4j is running
docker ps | grep neo4j

# Check logs
docker logs neo4j

# Reset password
docker exec neo4j cypher-shell -u neo4j -p password "ALTER CURRENT USER SET PASSWORD FROM 'password' TO 'newpassword'"
```

### Import Errors

```bash
# Reinstall dependencies
pip install -e .

# Or with Poetry
poetry install
poetry run pip install -e .
```

## Next Steps

- [Coding Standards](coding-standards.md)
- [Testing Guide](testing.md)
- [Debugging Guide](debugging.md)
