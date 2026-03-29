# Debugging Guide

This guide covers common debugging techniques and tools for ItalianOllama.

## Logging

### Application Logging

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
```

### Configure Logging

```python
# src/italianollama/api/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Environment-Based Logging

```bash
# Development
LOG_LEVEL=DEBUG

# Production
LOG_LEVEL=INFO
```

## Common Issues

### Neo4j Connection Issues

**Problem:** Cannot connect to Neo4j

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check logs
docker logs neo4j

# Test connection manually
docker exec neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

**Solution:**
```python
# Verify URI format
NEO4J_URI=bolt://localhost:7687  # Not bolt+routing://

# Check authentication
NEO4J_PASSWORD=password  # Must match the set password
```

### LLM Connection Issues

**Problem:** LLM requests failing

```bash
# Check LiteLLM health
curl http://localhost:4000/health

# Test specific model
curl http://localhost:4000/model/info?tutor
```

**Debug LLM calls:**
```python
import litellm

# Enable verbose logging
litellm.set_verbose = True

# Test direct call
response = litellm.completion(
    model="tutor",
    messages=[{"role": "user", "content": "Ciao"}]
)
print(response)
```

### Frontend Connection Issues

**Problem:** Frontend cannot reach API

```bash
# Check API is running
curl http://localhost:8000/health

# Check Nginx logs
docker logs nginx

# Test WebSocket
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost/chat/
```

## Debugging Tools

### VS Code Debugging

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: API",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.italianollama.api.main:app", "--reload", "--log-level", "debug"],
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Chainlit",
      "type": "python",
      "request": "launch",
      "module": "chainlit",
      "args": ["run", "frontend/chainlit/chainlit_app.py", "--dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Print Debugging

For quick debugging in any Python file:

```python
# Add debug prints
import pprint

def debug_state(state):
    print("=== STATE DEBUG ===")
    pprint.pprint(state)
    print("===================")
```

### Using breakpoint()

```python
def some_function():
    result = calculate_something()
    breakpoint()  # Opens debugger
    return process_result(result)
```

In the debugger:
```
p result  # Print result
c        # Continue
n        # Next line
s        # Step into
```

## HTTP Debugging

### Using curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"student_id": "test", "message": "Ciao"}'

# Test with authentication
curl -X GET http://localhost:8000/students/test \
  -H "Authorization: Bearer <token>"
```

### Using httpie

```bash
# Install
pip install httpie

# Use
http GET localhost:8000/health

http POST localhost:8000/chat \
  student_id=test message=Ciao
```

## Database Debugging

### Neo4j Browser

Access at http://localhost:7474

```cypher
# View all students
MATCH (s:Student) RETURN s

# View student with relationships
MATCH (s:Student {student_id: 'test-123'})
OPTIONAL MATCH (s)-[r]->(n)
RETURN s, r, n

# View vocabulary
MATCH (s:Student)-[:KNOWS]->(v:Vocabulary)
WHERE s.student_id = 'test-123'
RETURN v

# Count nodes
MATCH (n) RETURN count(n)
```

### Debug Queries in Code

```python
def get_student_debug(self, student_id: str) -> dict:
    """Get student with debug info."""
    query = """
    MATCH (s:Student {student_id: $student_id})
    OPTIONAL MATCH (s)-[:HAS_LEVEL]->(l:CEFRLevel)
    RETURN s, l
    """
    
    result = self._run_query(query, student_id=student_id)
    
    # Debug: print raw result
    print(f"Raw query result: {result}")
    
    return result
```

## LangGraph Debugging

### Visualize Graph

```python
# Print graph structure
from src.italianollama.graph.graph import create_graph

graph = create_graph()
print(graph.get_graph().draw_ascii())
```

### Debug State Transitions

```python
from src.italianollama.graph.graph import create_graph

graph = create_graph()

# Enable debug tracing
from langgraph.callbacks import StdOutCallbackHandler

handler = StdOutCallbackHandler()

result = graph.invoke(
    initial_state,
    config={"callbacks": [handler]}
)
```

### Step Through Execution

```python
# Use graph.stream() for step-by-step execution
for step in graph.stream(initial_state):
    print(f"Step: {step}")
    # Inspect step at each node
```

## Docker Debugging

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api
```

### Access Container Shell

```bash
# Shell into API container
docker compose exec api sh

# Shell into Neo4j
docker compose exec neo4j cypher-shell
```

### Network Debugging

```bash
# Check network
docker network ls
docker network inspect italianollama_backend

# Test connectivity between containers
docker compose exec api ping litellm
```

## Testing in Debug Mode

### Chainlit Dev Mode

```bash
cd frontend/chainlit
CHAINLIT_DEV=true python -m chainlit run chainlit_app.py --dev
```

### Streamlit Dev Mode

```bash
cd frontend/streamlit
streamlit run app.py --logger.level=debug
```

### API with Auto-reload

```bash
cd backend
uvicorn src.italianollama.api.main:app --reload --log-level debug
```

## Performance Debugging

### Profile Code

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = graph.invoke(initial_state)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print(20)
```

### Time Operations

```python
import time

start = time.time()
result = some_operation()
elapsed = time.time() - start
print(f"Operation took {elapsed:.2f} seconds")
```

## Related Documentation

- [Setup Guide](setup.md)
- [Coding Standards](coding-standards.md)
- [Testing Guide](testing.md)
- [Troubleshooting](../troubleshooting/common-issues.md)
