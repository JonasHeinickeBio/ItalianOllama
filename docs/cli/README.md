# ItalianOllama CLI Documentation

A modular, scalable command-line interface for managing ItalianOllama services.

## Overview

The project includes two CLI systems:

### Docker Compose CLI

The **Docker Compose CLI** (`src/italianollama/cli/compose.py` and `docker_helpers.py`) provides:

1. **Docker Compose Management** - Start/stop/restart Docker services with profiles
2. **System Diagnostics** - Check Neo4j, LLM providers, and configuration
3. **Helper Commands** - Reusable helper functions for common tasks (prune, validate, rebuild, info)

### Local Service CLI

The **Local Service CLI** (`src/italianollama/cli/services.py`) provides:

1. **Service Management** - Start/stop/restart local Python services (FastAPI, Chainlit, Streamlit)

Both CLI systems integrate with the main `cli.py` entry point for unified access.

## Quick Start

```bash
# View all commands
python cli.py --help

# Docker Compose commands
python cli.py docker --help

# Local service commands
python cli.py service --help

# System check commands
python cli.py neo4j status
python cli.py llm test
python cli.py config show
```

## When to Use Docker vs Local Services

| Scenario | Command |
|----------|---------|
| Development with full local stack | `python cli.py docker up --profile local` |
| Development with external LLM | `python cli.py docker up --profile cloud` |
| Fast restart for code changes | `python cli.py docker restart` |
| Production deployment | `python cli.py docker up --profile cloud --build` |
| Quick testing of single service | `python cli.py service start api` |
| Debugging | `python cli.py docker logs fastapi --follow` |
| System diagnostics | `python cli.py docker helpers check` |

## Docker Compose Commands

### `docker up` - Start Services

```bash
# Start all services in local profile (default)
python cli.py docker up

# Start specific profile
python cli.py docker up --profile local
python cli.py docker up --profile cloud
python cli.py docker up --profile blablador-only
python cli.py docker up --profile aura

# Start specific services
python cli.py docker up --services fastapi --services chainlit

# Build images before starting
python cli.py docker up --build

# Run in foreground (no detach)
python cli.py docker up --no-detach
```

### `docker down` - Stop Services

```bash
# Stop all services
python cli.py docker down

# Stop specific profile
python cli.py docker down --profile local

# Stop specific services
python cli.py docker down --services fastapi

# Remove volumes (⚠️ destroys data!)
python cli.py docker down --volumes
```

### `docker ps` - List Services

```bash
# List all running services
python cli.py docker ps

# List services in specific profile
python cli.py docker ps --profile local
```

### `docker restart` - Restart Services

```bash
# Restart all services
python cli.py docker restart

# Restart specific profile
python cli.py docker restart --profile local

# Restart specific services
python cli.py docker restart --services fastapi
```

### `docker status` - Show Status

```bash
# Show status of all Docker Compose services
python cli.py docker status
```

### `docker logs` - View Logs

```bash
# View last 100 lines of fastapi logs
python cli.py docker logs fastapi --tail 100

# Follow logs in real-time
python cli.py docker logs fastapi --follow
```

### `docker wait` - Wait for Services

```bash
# Wait for services to become healthy (timeout: 60s)
python cli.py docker wait fastapi chainlit --timeout 120
```

## Docker Helpers

The `docker helpers` group provides diagnostic and maintenance commands:

### `docker helpers check` - Check Installation

```bash
# Verify Docker and Docker Compose are installed
python cli.py docker helpers check
```

### `docker helpers validate` - Validate Configuration

```bash
# Validate docker-compose.yml configuration
python cli.py docker helpers validate --profile local
```

### `docker helpers prune` - Clean Up

```bash
# Remove stopped containers and unused volumes
python cli.py docker helpers prune
```

### `docker helpers rebuild` - Rebuild Images

```bash
# Rebuild all images
python cli.py docker helpers rebuild

# Rebuild specific services
python cli.py docker helpers rebuild --services fastapi --services chainlit
```

### `docker helpers info` - System Information

```bash
# Show Docker and Docker Compose version
python cli.py docker helpers info
```

## Local Service Commands

### `service start` - Start Services

```bash
# Start all services
python cli.py service start all

# Start specific service
python cli.py service start api
python cli.py service start chainlit
python cli.py service start streamlit
```

### `service stop` - Stop Services

```bash
# Stop all services
python cli.py service stop all

# Stop specific service
python cli.py service stop api
```

### `service restart` - Restart Services

```bash
# Restart all services
python cli.py service restart all

# Restart with custom delay
python cli.py service restart api --delay 30
```

### `service status` - Show Status

```bash
# Show status of all local services
python cli.py service status
```

### `service logs` - View Logs

```bash
# View last 20 lines of logs
python cli.py service logs api --lines 20

# Follow logs
python cli.py service logs api --follow
```

## System Check Commands

### `neo4j status` - Database Status

```bash
# Check Neo4j connection
python cli.py neo4j status
```

### `llm test` - Test LLM Connection

```bash
# Test LLM provider connectivity
python cli.py llm test
```

### `config show` - Show Configuration

```bash
# Display current configuration
python cli.py config show
```

## Docker Profiles

### local (Default)
- Ollama (local LLM)
- LiteLLM (LLM proxy)
- Neo4j (local)
- FastAPI
- Chainlit

### cloud
- Neo4j (local)
- FastAPI
- Chainlit
- Uses external LLM (Blablador)

### blablador-only
- Neo4j (local)
- FastAPI
- Chainlit
- Direct Blablador API access

### aura
- FastAPI
- Chainlit
- Neo4j Aura (cloud)

## Customization

### Environment Variables

Create a `.env` file in the project root:

```bash
# Neo4j configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
USE_AURA=false

# LLM configuration
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your-key

# Port configuration
API_PORT=8000
CHAINLIT_PORT=8501
STREAMLIT_PORT=8502
```

## Directory Structure

```
src/italianollama/cli/
├── compose.py       # Docker Compose commands
├── docker_helpers.py # Docker helper functions (modular, reusable)
├── services.py      # Local service management
├── main.py          # Main CLI entry point (integrates docker and service groups)
├── __init__.py
└── __main__.py      # CLI package entry point

compose_cli.py       # Standalone Docker CLI (can run independently)
```

## Modular Architecture

The Docker Compose CLI was refactored to be **modular and helper-driven**:

- **`docker_helpers.py`** - Contains reusable helper functions that can be called from multiple commands
- **`compose.py`** - Contains docker group commands using decorators for consistent behavior
- **Separation of concerns** - Helper functions are independent of command structure

This architecture makes it easy to:
- Add new commands without duplicating logic
- Test helper functions independently
- Reuse helper functions across different commands
- Maintain consistent error handling and validation

## Contributing

To add new Docker Compose commands:

1. Add functions to `docker_helpers.py` for reusable logic
2. Add commands to `compose.py` with proper decorators
3. Use `@docker.command()` for main commands
4. Use `@helpers.command()` for utility commands
5. Add help text and click options

Example:

```python
@docker.command()
@docker_compose_wrapper
@click.option("--name", help="Service name")
def new_command(name):
    """Command description."""
    # Your implementation here
    pass
```

## Troubleshooting

### Docker not found
```bash
# Check Docker installation
python cli.py docker helpers check

# Install Docker: https://docs.docker.com/get-docker/
```

### Service already running
```bash
# Check status
python cli.py docker status

# Stop service first
python cli.py docker down --services <name>
```

### Port conflicts
```bash
# Check which ports are in use
python cli.py service status

# Modify ports in .env file
# API_PORT=8001
```

## License

MIT License

## License

MIT License
