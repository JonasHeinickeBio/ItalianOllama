# Chainlit-Streamlit Integration Guide

## Quick Summary of Improvements

✅ **Backend Reliability**: Chainlit now retries health checks (3 attempts) and falls back to demo mode if backend unavailable
✅ **Config Flow**: student_id, level, and name now pass from Streamlit → Chainlit via URL query parameters
✅ **Data Persistence**: All chat messages automatically stored in Neo4j with timestamps
✅ **Error Recovery**: Exponential backoff retry logic in API client (1s, 2s, 4s delays)
✅ **Fallback Mode**: Works offline with demo profile if backend unreachable

## Environment Setup

### Required Environment Variables

```bash
# Backend
export BACKEND_URL=http://localhost:8000
export BACKEND_TIMEOUT=120

# Neo4j
export NEO4J_URI=neo4j://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
export NEO4J_DATABASE=neo4j

# Chainlit / Streamlit
export CHAINLIT_URL=http://localhost:8000
export CHAINLIT_ENABLED=true
export DEFAULT_STUDENT_ID=demo
```

### Or Create .env File

```ini
# .env in project root

# Backend
BACKEND_URL=http://localhost:8000
BACKEND_TIMEOUT=120

# Neo4j
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# Chainlit / Streamlit
CHAINLIT_URL=http://localhost:8000
CHAINLIT_ENABLED=true
DEFAULT_STUDENT_ID=demo
```

## Running the System

### Terminal 1: Neo4j Database

```bash
docker-compose up neo4j
# Or if using local installation:
# neo4j start
```

### Terminal 2: Backend FastAPI

```bash
cd /home/jhe24/ItalianOllama
poetry run python -m italianollama.api.main
# Or with uvicorn directly:
# poetry run uvicorn italianollama.api.main:app --reload --port 8000
```

### Terminal 3: Chainlit Frontend

```bash
cd /home/jhe24/ItalianOllama
poetry run chainlit run src/italianollama/frontend/chainlit_app.py \
  --port 8000 --host 0.0.0.0
```

### Terminal 4: Streamlit Frontend

```bash
cd /home/jhe24/ItalianOllama
poetry run streamlit run src/italianollama/frontend/streamlit/pages/01_home.py \
  --logger.level=debug
```

Then open: http://localhost:8501

Click "Chat con Sofia 💬" (or navigate to /chat page)

## Testing Scenarios

### Scenario 1: Normal Operation (All Services Running)

1. Start all services (Neo4j, Backend, Chainlit, Streamlit)
2. In Streamlit, click "🚀 Usa Chainlit (Avanzato)" toggle
3. Chainlit iframe loads
4. Send a message: "Ciao! Come stai?"
5. Check Neo4j for ChatMessage nodes:
   ```cypher
   MATCH (s:Student)-[:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
   RETURN msg
   LIMIT 5
   ```

### Scenario 2: Backend Temporarily Unavailable

1. Start Streamlit and Chainlit only (stop Backend/FastAPI)
2. In Streamlit, toggle "🚀 Usa Chainlit"
3. Chainlit should show fallback greeting with warning:
   ```
   🔌 Ciao! Sono Sofia, la tua tutor di italiano.

   ⚠️ Modalità demo: alcuni dati potrebbero non essere salvati.
   ```
4. Chat history stored in session memory only (not persisted to Neo4j)

### Scenario 3: Retry Logic in Action

1. Start Backend service but **make it slow** (e.g., add network delay):
   ```bash
   # On macOS: Add 1 second latency to localhost:8000
   sudo ipfw pipe 1 config delay 1000ms
   sudo ipfw add 100 pipe 1 src-ip 127.0.0.1 dst-port 8000
   ```
2. Trigger a student creation call
3. Watch logs for retry attempts:
   ```
   WARNING: get_student_profile(demo) attempt 1/3 failed, retrying in 1s: ...
   WARNING: get_student_profile(demo) attempt 2/3 failed, retrying in 2s: ...
   INFO: Student profile retrieved: demo
   ```

### Scenario 4: Config Parameter Passing

1. In Streamlit, toggle "🚀 Usa Chainlit"
2. Look at browser dev tools (F12 → Network tab)
3. Find the iframe src URL - should be:
   ```
   http://localhost:8000?student_id=demo&level=A1&name=Student+demo
   ```
4. In Chainlit logs, verify extraction:
   ```
   INFO: Found student_id in query params: demo
   ```

## Debugging Tips

