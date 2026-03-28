# Docker Setup Guide

Complete guide to running ItalianOllama with Docker.

## Prerequisites

- Docker 20.10+
- Docker Compose v2+
- 16GB+ RAM (for Ollama)

## Quick Start

```bash
# Clone and setup
cd ItalianOllama

# Create required secrets
mkdir -p secrets
openssl rand -base64 32 > secrets/neo4j_password.txt
openssl rand -base64 32 > secrets/webui_secret_key.txt

# Copy API key from .env
cp .env secrets/blablador_api_key.txt

# Start services
docker compose up -d

# Check status
docker compose ps
```

## Services

### OpenWebUI

Web-based user interface for interacting with LLMs.

- **Image**: `ghcr.io/open-webui/open-webui:main`
- **Port**: 8080
- **Features**:
  - Chat interface
  - Model selection
  - Admin panel

### Neo4j

Graph database for storing vocabulary and learning history.

- **Image**: `neo4j:5.26-community`
- **Ports**: 7474 (HTTP), 7687 (Bolt)
- **Plugins**: APOC
- **Volume**: `neo4j_data`

### Ollama

Local LLM inference server (optional, for local models).

- **Image**: `ollama/ollama:latest`
- **Port**: 11434
- **Volume**: `ollama_models`

### Language Service

Python API for language learning.

- **Build**: Local Dockerfile
- **Port**: 8000
- **User**: Non-root (UID 1000)

## Managing Services

### Start Services

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d neo4j

# Start with logs
docker compose up
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes all data)
docker compose down -v

# Stop specific service
docker compose stop neo4j
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f neo4j
docker compose logs -f openwebui

# Last 100 lines
docker compose logs --tail=100
```

### Access Containers

```bash
# Shell into language service
docker exec -it italianollama-language-service /bin/bash

# Shell into Neo4j
docker exec -it italianollama-neo4j bash

# Neo4j cypher-shell
docker exec -it italianollama-neo4j cypher-shell -u neo4j -p password
```

## Data Management

### Backup Neo4j

```bash
# Create backup
docker exec italianollama-neo4j neo4j-admin database dump neo4j --to-path=/backup

# Copy backup from container
docker cp italianollama-neo4j:/backup ./backup
```

### Restore Neo4j

```bash
# Copy backup to container
docker cp ./backup italianollama-neo4j:/restore

# Stop Neo4j
docker compose stop neo4j

# Restore
docker exec italianollama-neo4j neo4j-admin database load neo4j --from-path=/restore

# Start Neo4j
docker compose start neo4j
```

### Ollama Models

```bash
# Pull a model
docker exec italianollama-ollama ollama pull llama3.2

# List models
docker exec italianollama-ollama ollama list

# Remove a model
docker exec italianollama-ollama ollama rm llama3.2
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs service_name

# Check resource usage
docker stats

# Check ports
netstat -tlnp | grep port
```

### Neo4j Issues

```bash
# Check Neo4j status
docker exec italianollama-neo4j cypher-shell -u neo4j -p password "RETURN 1"

# View Neo4j logs
docker compose logs neo4j
```

### Ollama Issues

```bash
# Check Ollama logs
docker compose logs ollama

# Test Ollama API
curl http://localhost:11434/api/tags
```

## Production Considerations

### Resource Allocation

Adjust in docker-compose.yml based on your hardware:

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 16G  # More for larger models
          cpus: '8'    # More cores for faster inference
```

### Security Hardening

1. Change default Neo4j password
2. Enable Neo4j authentication
3. Use reverse proxy for SSL
4. Configure firewall rules

### Monitoring

Add monitoring with Prometheus/Grafana:

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```
