# Testing Guide

This guide covers testing practices and patterns for ItalianOllama.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_graph/
│   │   ├── test_state.py
│   │   └── test_nodes/
│   │       ├── test_vocabulary.py
│   │       └── test_grammar.py
│   ├── test_api/
│   │   └── test_endpoints.py
│   └── test_memory/
│       └── test_neo4j_client.py
├── integration/             # Integration tests
│   ├── test_api_flow.py
│   └── test_graph_flow.py
└── fixtures/               # Test data
    ├── __init__.py
    └── sample_students.py
```

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=src --cov-report=html
```

### Specific Test File

```bash
pytest tests/unit/test_graph/test_nodes/test_vocabulary.py -v
```

### Watch Mode

```bash
pytest --watch
```

## Unit Tests

### Using Fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_neo4j():
    """Mock Neo4j client."""
    client = MagicMock()
    client.get_student.return_value = {
        "student_id": "test-123",
        "name": "Test User",
        "current_cefr": "B1"
    }
    return client

@pytest.fixture
def sample_student():
    """Sample student data."""
    return {
        "student_id": "test-123",
        "name": "Test User",
        "email": "test@example.com",
        "current_cefr": "B1"
    }
```

### Testing LangGraph Nodes

```python
# tests/unit/test_graph/test_nodes/test_vocabulary.py
import pytest
from src.italianollama.graph.state import TutorState
from src.italianollama.graph.nodes.vocabulary import vocabulary_node

def test_vocabulary_node_returns_flashcards(sample_student):
    """Test that vocabulary node returns flashcard exercises."""
    state: TutorState = {
        "student_id": "test-123",
        "messages": [{"role": "user", "content": "Fai vocab"}],
        "current_exercise": "vocabulary",
        "cefr_level": "B1",
        "vocabulary": [],
        "grammar_errors": [],
        "exercise_scores": {}
    }
    
    result = vocabulary_node(state)
    
    assert "messages" in result
    assert len(result["messages"]) > 0
    assert "flashcard" in result["messages"][-1]["content"].lower()

def test_vocabulary_node_respects_cefr_level(sample_student):
    """Test that vocabulary difficulty matches CEFR level."""
    state = {
        "student_id": "test-123",
        "messages": [{"role": "user", "content": "Fai vocab"}],
        "current_exercise": "vocabulary",
        "cefr_level": "A1",
        "vocabulary": [],
        "grammar_errors": [],
        "exercise_scores": {}
    }
    
    result = vocabulary_node(state)
    
    # A1 should have simpler vocabulary
    assert "ciao" in result["messages"][-1]["content"].lower() or \
           "simple" in result["messages"][-1]["content"].lower()
```

### Testing API Endpoints

```python
# tests/unit/test_api/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.italianollama.api.main import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

def test_health_endpoint(client):
    """Test health check returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_create_student(client, sample_student):
    """Test student creation."""
    response = client.post("/students", json=sample_student)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "student_id" in data

def test_get_student_not_found(client):
    """Test 404 for non-existent student."""
    response = client.get("/students/nonexistent-id")
    assert response.status_code == 404
```

### Testing Neo4j Client

```python
# tests/unit/test_memory/test_neo4j_client.py
import pytest
from unittest.mock import MagicMock, patch
from src.italianollama.memory.neo4j_client import Neo4jClient

@patch("src.italianollama.memory.neo4j_client.GraphDatabase")
def test_create_student(mock_graph_db):
    """Test student creation in Neo4j."""
    mock_driver = MagicMock()
    mock_graph_db.driver.return_value = mock_driver
    
    client = Neo4jClient("bolt://localhost", "neo4j", "password")
    
    with patch.object(client, "_run_query", return_value={"student_id": "123"}):
        result = client.create_student("Test User", "test@example.com")
        
    assert result["student_id"] == "123"
    mock_driver.close.assert_called()
```

## Integration Tests

### Testing the Full Flow

```python
# tests/integration/test_graph_flow.py
import pytest
from src.italianollama.graph.graph import create_graph

def test_full_conversation_flow(mock_neo4j):
    """Test complete conversation from greeting to exercise."""
    graph = create_graph()
    
    initial_state = {
        "student_id": "test-123",
        "messages": [{"role": "user", "content": "Ciao"}],
        "current_exercise": None,
        "cefr_level": "B1",
        "vocabulary": [],
        "grammar_errors": [],
        "exercise_scores": {}
    }
    
    result = graph.invoke(initial_state)
    
    assert len(result["messages"]) == 2
    assert result["messages"][-1]["role"] == "assistant"
```

### Testing API to Database Flow

```python
# tests/integration/test_api_flow.py
import pytest
from fastapi.testclient import TestClient

def test_chat_to_progress_flow(client, mock_neo4j):
    """Test that chat creates progress records."""
    # Create student
    response = client.post("/students", json={
        "name": "Test",
        "email": "test@example.com"
    })
    student_id = response.json()["student_id"]
    
    # Send chat message
    response = client.post(f"/chat", json={
        "student_id": student_id,
        "message": "Fai vocab"
    })
    
    assert response.status_code == 200
    
    # Verify progress was recorded
    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert "progress" in data
```

## Mocking

### Mocking LLM Responses

```python
from unittest.mock import patch

@pytest.fixture
def mock_llm_response():
    """Mock LLM completion response."""
    return {
        "choices": [
            {
                "delta": {
                    "content": "Ciao! Benvenuto al corso di italiano!"
                }
            }
        ]
    }

def test_chat_with_mocked_llm(client, mock_llm_response):
    """Test chat with mocked LLM."""
    with patch("litellm.completion", return_value=mock_llm_response):
        response = client.post("/chat", json={
            "student_id": "test-123",
            "message": "Ciao"
        })
        
    assert response.status_code == 200
    assert "Ciao" in response.json()["message"]
```

## Test Database

### Using Test Neo4j

```bash
# Start test database
docker run -d \
  --name neo4j-test \
  -p 7688:7687 \
  -p 7475:7474 \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_AUTH=neo4j/testpassword \
  neo4j
```

### Test Environment Variables

```bash
# .env.test
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=testpassword
NEO4J_DATABASE=neo4j
```

## Coverage Reports

### Generate HTML Report

```bash
pytest --cov=src --cov-report=html --cov-report=term
open htmlcov/index.html
```

### Minimum Coverage

| Module | Minimum |
|--------|---------|
| `graph/` | 80% |
| `api/` | 85% |
| `memory/` | 75% |
| `cli/` | 60% |

## CI/CD Testing

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-cov
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Related Documentation

- [Setup Guide](setup.md)
- [Coding Standards](coding-standards.md)
- [Debugging Guide](debugging.md)
