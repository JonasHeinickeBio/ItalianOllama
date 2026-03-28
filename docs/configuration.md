# Configuration Guide

This guide covers all configuration options for ItalianOllama.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BLABLADOR_API_KEY` | Helmholtz Blablador API key | `glpat-...` |
| `BLABLADOR_API_BASE` | Blablador API base URL | `https://api.helmholtz-blablador.fz-juelich.de/v1/` |
| `BLABLADOR_MODEL` | Default model (alias-fast recommended) | `alias-fast` |
| `NEO4J_PASSWORD` | Neo4j database password | (generated) |

### Optional Variables

#### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AISUITE_PROVIDER` | `ollama` | LLM provider (ollama, openai, anthropic, helmholtz) |
| `AISUITE_API_KEY` | - | Provider API key |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3.2` | Default Ollama model |
| `LLM_TEMPERATURE` | `0.7` | LLM sampling temperature |
| `LLM_MAX_TOKENS` | `4096` | Maximum tokens to generate |

#### Neo4j Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j bolt URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_DATABASE` | `neo4j` | Database name |

#### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API binding host |
| `API_PORT` | `8000` | API port |
| `DEBUG` | `false` | Enable debug mode |

#### Language Learning

| Variable | Default | Description |
|----------|---------|-------------|
| `TARGET_LANGUAGE` | `italian` | Default target language |
| `DIFFICULTY_LEVEL` | `intermediate` | Default difficulty (beginner, intermediate, advanced) |

## Docker Configuration

### Resource Limits

Default resource limits in docker-compose.yml:

| Service | Memory | CPUs |
|---------|--------|------|
| neo4j | 2GB | 1.5 |
| ollama | 8GB | 4 |
| openwebui | 2GB | 1 |
| language-service | 2GB | 1 |

### Ports

| Service | Internal | External | Description |
|---------|----------|----------|-------------|
| neo4j | 7474 | 7474 | HTTP |
| neo4j | 7687 | 7687 | Bolt |
| ollama | 11434 | 11434 | API |
| openwebui | 8080 | 8080 | Web UI |
| language-service | 8000 | 8000 | API |

## Model Configuration

### Available Models

See [Model Management](models.md) for available Blablador models and their token limits.

### Recommended Models

| Use Case | Model | Tokens | Notes |
|----------|-------|--------|-------|
| Fast responses | `alias-fast` | 32k | Quick, efficient |
| Complex tasks | `alias-large` | 128k | High capability |
| Maximum power | `alias-huge` | 128k | Largest model |
| Coding | `alias-code` | 128k | Code-optimized |

## Hellmholtz Configuration

The `config/hellmholtz.yaml` file configures the agent behavior:

```yaml
llm:
  provider: ollama  # or openai, anthropic, etc.
  model: llama3.2
  base_url: http://ollama:11434
  temperature: 0.7
  max_tokens: 4096

agent:
  max_iterations: 10
  reflection_enabled: true
  memory_enabled: true
  verbose: true

language_learning:
  target_language: italian
  difficulty_level: intermediate
  
  vocabulary_topics:
    - daily_conversation
    - food_and_dining
    - travel
    - healthcare
    - science

memory:
  connection:
    uri: bolt://neo4j:7687
    database: neo4j
```

## Security

### Secrets Management

1. **Never commit secrets** to version control
2. Use **Docker secrets** for production
3. Generate strong passwords: `openssl rand -base64 32`
4. Rotate passwords periodically

### Network Security

- Services communicate on isolated Docker network
- Only necessary ports exposed to host
- Consider VPN for production access

### Container Security

- All containers run with `no-new-privileges`
- Language service runs as non-root user (UID 1000)
- Read-only config mounts where possible
