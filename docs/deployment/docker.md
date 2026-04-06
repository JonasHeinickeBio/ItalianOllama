# Docker Deployment Guide

This guide covers Docker-specific deployment configurations for ItalianOllama.

## Docker Architecture

```
┌─────────────────────────────────────────────┐
│           docker-compose.yml                │
├─────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐            │
│  │   Nginx     │ │   API       │            │
│  │   (Router)  │ │   (FastAPI) │            │
│  └─────────────┘ └─────────────┘            │
│  ┌─────────────┐ ┌─────────────┐            │
│  │  Chainlit   │ │  Streamlit  │            │
│  │   (Chat)    │ │  (Dashboard)│            │
│  └─────────────┘ └─────────────┘            │
│  ┌─────────────┐ ┌─────────────┐            │
│  │   LiteLLM   │ │   Neo4j     │            │
│  │   (LLM)     │ │   (DB)      │            │
│  └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────┘
```

## Docker Compose Files

### Main Compose File

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - chainlit
      - streamlit
      - api

  chainlit:
    build: ./chainlit/
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - AUTH_SECRET=${AUTH_SECRET}
      - LITELLM_BASE_URL=http://api:8000
    expose:
      - "8000"

  streamlit:
    build: ./streamlit/
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - AUTH_SECRET=${AUTH_SECRET}
      - API_BASE_URL=http://api:8000
    expose:
      - "8501"

  api:
    build: ../backend/
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - LITELLM_BASE_URL=http://litellm:4000
      - BLABLADOR_API_URL=${BLABLADOR_API_URL}
      - BLABLADOR_API_KEY=${BLABLADOR_API_KEY}
    expose:
      - "8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    volumes:
      - ./litellm/litellm_config.yaml:/app/config.yaml
    environment:
      - LITELLM_CONFIG_PATH=/app/config.yaml
      - DATABASE_URL=postgres://postgres:postgres@database:5432/postgres
    expose:
      - "4000"

  neo4j:
    image: neo4j:5
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
    ports:
      - "7474:7474"
      - "7687:7687"
```

### Neo4j Aura Overlay

```yaml
# docker-compose.aura.yml
services:
  neo4j:
    image: neo4j:5
    # Disable local Neo4j - use Aura instead
    profiles:
      - local

# Add external Neo4j via environment
# (handled in .env file)
```

## Building Images

### Build All Images

```bash
docker compose build
```

### Build Specific Image

```bash
# Backend API
docker build -t italianollama/api ./backend/

# Chainlit
docker build -t italianollama/chainlit ./frontend/chainlit/

# Streamlit
docker build -t italianollama/streamlit ./frontend/streamlit/
```

## Dockerfiles

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home appuser

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost/health || exit 1

# Run
CMD ["uvicorn", "src.italianollama.api.main:app", "--host", "0.0.0.0"]
```

### Chainlit Dockerfile

```dockerfile
# frontend/chainlit/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser

EXPOSE 8000

CMD ["chainlit", "run", "chainlit_app.py"]
```

### Streamlit Dockerfile

```dockerfile
# frontend/streamlit/Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

## Environment Variables

### Required Variables

```bash
# .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_key

LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy

AUTH_SECRET=your_jwt_secret
```

## Volume Management

### Named Volumes

```yaml
volumes:
  neo4j_data:
  litellm_cache:
```

### Backup Volumes

```bash
# Backup Neo4j data
docker run --rm -v italianollama_neo4j_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/neo4j_backup.tar.gz /data

# Restore
docker run --rm -v italianollama_neo4j_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/neo4j_backup.tar.gz -C /
```

## Networking

### Network Configuration

```yaml
networks:
  default:
    name: italianollama_network
    driver: bridge
```

### Service Communication

```bash
# From API to Neo4j
NEO4J_URI=bolt://neo4j:7687

# From API to LiteLLM
LITELLM_BASE_URL=http://litellm:4000
```

## Common Commands

### Start Services

```bash
# Using Docker CLI
docker compose up -d

# Using Docker Compose CLI
python cli.py docker up
```

### Stop Services

```bash
# Using Docker CLI
docker compose down

# Using Docker Compose CLI
python cli.py docker down
```

### Rebuild

```bash
# Using Docker CLI
docker compose build
docker compose up -d

# Using Docker Compose CLI
python cli.py docker helpers rebuild
python cli.py docker up
```

### Debug

```bash
# Shell into container
docker compose exec api sh

# View logs
docker compose logs -f api

# Check running containers
docker compose ps

# Using Docker Compose CLI equivalents
python cli.py docker logs fastapi --follow
python cli.py docker status
python cli.py docker helpers check
```

## Multi-Stage Builds

Optimize image size with multi-stage builds:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app
USER appuser
CMD ["python", "-m", "src.italianollama.api"]
```

## Docker Compose CLI

The project includes a comprehensive CLI for managing Docker Compose services:

```bash
# View all Docker commands
python cli.py docker --help

# Start services with specific profile
python cli.py docker up --profile cloud

# Check status
python cli.py docker status

# View logs
python cli.py docker logs fastapi --tail 100

# System diagnostics
python cli.py docker helpers check
python cli.py docker helpers validate --profile local

# Cleanup
python cli.py docker helpers prune
```

For complete CLI documentation, see [CLI README](../cli/README.md).

## Related Documentation

- [Production Deployment](production.md)
- [Nginx Configuration](nginx.md)
- [Troubleshooting](../troubleshooting/common-issues.md)
- [CLI Documentation](../cli/README.md)
