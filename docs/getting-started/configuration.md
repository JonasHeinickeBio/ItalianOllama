# Configuration Guide

This guide explains all configuration options available in ItalianOllama.

## Environment Variables

### Neo4j Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` | Yes |
| `NEO4J_USER` | Neo4j username | `neo4j` | Yes |
| `NEO4J_PASSWORD` | Neo4j password | - | Yes |
| `NEO4J_DATABASE` | Neo4j database | `neo4j` | No |
| `USE_AURA` | Use Neo4j Aura cloud | `false` | No |

### LLM Provider Configuration

#### Blablador (Recommended)

```bash
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_api_key
BLABLADOR_MODEL=alias-fast
```

#### Ollama (Local)

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

#### OpenAI

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

#### Anthropic

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus
```

### LiteLLM Configuration

```bash
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy
LITELLM_DROP_PARAMS=true
LITELLM_MAX_PARALLEL_REQUESTS=100
```

### Application Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `AUTH_SECRET` | JWT signing secret | - |
| `DISABLE_OAUTH` | Disable OAuth in dev | `false` |
| `SESSION_TIMEOUT` | Session timeout (seconds) | `14400` |

## Configuration Files

### LiteLLM (`backend/litellm/litellm_config.yaml`)

```yaml
model_list:
  - model_name: tutor
    litellm_params:
      model: openai/fake
      api_key: os.environ/OAI_API_KEY

  - model_name: blablador
    litellm_params:
      model: openai/fake
      api_base: os.environ/BLABLADOR_API_URL
      api_key: os.environ/BLABLADOR_API_KEY

litellm_settings:
  drop_params: true
  set_verbose: true

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
```

### Chainlit (`frontend/chainlit/.chainlit/config.toml`)

```toml
[project]
enableVPN = false
userEnv = []

[UI]
name = "Italian Tutor"
default_collapse_content = true
default_expand_messages = false

[Features]
multimodal = true
unsafe_allow_html = false
latex = true

[Features.prompt_playground]
show_in_chat = false
```

### Nginx (`frontend/nginx.conf`)

```nginx
erver {
    listen 80;
    client_max_body_size 100M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;

    location /chat/ {
        proxy_pass http://chainlit:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /dashboard/ {
        proxy_pass http://streamlit:8501/;
        proxy_set_header X-Script-Name /dashboard;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://api/health;
    }
}
```

## Development vs Production

### Development Settings

```bash
# .env.development
LOG_LEVEL=DEBUG
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
USE_AURA=false
DISABLE_OAUTH=true
```

### Production Settings

```bash
# .env.production
LOG_LEVEL=INFO
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=your_user
NEO4J_PASSWORD=your_secure_password
NEO4J_DATABASE=neo4j
USE_AURA=true
AUTH_SECRET=$(openssl rand -hex 32)
```

## Docker Compose Overlays

Use compose overlays for different environments:

```bash
# Development
docker compose up -d

# Production with Neo4j Aura
docker compose -f docker-compose.yml -f docker-compose.aura.yml up -d

# With custom config
docker compose --env-file .env.production up -d
```
