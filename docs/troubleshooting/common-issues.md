# Common Issues & Troubleshooting

This guide covers common issues you may encounter with ItalianOllama and how to resolve them.

## Quick Diagnosis

If you're experiencing issues, check these first:

1. **Are all services running?**
   ```bash
   docker compose ps
   ```

2. **Is the API healthy?**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Are logs showing errors?**
   ```bash
   docker compose logs --tail=50
   ```

## Docker Issues

### Services Not Starting

**Symptom:** Docker containers fail to start

**Diagnosis:**
```bash
docker compose logs
```

**Solutions:**
- Check if ports are already in use
- Verify `.env` file exists and is valid
- Ensure Docker has enough resources

**Fix:**
```bash
# Check port usage
lsof -i :8000
lsof -i :8501

# Restart services
docker compose down
docker compose up -d
```

### Neo4j Connection Failed

**Symptom:** "Connection to Neo4j failed"

**Diagnosis:**
```bash
docker logs neo4j
docker exec neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

**Solutions:**
- Verify Neo4j is running
- Check credentials in `.env`
- Wait for Neo4j to fully start (can take 30s)

**Fix:**
```bash
# Wait for Neo4j
sleep 30

# Or restart
docker compose restart neo4j
```

### Port Already in Use

**Symptom:** "Port is already allocated"

**Fix:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

## API Issues

### Health Check Failing

**Symptom:** `/health` returns unhealthy status

**Diagnosis:**
```bash
curl http://localhost:8000/health
docker compose logs api
```

**Solutions:**

1. **Neo4j not connected:**
   ```bash
   # Check Neo4j
   docker compose ps neo4j
   docker logs neo4j
   ```

2. **LiteLLM not connected:**
   ```bash
   # Check LiteLLM
   curl http://localhost:4000/health
   docker compose logs litellm
   ```

### API Returns 500 Error

**Symptom:** Internal server error

**Diagnosis:**
```bash
docker compose logs api | grep ERROR
```

**Common causes:**
- Invalid environment variables
- Neo4j query error
- LLM provider error

**Fix:**
```bash
# Check environment
docker compose exec api env | grep -E "NEO4J|LITELLM"

# Restart API
docker compose restart api
```

### Slow Response Times

**Symptom:** Chat takes very long to respond

**Solutions:**
1. Check LiteLLM logs for LLM delays
2. Increase timeout in nginx.conf
3. Check network between containers

```bash
# Test LiteLLM directly
time curl http://localhost:4000/health

# Check container network
docker network inspect italianollama_backend
```

## LLM Issues

### No Response from LLM

**Symptom:** Chat hangs or times out

**Diagnosis:**
```bash
docker compose logs litellm
curl http://localhost:4000/health
```

**Solutions:**

1. **Wrong API key:**
   ```bash
   # Verify key in .env
   cat .env | grep API_KEY
   ```

2. **Wrong model:**
   ```bash
   # Check model name
   curl http://localhost:4000/model/info
   ```

3. **Rate limiting:**
   ```bash
   # Wait and retry
   sleep 10
   ```

### Invalid API Key

**Symptom:** "Invalid API key" or authentication error

**Fix:**
```bash
# Update .env with correct key
nano .env

# Restart services
docker compose down
docker compose up -d
```

### Ollama Not Running

**Symptom:** Cannot connect to Ollama

**Fix:**
```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3.2

# Check
curl http://localhost:11434
```

## Frontend Issues

### Chainlit Not Loading

**Symptom:** Chat page shows error or blank

**Diagnosis:**
```bash
docker compose logs chainlit
curl http://localhost:8000
```

**Solutions:**
1. Check API is running
2. Check environment variables
3. Check WebSocket connection

**Fix:**
```bash
# Verify API
curl http://localhost:8000/health