### Check Chainlit Logs

```bash
# Verbose logging
CHAINLIT_DEBUG=true poetry run chainlit run src/italianollama/frontend/chainlit_app.py

# Or set in app:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Neo4j Chat Persistence

```cypher
# All chat messages for a student
MATCH (s:Student {student_id: "demo"})-[:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
RETURN msg, s
ORDER BY msg.timestamp DESC
LIMIT 10

# Count messages per student
MATCH (s:Student)-[r:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
RETURN s.student_id, count(msg) AS message_count
ORDER BY message_count DESC

# Message stats
MATCH (s:Student {student_id: "demo"})-[:HAS_CHAT_MESSAGE]->(msg:ChatMessage)
RETURN {
  count: count(msg),
  avg_user_len: round(avg(size(msg.user_content))),
  avg_assistant_len: round(avg(size(msg.assistant_content))),
  latest: max(msg.timestamp)
}
```

### Monitor Backend Health

```bash
# Quick health check
curl -s http://localhost:8000/health | jq .

# Check if Neo4j is reachable by backend
curl -s http://localhost:8000/health | jq .neo4j
```

### Verify Student Creation

```bash
# Create student via API
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{"student_id": "test_user", "name": "Test User"}'

# Verify in Neo4j
cypher-shell -u neo4j -p password \
  "MATCH (s:Student {student_id: 'test_user'}) RETURN s"
```

## Architecture Diagram

```
┌─────────────────┐
│  Streamlit UI   │
│  (03_chat.py)   │
└────────┬────────┘
         │ iframe with query params
         │ ?student_id=demo&level=A1
         ↓
┌─────────────────────────┐
│    Chainlit App         │
│  (chainlit_app.py)      │
├─────────────────────────┤
│ Health check (3 retries)│
│ Session Manager         │
│ Message Handler         │
└────┬──────────┬─────────┘
     │          │
     ↓ HTTP     ↓ Async Neo4j
┌─────────┐  ┌──────────────────┐
│ Backend │  │ Neo4j Database   │
│ (8000)  │  │ ChatMessage      │
└─────────┘  │ HAS_CHAT_MESSAGE │
             └──────────────────┘
```

## Common Issues & Fixes

### "Backend availability check failed"

**Cause**: Health check endpoint unreachable

**Fix**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check firewall: `lsof -i :8000` (should show service listening)
3. Verify env var: `echo $BACKEND_URL`

### "Failed to create student: demo"

**Cause**: Backend not creating student in Neo4j

**Fix**:
1. Check Neo4j is running: `cypher-shell -u neo4j -p password "RETURN 1"`
2. Check backend logs for Neo4j connection errors
3. Verify Student node creation with: `MATCH (s:Student) RETURN count(s)`

### "Chainlit not available on http://localhost:8000"

**Cause**: Chainlit service not running on expected port

**Fix**:
1. Start Chainlit: `chainlit run src/italianollama/frontend/chainlit_app.py --port 8000`
2. Verify: `curl http://localhost:8000`
3. Check that backend isn't running on same port

### Messages not persisting to Neo4j

**Cause**: Chat persistence disabled or Neo4j unreachable

**Fix**:
1. Verify Neo4j config in frontend/config.py
2. Check logs for "Failed to persist chat to Neo4j" warnings
3. Verify Neo4j connection: `cypher-shell "RETURN 1"`
4. Manually test: `client.save_chat_message(student_id, msg1, msg2)`

## Performance Tuning

### Increase Retry Timeout for Slow Networks

```python
# In frontend/api/client.py
client = BackendClient(timeout=60.0, max_retries=5)  # 5 retries instead of 3
```

### Optimize Chat Persistence

```python
# In chainlit_app.py - make persistence truly non-blocking
import asyncio

try:
    # Fire-and-forget chat persistence
    asyncio.create_task(_persist_chat_message_to_neo4j(...))
except Exception:
    pass  # Log but don't block
```

### Monitor Retry Metrics

```bash
# Watch logs for retry attempts
poetry run chainlit run src/italianollama/frontend/chainlit_app.py 2>&1 | grep "attempt"
```

## Next Steps

1. **Session Synchronization**: Sync Streamlit and Chainlit session state
2. **Chat History UI**: Display Neo4j chat history in Streamlit
3. **Analytics**: Show conversation stats per student
4. **Circuit Breaker**: Auto-disable features when backend repeatedly fails
5. **Metrics Export**: Prometheus metrics for retry counts, persistence success rate
