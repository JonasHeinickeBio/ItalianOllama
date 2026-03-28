# ItalianOllama Docker Setup

This directory contains the Docker configuration for the LLM-based language learning workflow.

## Components

| Service | Port | Description |
|---------|------|-------------|
| OpenWebUI | 8080 | User interface for interacting with LLMs |
| Neo4j | 7474/7687 | Graph database for memory/knowledge graph |
| Ollama | 11434 | Local LLM inference server |
| Language Service | 8000 | Python API for aisuite/hellmholtz |

## Quick Start

1. **Create required secrets** (see below)
2. **Start services**: `docker-compose up -d`
3. **Access OpenWebUI**: http://localhost:8080
4. **Access Neo4j**: http://localhost:7474

## Creating Secrets

Create the following files in the `secrets/` directory:

```bash
# Generate secure passwords
openssl rand -base64 32 > secrets/neo4j_password.txt
openssl rand -base64 32 > secrets/webui_secret_key.txt
openssl rand -base64 32 > secrets/openwebui_api_key.txt

# Set your model preference
echo "llama3.2" > secrets/ollama_model.txt

# For external LLM providers (optional)
# echo "sk-your-openai-key" > secrets/aisuite_api_key.txt
```

Or create a `.env` file in the project root:

```bash
# .env file (DO NOT COMMIT THIS FILE!)
NEO4J_PASSWORD=your_secure_password_here
WEBUI_SECRET_KEY=your_webui_secret_key_min_32_chars
OPENWEBUI_API_KEY=your_api_key_here
OLLAMA_MODEL=llama3.2
AISUITE_PROVIDER=ollama
AISUITE_API_KEY=
```

## Security Features

- All containers run with `no-new-privileges` security option
- Non-root user (UID 1000) for the language service
- Resource limits (memory/CPU) on all containers
- Isolated network bridge
- Secrets loaded from files (not committed)

## Managing Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v

# Rebuild language service
docker-compose build language-learning-service

# Access container shell
docker exec -it italianollama-language-service /bin/bash
```

## Testing Neo4j Connection

```bash
# From host
curl -u neo4j:your_password http://localhost:7474/db/neo4j/tx/commit \
  -H 'Content-Type: application/json' \
  -d '{"statements": [{"statement": "RETURN 1"}]}'

# From container
docker exec italianollama-neo4j cypher-shell -u neo4j -p your_password "RETURN 1"
```

## Pulling Ollama Models

```bash
# Pull Italian-specific models
docker exec italianollama-ollama ollama pull llama3.2
docker exec italianollama-ollama ollama pull mistral
docker exec italianollama-ollama ollama pull codellama  # for code-related queries
```

## Troubleshooting

### Ollama not responding
```bash
docker exec italianollama-ollama ollama list
```

### Neo4j won't start
Check memory requirements: Neo4j needs at least 2GB available RAM

### OpenWebUI can't connect to Ollama
Ensure Ollama is healthy: `docker-compose ps`

## Development

To add aisuite and hellmholtz to the project:

1. Update `pyproject.toml` with the dependencies
2. Rebuild: `docker-compose build language-learning-service`
3. Add config to `config/hellmholtz.yaml`

Note: You may need to resolve the typer version conflict with hellmholtz.