# Restart Chainlit
docker compose restart chainlit
```

### Streamlit Not Loading

**Symptom:** Dashboard page shows error

**Diagnosis:**
```bash
docker compose logs streamlit
curl http://localhost:8501
```

**Solutions:**
1. Check API is accessible
2. Verify AUTH_SECRET matches
3. Check JWT token validity

### WebSocket Connection Failed

**Symptom:** Chat doesn't stream responses

**Diagnosis:**
```bash
# Check Nginx WebSocket headers
docker compose logs nginx | grep upgrade
```

**Fix:**
```nginx
# Ensure Nginx has WebSocket headers
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### Components Not Rendering

**Symptom:** Interactive components don't appear

**Solutions:**
1. Check browser console for errors
2. Verify SSE stream format
3. Check component registry

```bash
# Test SSE manually
curl -N http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}],"stream":true}'
```

## Authentication Issues

### JWT Token Invalid

**Symptom:** "Invalid token" error

**Diagnosis:**
```python
# Check token
import jwt
token = "your_token"
jwt.decode(token, "secret", algorithms=["HS256"])
```

**Solutions:**
1. Verify AUTH_SECRET matches
2. Check token expiration
3. Regenerate token

### Session Not Persisting

**Symptom:** Must log in repeatedly

**Fix:**
```bash
# Check AUTH_SECRET is set
echo $AUTH_SECRET

# Clear session cache
rm -rf .streamlit
```

### OAuth Not Working

**Symptom:** Google login fails

**Solutions:**
1. Check OAuth credentials
2. Enable dev mode for testing
3. Check redirect URIs

```bash
# Dev mode
DISABLE_OAUTH=true
```

## Database Issues

### Neo4j Query Timeout

**Symptom:** Slow database queries

**Fix:**
```cypher
# Add index
CREATE INDEX student_id_idx FOR (s:Student) ON (s.student_id);
CREATE INDEX vocab_word_idx FOR (v:Vocabulary) ON (v.word);
```

### Database Full

**Symptom:** "Neo4j out of memory"

**Fix:**
```bash
# Increase memory in docker-compose.yml
neo4j:
  environment:
    - NEO4J_dbms_memory_heap_max__size=2G
```

### Data Migration Issues

**Symptom:** Old data not appearing

**Fix:**
```bash
# Check data
docker exec neo4j cypher-shell -u neo4j -p password "MATCH (n) RETURN count(n)"

# Clear cache
docker exec neo4j cypher-shell -u neo4j -p password "CALL db.clearQueryCaches()"
```

## Browser Issues

### CORS Errors

**Symptom:** "CORS policy" error in console

**Fix:**
```python
# Add CORS in FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Cache Issues

**Symptom:** Old content showing

**Fix:**
```bash
# Clear browser cache
# Or use incognito mode

# Clear Streamlit cache
rm -rf ~/.streamlit
rm -rf .streamlit
```

## Performance Issues

### High Memory Usage

**Symptom:** System running slow

**Fix:**
```bash
# Check Docker usage
docker stats

# Restart services
docker compose restart
```

### Slow Loading

**Symptom:** Pages take long to load

**Solutions:**
1. Check API response times
2. Enable caching in Streamlit
3. Check Neo4j query performance

```bash
# Profile API
time curl http://localhost:8000/health

# Check slow queries
docker exec neo4j cypher-shell -u neo4j -p password "CALL dbms.listQueries()"
```

## Getting Help

### Collect Debug Info

```bash
# Create debug bundle
docker compose logs > logs.txt
docker compose ps > services.txt
docker exec neo4j cypher-shell -u neo4j -p password "CALL dbms.procedures()" > procedures.txt
```

### Check System Resources

```bash
# CPU and memory
htop

# Disk space
df -h

# Docker disk usage
docker system df
```

## Related Documentation

- [Installation Guide](../getting-started/installation.md)
- [Configuration Guide](../getting-started/configuration.md)
- [Debugging Guide](../development/debugging.md)
- [FAQ](faq.md)
