# CLI Quick Start Guide

This guide provides a quick introduction to using the Docker Compose CLI for managing ItalianOllama services.

## Installation

Verify Docker and Docker Compose are installed:

```bash
python cli.py docker helpers check
```

## Common Operations

### Start Services

```bash
# Start all services (default: local profile)
python cli.py docker up

# Start with specific profile
python cli.py docker up --profile cloud
python cli.py docker up --profile aura
```

### Check Status

```bash
# View running services
python cli.py docker ps

# View status summary
python cli.py docker status
```

### View Logs

```bash
# View last 100 lines of logs
python cli.py docker logs fastapi --tail 100

# Follow logs in real-time
python cli.py docker logs fastapi --follow
```

### Stop Services

```bash
# Stop all services
python cli.py docker down

# Stop and remove volumes
python cli.py docker down --volumes
```

### Helper Commands

```bash
# Check Docker installation
python cli.py docker helpers check

# Validate configuration
python cli.py docker helpers validate --profile local

# Rebuild images after code changes
python cli.py docker helpers rebuild

# Cleanup stopped containers
python cli.py docker helpers prune
```

## Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `local` | ollama, litellm, neo4j, fastapi, chainlit | Full local deployment (offline) |
| `cloud` | neo4j, fastapi, chainlit | External LLM (Blablador) |
| `blablador-only` | neo4j, fastapi, chainlit | Direct Blablador API |
| `aura` | fastapi, chainlit | Neo4j Cloud |

## Service Names

| Service Name | Purpose |
|--------------|---------|
| `fastapi` | Backend API |
| `chainlit` | Chat interface |
| `streamlit` | Dashboard |
| `ollama` | Local LLM (local profile) |
| `litellm` | LLM proxy |
| `neo4j` | Database |
| `nginx` | Reverse proxy |

## Common Workflows

### Development

```bash
# Start services
python cli.py docker up --profile local

# Check status
python cli.py docker status

# After code changes, rebuild
python cli.py docker helpers rebuild --services fastapi

# Restart services
python cli.py docker restart --profile local

# View logs
python cli.py docker logs fastapi --follow
```

### Production

```bash
# Validate configuration
python cli.py docker helpers validate --profile cloud

# Start services
python cli.py docker up --profile cloud

# Wait for services to be healthy
python cli.py docker wait fastapi chainlit --timeout 120

# Check status
python cli.py docker status
```

### Troubleshooting

```bash
# Check Docker installation
python cli.py docker helpers check

# Validate configuration
python cli.py docker helpers validate --profile local

# View logs
python cli.py docker logs fastapi --tail 500

# Restart problematic service
python cli.py docker restart --services fastapi

# Prune and restart
python cli.py docker helpers prune
python cli.py docker up --profile local
```

## Getting Help

```bash
# View all commands
python cli.py docker --help

# View specific command help
python cli.py docker up --help
python cli.py docker helpers check --help
```

## Next Steps

- Read the full [CLI README](cli/README.md) for detailed documentation
- Check [troubleshooting](troubleshooting/common-issues.md) for common issues
- See [deployment/docker.md](deployment/docker.md) for Docker specifics
- Review [architecture](architecture/overview.md) to understand the system
