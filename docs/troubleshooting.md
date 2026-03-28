# Troubleshooting Guide

Solutions to common issues with ItalianOllama.

## Docker Issues

### Container Won't Start

**Symptoms:** Container exits immediately after starting

**Solutions:**
```bash
# Check logs
docker compose logs service_name

# Check port conflicts
netstat -tlnp | grep port

# Remove old containers
docker compose down
docker system prune
```

### Out of Memory

**Symptoms:** OOM errors, containers restarting

**Solutions:**
```bash
# Check memory usage
docker stats

# Increase swap
sudo swapon --size=8G

# Reduce Ollama memory in docker-compose.yml
```

### Port Already in Use

**Symptoms:** "Port is already allocated" error

**Solutions:**
```bash
# Find what's using the port
lsof -i :8080

# Stop the conflicting service
sudo systemctl stop service_name

# Or change the port in docker-compose.yml
```

## Neo4j Issues

### Can't Connect to Neo4j

**Symptoms:** Connection refused errors

**Solutions:**
```bash
# Check Neo4j is running
docker compose ps neo4j

# Check logs
docker compose logs neo4j

# Wait for startup (can take 30+ seconds)
docker compose logs neo4j | grep "Started."

# Test connection
docker exec italianollama-neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

### Authentication Failed

**Symptoms:** "Authentication failed" errors

**Solutions:**
```bash
# Check password in secrets file
cat secrets/neo4j_password.txt

# Recreate password if needed
openssl rand -base64 32 > secrets/neo4j_password.txt

# Restart Neo4j
docker compose restart neo4j
```

### Neo4j Browser Blank

**Symptoms:** Neo4j browser loads but shows blank screen

**Solutions:**
```bash
# Use different browser
# Chrome often has issues, try Firefox

# Or access via HTTP API
curl -u neo4j:password http://localhost:7474/db/neo4j/tx/commit \
  -H 'Content-Type: application/json' \
  -d '{"statements": [{"statement": "RETURN 1"}]}'
```

## LLM/Blablador Issues

### "Model not found" Error

**Symptoms:** LLM returns model not found

**Solutions:**
```bash
# Check available models
poetry run hellm models

# Verify API key
echo $BLABLADOR_API_KEY

# Test API directly
curl -H "Authorization: Bearer $BLABLADOR_API_KEY" \
  https://api.helmholtz-blablador.fz-juelich.de/v1/models
```

### API Key Not Found

**Symptoms:** "Blablador API key must be set"

**Solutions:**
```bash
# Check .env file exists
ls -la .env

# Verify content
cat .env | grep BLABLADOR

# Load dotenv manually
poetry run python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('BLABLADOR_API_KEY'))"

# Check variable name (hellmholtz uses BLABLADOR_API_BASE, not BLABLADOR_API_URL)
# Make sure both are in .env
```

### Slow Responses

**Symptoms:** LLM requests take very long

**Solutions:**
```bash
# Check network latency
ping api.helmholtz-blablador.fz-juelich.de

# Try faster model
# alias-fast is quicker than alias-large

# Check for rate limiting
docker compose logs language-service | grep "rate limit"
```

### Token Limit Errors

**Symptoms:** "exceeds maximum context"

**Solutions:**
- Use shorter prompts
- Reduce conversation history
- Switch to model with larger context
- Clear session to reset context

## Python/API Issues

### Module Not Found

**Symptoms:** "No module named 'italianollama'"

**Solutions:**
```bash
# Install in development mode
poetry install

# Or add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### Import Errors

**Symptoms:** Circular imports or missing dependencies

**Solutions:**
```bash
# Reinstall dependencies
poetry install

# Update lock file
poetry lock --no-update
poetry install

# Check Python version
python --version  # Should be 3.10+
```

### Tests Failing

**Symptoms:** pytest errors

**Solutions:**
```bash
# Run with verbose output
poetry run pytest -v

# Skip integration tests
poetry run pytest -m "not integration"

# Check test output for specific errors
```

## Ollama Issues (if used)

### Ollama Not Responding

**Symptoms:** Connection timeout to Ollama

**Solutions:**
```bash
# Check Ollama logs
docker compose logs ollama

# Pull required model
docker exec italianollama-ollama ollama pull llama3.2

# List available models
docker exec italianollama-ollama ollama list

# Test API
curl http://localhost:11434/api/tags
```

### Model Not Available

**Symptoms:** Specific model not found

**Solutions:**
```bash
# Pull the model
docker exec italianollama-ollama ollama pull modelname

# Check available models
docker exec italianollama-ollama ollama list
```

## OpenWebUI Issues

### Can't Connect to Ollama

**Symptoms:** OpenWebUI shows connection error

**Solutions:**
```bash
# Check Ollama is healthy
docker compose ps ollama

# Check environment variable
docker compose exec openwebui env | grep OLLAMA

# Restart OpenWebUI
docker compose restart openwebui
```

### Login Issues

**Symptoms:** Can't log in to OpenWebUI

**Solutions:**
```bash
# Check secret key
cat secrets/webui_secret_key.txt

# Disable signup check (for admin creation)
# Edit docker-compose.yml and add: ENABLE_SIGNUP=true

# Or create user via CLI
docker exec -it italianollama-openwebui /bin/bash
# Then create admin user
```

## Getting Help

### Collect Debug Information

```bash
# System info
uname -a
docker --version
docker compose version

# Container status
docker compose ps

# Relevant logs
docker compose logs --tail=100 > debug.log

# Environment
env | grep -E "BLABLADOR|NEO4J|OLLAMA" > env.log
```

### Report Issues

When reporting issues, include:
1. Output of `docker compose ps`
2. Relevant logs from `docker compose logs`
3. Your .env (without secrets)
4. Steps to reproduce
