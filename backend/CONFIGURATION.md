# ItalianOllama Configuration - Optimized for Local & Cloud Modes

## Overview

This configuration supports two modes:
1. **Local Mode**: All services run locally (Ollama, Neo4j, LiteLLM) - offline capable
2. **Cloud Mode**: Use external services (Blablador API, optional Neo4j Aura) - requires internet

## File Structure

```
backend/
├── .env              # Environment variables (API keys, credentials)
├── docker-compose.yml  # Service definitions with profiles
└── litellm/
    └── config.yaml   # LiteLLM configuration (optional)
```

## Environment Variables (`.env`)

### Neo4j Configuration
```bash
# Local (default)
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=admin
NEO4J_DATABASE=neo4j

# Cloud (Neo4j Aura)
# NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
# NEO4J_PASSWORD=your-aura-password

USE_AURA=false  # Set to true for Neo4j Aura
```

### LLM Configuration (Pick ONE Mode)

**Option 1: Local Mode (LiteLLM Proxy)**
```bash
LITELLM_MODE=proxy
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
# Ollama will be used via LiteLLM (local models)
```

**Option 2: Cloud Mode (Blablador Direct API)**
```bash
LITELLM_MODE=proxy
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor

BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your-key-here
BLABLADOR_MODEL=alias-fast

# Enable Blablador direct mode (bypass LiteLLM)
USE_BLABLADOR_DIRECT=true
```

### Application Settings
```bash
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

## Docker Compose Profiles

### Local Profile (Default - Offline Capable)
All services run locally including Ollama for LLM:
```bash
cd backend && docker compose --profile local up -d
```

Services:
- Ollama (LLM)
- Neo4j (Database)
- LiteLLM (LLM proxy)
- FastAPI (Backend)
- Chainlit (Chat UI)

### Cloud Profile
Use external LLM (Blablador) with local Neo4j:
```bash
cd backend && docker compose --profile cloud up -d
```

Services:
- Neo4j (Database)
- LiteLLM (LLM proxy, routes to Blablador)
- FastAPI (Backend)
- Chainlit (Chat UI)

### Blablador-Only Profile
Direct Blablador API without LiteLLM:
```bash
cd backend && docker compose --profile blablador-only up -d
```

Services:
- Neo4j (Database)
- FastAPI (Backend - uses Blablador directly)
- Chainlit (Chat UI)

### All Services (No Profile)
Runs all services (including Ollama):
```bash
cd backend && docker compose up -d
```

## API Keys Security

### ✅ Safe Practices
1. `.env` file is in `.gitignore` - won't be committed
2. Credentials loaded via `env_file` in docker-compose.yml
3. No API keys in docker-compose.yml itself

### ⚠️ Production Recommendations
1. Use Docker secrets or external secret management (Vault, AWS Secrets Manager)
2. Never commit `.env` to version control
3. Rotate API keys regularly
4. Use separate keys for development/staging/production

### Current Setup
Your `.env` contains:
- `NEO4J_PASSWORD` - Database password (safe, local)
- `BLABLADOR_API_KEY` - External LLM API key (needs protection)

## Mode Selection Matrix

| Mode | Neo4j | LLM | Internet | Use Case |
|------|-------|-----|----------|----------|
| Local | bolt://localhost | Ollama (via LiteLLM) | No | Offline development |
| Cloud | bolt://localhost | Blablador API | Yes | Better quality, online |
| Aura | neo4j+s:// | Blablador API | Yes | Cloud database + API |

## Quick Start

### Local Mode (Offline)
```bash
cd backend

# Ensure .env has:
# NEO4J_URI=bolt://127.0.0.1:7687
# BLABLADOR_API_URL=
# USE_AURA=false

docker compose --profile local up -d
```

### Cloud Mode (Blablador)
```bash
cd backend

# Update .env:
NEO4J_URI=bolt://127.0.0.1:7687
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your-key-here
USE_BLABLADOR_DIRECT=false  # Use LiteLLM proxy

docker compose --profile cloud up -d
```

## Troubleshooting

### Port Conflicts
If ports are already in use:
```bash
# Edit .env to change ports:
NEO4J_BOLT_PORT=7688
NEO4J_HTTP_PORT=7475
LITELLM_PORT=4001
API_PORT=8001
CHAINLIT_PORT=8502
```

### Services Not Starting
```bash
# Check logs
docker compose logs -f

# Restart specific service
docker compose restart fastapi

# Rebuild and start
docker compose up -d --build
```

### Environment Variables Not Loading
```bash
# Verify .env file exists and is readable
ls -la .env

# Check container environment
docker exec italian-tutor-api env | grep BLABLADOR
```

## Files to Keep

### Version Control (✅ Committed)
- `docker-compose.yml` - Service definitions
- `.env.aura` - Example Aura configuration
- `backend/Dockerfile` - Backend container
- `src/italianollama/frontend/Dockerfile` - Frontend container

### Git Ignore (❌ Never Commit)
- `.env` - Contains API keys and credentials
- `data/` - Database data
- `logs/` - Application logs
- `secrets/` - Secret files (if created)

## Notes

1. **Blablador API Key**: Currently configured for Helmholtz Blablador service
2. **LiteLLM**: Routes to Ollama (local) or Blablador (cloud) based on config
3. **FastAPI Priority**: Checks `use_blablador` flag to determine LLM source
4. **Chainlit**: Can access Neo4j directly if needed (credentials passed via env)

## Summary

✅ Optimized `.env` with clear mode selection  
✅ docker-compose.yml with profiles for different use cases  
✅ API config properly loads Blablador credentials  
✅ No API keys exposed in docker-compose.yml  
✅ `.env` protected by `.gitignore`  
✅ Clear documentation of each mode's requirements
