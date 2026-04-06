# Neo4j Configuration Guide

**Date**: April 6, 2026  
**Purpose**: Configure Neo4j connections for different deployment modes

## Overview

ItalianOllama supports three Neo4j configuration modes:

1. **Local Development** - Neo4j Docker container (recommended for development)
2. **Neo4j Aura (Cloud)** - Managed Neo4j cloud service
3. **Mixed Mode** - Local Docker with remote Aura (not currently supported)

## Configuration Files

### Root `.env` File

Location: `/home/jhe24/ItalianOllama/.env`

This file contains credentials used by local development tools and some services.

### Backend `.env` File

Location: `/home/jhe24/ItalianOllama/backend/.env`

This file contains credentials used by Docker services. It overrides root `.env` values when running via `docker compose`.

## Local Development Configuration

### Prerequisites

- Docker installed and running
- Neo4j Docker image available

### Configuration

**Root `.env`**:
```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
NEO4J_DATABASE=neo4j
NEO4J_BOLT_PORT=7688
NEO4J_HTTP_PORT=7475
```

**Backend `.env`**:
```env
USE_AURA=false
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
NEO4J_DATABASE=neo4j
```

### Docker Ports

The Docker Compose configuration maps container ports to host ports:

- **Container**: `7687` (BOLT) → **Host**: `7688`
- **Container**: `7474` (HTTP) → **Host**: `7475`

This avoids conflicts with any locally installed Neo4j instance.

## Neo4j Aura Configuration

### Prerequisites

- Neo4j Aura account
- Active Aura instance

### Configuration

**Root `.env`**:
```env
NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password
NEO4J_DATABASE=your_database_id
NEO4J_BOLT_PORT=7687
NEO4J_HTTP_PORT=7474
```

**Backend `.env`**:
```env
USE_AURA=true
NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password
NEO4J_DATABASE=your_database_id
```

### Important Notes

1. Wait 60 seconds after Aura instance creation before connecting
2. The connection URI must use `neo4j+s://` protocol
3. Credentials must match what's configured in the Aura dashboard
4. Network access must be enabled for your IP range in Aura

## Switching Between Modes

### From Local to Aura

1. Update both `.env` files with Aura credentials
2. Set `USE_AURA=true` in both files
3. Rebuild and restart Docker:
   ```bash
   cd /home/jhe24/ItalianOllama/backend
   docker compose down
   docker compose build --no-cache fastapi
   docker compose up -d
   ```

### From Aura to Local

1. Update both `.env` files with local credentials
2. Set `USE_AURA=false` in both files
3. Rebuild and restart Docker:
   ```bash
   cd /home/jhe24/ItalianOllama/backend
   docker compose down
   docker compose build --no-cache fastapi
   docker compose up -d
   ```

## Troubleshooting

### Connection Refused

**Error**: `Neo.ClientError.Security.Unauthorized`  
**Cause**: Wrong password or authentication failure  
**Solution**: Verify `NEO4J_PASSWORD` matches the container's `NEO4J_AUTH` environment variable

### Host Unreachable

**Error**: Connection timeout to `bolt://neo4j:7687`  
**Cause**: Service not running or wrong URI  
**Solution**: 
```bash
docker ps | grep neo4j
docker logs italian-tutor-neo4j
```

### Incorrect Credentials

**Error**: `The client is unauthorized due to authentication failure`  
**Solution**: Ensure both `.env` files have the same credentials and they match the container configuration.

### Port Conflicts

**Error**: `Address already in use` for port 7687 or 7474  
**Cause**: Local Neo4j instance running  
**Solution**: 
1. Stop local Neo4j, or
2. Use different ports in Docker Compose:
   ```yaml
   ports:
     - "7688:7687"
     - "7475:7474"
   ```

## Docker Container Environment

The FastAPI container loads Neo4j credentials from:

1. `docker-compose.yml` environment variables (defaults)
2. `env_file: ../.env` (overrides)

Verify loaded values:
```bash
docker exec italian-tutor-api env | grep NEO4J
```

Expected output:
```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
NEO4J_BOLT_PORT=7688
NEO4J_HTTP_PORT=7475
```

## Security Best Practices

1. **Never commit `.env` files** to version control (already in `.gitignore`)
2. **Use strong passwords** for Neo4j containers
3. **Restrict Aura IP access** to your development machines only
4. **Rotate credentials** periodically
5. **Use separate databases** for development and production

## Related Documentation

- [GraphRecursionError Fix](./GRAPH_RECURSION_FIX.md)
- [Neo4j Best Practices](../NEO4J_BEST_PRACTICES.md)
- [Developer Quick Reference](../DEVELOPER_QUICK_REFERENCE.md)
