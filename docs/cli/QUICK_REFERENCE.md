# Docker Compose CLI Quick Reference

## Installation

```bash
# Check Docker
python cli.py docker helpers check
```

## Common Tasks

### Start Services

```bash
# All services (local profile)
python cli.py docker up

# Specific profile
python cli.py docker up --profile cloud

# Specific services
python cli.py docker up --services fastapi
```

### Stop Services

```bash
# All services
python cli.py docker down

# Specific services
python cli.py docker down --services chainlit

# Remove volumes
python cli.py docker down --volumes
```

### Status & Logs

```bash
# Status
python cli.py docker status

# Logs (last 100 lines)
python cli.py docker logs fastapi --tail 100

# Follow logs
python cli.py docker logs fastapi --follow
```

### Helpers

```bash
# Check Docker
python cli.py docker helpers check

# Validate config
python cli.py docker helpers validate --profile local

# Rebuild images
python cli.py docker helpers rebuild

# Prune (cleanup)
python cli.py docker helpers prune
```

## Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| local | ollama, litellm, neo4j, fastapi, chainlit | Full local deployment |
| cloud | neo4j, fastapi, chainlit | External LLM |
| blablador-only | neo4j, fastapi, chainlit | Direct Blablador API |
| aura | fastapi, chainlit | Neo4j Cloud |

## Commands

| Command | Description |
|---------|-------------|
| `up` | Start services |
| `down` | Stop services |
| `ps` | List services |
| `restart` | Restart services |
| `status` | Show status |
| `logs` | View logs |
| `wait` | Wait for healthy |

## Options

| Option | Description |
|--------|-------------|
| `--profile` | Select profile (local/cloud/blablador-only/aura) |
| `--services` | Target specific services |
| `--volumes` | Remove volumes (down only) |
| `--tail` | Number of log lines |
| `--follow` | Follow logs in real-time |
| `--timeout` | Timeout in seconds |

## Environment

Set in `.env` file:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=yourpass
USE_AURA=false
BLABLADOR_API_KEY=yourkey
API_PORT=8000
```

## Directory

```
src/italianollama/cli/
├── docker_helpers.py  # Reusable helpers
├── compose.py         # Docker commands
└── services.py        # Local services

compose_cli.py         # Standalone CLI
```

## Next Steps

1. Start services: `python cli.py docker up`
2. Check status: `python cli.py docker status`
3. View logs: `python cli.py docker logs fastapi`
4. Troubleshoot: `python cli.py docker helpers check`

For more details: [CLI README](README.md)
