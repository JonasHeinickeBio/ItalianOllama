# Coding Standards

This document outlines the coding standards and best practices for ItalianOllama development.

## Python Standards

### Style Guide

We follow **PEP 8** with some modifications:

- Line length: 100 characters (Black default)
- Use Black for formatting
- Use isort for import sorting
- Use type hints everywhere possible

### Code Formatting

```bash
# Format code
ruff check src/ tests/

# Sort imports
isort src/ tests/

# Combined (pre-commit does this)
pre-commit run --all-files
```

### Type Hints

**Always use type hints:**

```python
# Good
def get_student(student_id: str) -> Student | None:
    pass

def process_items(items: list[dict[str, Any]]) -> dict[str, int]:
    pass

# Avoid
def get_student(student_id):
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_confidence(
    correct: int,
    total: int,
    decay_factor: float = 0.9
) -> float:
    """Calculate vocabulary confidence based on practice results.

    Args:
        correct: Number of correct answers.
        total: Total number of attempts.
        decay_factor: Factor to reduce confidence on wrong answers.

    Returns:
        Confidence score between 0 and 1.

    Raises:
        ValueError: If total is zero or negative.
    """
    if total <= 0:
        raise ValueError("Total must be positive")

    accuracy = correct / total
    return min(1.0, accuracy * decay_factor)
```

## Project Structure

### Module Organization

```
src/italianollama/
├── api/              # FastAPI endpoints
│   ├── main.py       # API entry point
│   └── __init__.py
├── graph/            # LangGraph workflow
│   ├── state.py      # State definitions
│   ├── graph.py      # Graph builder
│   └── nodes/        # Graph nodes
│       ├── base.py
│       ├── vocabulary.py
│       └── ...
├── memory/           # Neo4j client
│   └── neo4j_client.py
└── cli/              # CLI commands
    └── main.py
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `neo4j_client.py` |
| Classes | PascalCase | `LLMClient` |
| Functions | snake_case | `get_student()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Variables | snake_case | `student_id` |

### File Organization

Each Python file should have:
1. Module docstring
2. Imports (stdlib, third-party, local)
3. Type aliases (if needed)
4. Functions/Classes
5. Main execution (if script)

```python
"""Short module description.

Longer description if needed.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from fastapi import FastAPI

from . import graph, memory

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI()
    # ...
    return app
```

## Git Conventions

### Commit Messages

Follow Conventional Commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(graph): add vocabulary flashcard node
fix(api): resolve student profile not loading
docs: update API endpoint documentation
refactor(neo4j): simplify query building
```

### Branch Naming

```
feature/description
bugfix/description
hotfix/urgent-fix
docs/new-section
```

### Pull Requests

- Keep PRs small and focused
- Include description of changes
- Link related issues
- Request review from maintainers

## Testing Standards

### Test Organization

```
tests/
├── unit/
│   ├── test_graph/
│   │   ├── test_nodes/
│   │   │   └── test_vocabulary.py
│   │   └── test_state.py
│   └── test_api/
├── integration/
│   └── test_api_integration.py
└── fixtures/
    └── sample_data.py
```

### Test Naming

```python
class TestLLMClient:
    def test_chat_returns_response(self):
        """Test that chat returns a valid response."""
        ...

    def test_chat_handles_stream(self):
        """Test streaming response handling."""
        ...

    def test_chat_raises_on_error(self):
        """Test error handling on API failure."""
        ...
```

### Test Coverage

- Aim for 80%+ coverage on core modules
- Test edge cases and error conditions
- Mock external dependencies

## Docker Standards

### Dockerfile Best Practices

```dockerfile
# Use specific versions
FROM python:3.11-slim

# Non-root user
RUN useradd --create-home appuser
USER appuser

# Copy only necessary files
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser src/ ./src/

# Use healthchecks
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost/health || exit 1
```

### Docker Compose

```yaml
services:
  api:
    build: ./backend
    restart: unless-stopped
    environment:
      - NEO4J_URI=${NEO4J_URI}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Security Standards

### Secrets Management

- Never commit secrets to git
- Use environment variables
- Use Docker secrets in production
- Rotate API keys regularly

### Input Validation

```python
from pydantic import BaseModel, Field

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[\w.-]+@[\w.-]+\.\w+$")
```

## Code Review Checklist

- [ ] Code follows style guide
- [ ] Type hints are present
- [ ] Docstrings explain "why", not "what"
- [ ] Tests are included
- [ ] No secrets in code
- [ ] Error handling is appropriate
- [ ] Performance considerations addressed

## Related Documentation

- [Setup Guide](setup.md)
- [Testing Guide](testing.md)
- [Debugging Guide](debugging.md)
