# GraphRecursionError Fix

**Date**: April 6, 2026  
**Issue**: LangGraph hitting recursion limit of 100 without stopping  
**Status**: Resolved

## Problem Description

The ItalianOllama API service was returning a `GraphRecursionError` with the message:

```
GraphRecursionError: Recursion limit of 100 reached without hitting a stop condition.
```

This occurred when the LangGraph tutor workflow ran, indicating that the graph was not stopping correctly after chat responses.

## Root Cause Analysis

The issue was in the `placement_node` function located at:
- `src/italianollama/graph/nodes/placement.py`

### Issues Found

1. **Missing `should_continue=False` assignments**: The `placement_node` function had multiple code paths where it didn't set `should_continue=False`, causing the graph to continue indefinitely.

2. **Syntax error in placement.py**: The container had an old cached version of `placement.py` with:
   - Improper indentation on the `if len(messages) <= 1:` block
   - An orphaned `else:` statement causing Python syntax error

3. **Incomplete state management**: The placement node was not setting `current_level` in all execution paths, which could cause routing loops.

### Code Flow That Caused Infinite Loop

```
User message → router → placement_node → (no should_continue=False) → router → placement_node → ...
```

The graph structure has all nodes (including `chat`) edge back to `router`. The conditional edges use `router_decision` to determine where to go, with `"__end__": "__end__"` stopping the graph. Without `should_continue=False` being set, the router would always route back.

## Solution

### Code Changes

Updated `src/italianollama/graph/nodes/placement.py` to ensure `should_continue=False` is set in **all** code paths.

See the file for the exact implementation details.

### Docker Configuration Changes

Fixed Neo4j authentication issues:

**`.env` (root)**: Updated to use local Docker Neo4j
```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=JbAl2SE5yvUavfe+D3zgzgtgd50Lgn2oAimCCKmdRoc=
NEO4J_DATABASE=neo4j
```

**`backend/.env`**: Updated to use local Docker Neo4j
```env
USE_AURA=false
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=JbAl2SE5yvUavfe+D3zgzgtgd50Lgn2oAimCCKmdRoc=
NEO4J_DATABASE=neo4j
```

### Docker Commands Used

```bash
# Stop all services
cd /home/jhe24/ItalianOllama/backend
docker compose down

# Rebuild FastAPI container with fixes
docker compose build --no-cache fastapi

# Start all services
docker compose up -d

# Verify configuration
docker exec italian-tutor-api env | grep NEO4J

# Check logs for issues
docker logs italian-tutor-api --tail 50
```

## Verification

### Test Results

1. **Health endpoint**: Working
   ```
   curl http://localhost:8000/health
   {"status":"ok","neo4j":"connected","litellm":"unreachable"}
   ```

2. **Chat endpoint**: Working without recursion error
   ```json
   {
       "response": "Mi dispiace, non ho capito. Puoi ripetere?",
       "session_id": "newstudent999",
       "student_level": "A1"
   }
   ```

3. **Logs verification**: Correct behavior
   ```
   ROUTER DEBUG: Set router_decision=placement
   PLACEMENT DEBUG: Final should_continue=False, current_level=A1
   ROUTER DEBUG: should_continue=False, setting router_decision to __end__
   ```

### Key Log Messages

- `should_continue=False` is set in placement_node
- Router sees `should_continue=False` and routes to `__end__`
- No recursion errors after 10+ test requests

## Prevention

To prevent similar issues:

1. **Always ensure `should_continue=False`** is set in all node execution paths
2. **Use linters** to catch syntax errors before deployment
3. **Add tests** for graph nodes to verify they stop correctly
4. **Monitor logs** for recursion-related debug messages

## Files Modified

1. `src/italianollama/graph/nodes/placement.py` - Fixed `should_continue` assignment
2. `/home/jhe24/ItalianOllama/.env` - Updated Neo4j URI for local development
3. `/home/jhe24/ItalianOllama/backend/.env` - Updated Neo4j URI for local development

## Related Documentation

- [Architecture Overview](../architecture/)
- [Neo4j Best Practices](../NEO4J_BEST_PRACTICES.md)
- [Developer Quick Reference](../DEVELOPER_QUICK_REFERENCE.md)
