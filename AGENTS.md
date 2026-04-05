# AGENTS.md - ItalianOllama Development Guidelines

## Project Overview
ItalianOllama is an AI-powered Italian language learning platform using LangGraph, Neo4j, and LiteLLM. It features dual frontends (Chainlit for chat, Streamlit for analytics) with a shared FastAPI backend.

## Build & Test Commands

### Running Tests
```bash
# All tests
poetry run pytest

# Single test file
poetry run pytest tests/unit/api/test_api_config.py

# Single test function
poetry run pytest tests/unit/api/test_api_config.py::test_config_validation

# Unit tests only
poetry run pytest -m unit

# Integration tests only
poetry run pytest -m integration

# Skip slow tests
poetry run pytest -m "not slow"

# With coverage
poetry run pytest --cov=italianollama --cov-report=term-missing

# Benchmark tests
poetry run pytest src/italianollama/benchmarking/tests.py
```

### Linting & Formatting
```bash
# Run all linting (ruff, mypy, bandit)
poetry run pre-commit run --all-files

# Format code
poetry run ruff format src/
poetry run black src/

# Type checking
poetry run mypy src/

# Security scan
poetry run bandit -r src/

# Ruff linting only
poetry run ruff check src/
```

### Docker Commands
```bash
# Start services
python cli.py docker up

# Stop services
python cli.py docker down

# View logs
python cli.py docker logs api

# Run migration/health checks
python cli.py neo4j status
python cli.py llm test
```

### Local Development
```bash
# Backend API
poetry run uvicorn src.italianollama.api.main:app --port 8000 --reload

# Chainlit chat interface
poetry run chainlit run src/italianollama/frontend/chainlit_app.py --port 8501 --reload

# Streamlit dashboard
poetry run streamlit run src/italianollama/frontend/streamlit/app_enhanced.py --server.port 8502
```

## Code Style Guidelines

### Python Conventions
- **Python version**: >=3.10, <4.0
- **PEP 8** compliant with additional rules from ruff
- **Line length**: 99 characters (configured in pyproject.toml)
- **String quotes**: Double quotes (config: `inline-quotes = "double"`, `multiline-quotes = "double"`)
- **Docstrings**: Google Python Style Guide format for all public functions/classes

### Type Hints
- **Strict mode**: mypy runs with `strict = true`
- **All functions must have type hints** including return types
- Use `typing.Optional[T]` for nullable values
- Use `typing.Union[T1, T2]` for union types
- Use `asyncio` patterns for async functions
- Prefer `pydantic.BaseModel` for data models

### Import Order (isort configuration)
1. Standard library imports
2. Third-party imports
3. First-party imports (`italianollama.*`)
4. Relative imports

Example:
```python
import os
import json
from typing import Optional

import pydantic
import neo4j

from italianollama.memory.neo4j_client import Neo4jClient
from .utils import helper_function
```

### Naming Conventions
- **Classes**: PascalCase (`Neo4jClient`, `LLMClient`, `BenchmarkRunner`)
- **Functions/Variables**: snake_case (`get_student`, `vocabulary_list`, `max_retries`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Async functions**: prefix with `async_` or use descriptive names (`fetch_data`, `process_stream`)

### Error Handling
- Use custom exceptions from `italianollama.api.exceptions`
- Include context in exceptions (student_id, operation, etc.)
- Use try/except with specific exception types
- Log errors with context using the `logging` module
- Return structured error responses in API endpoints

### Async Patterns
- Use `async/await` for I/O operations (database, API calls)
- Use `asyncio.create_task()` for concurrent operations
- Prefer `httpx.AsyncClient` over synchronous HTTP clients
- Test async functions with `pytest-asyncio` and `@pytest.mark.asyncio`

### Testing Guidelines
- Unit tests in `tests/unit/`, integration tests in `tests/integration/`
- Test file naming: `test_<module>.py` or `test_<feature>.py`
- Use fixtures for common test setups
- Mock external dependencies (database, LLM API)
- Achieve >=50% code coverage (configured in pyproject.toml)

### File Organization
```
src/italianollama/
├── api/              # FastAPI endpoints and middleware
├── graph/            # LangGraph workflow nodes
├── memory/           # Neo4j integration and data models
├── frontend/         # Chainlit and Streamlit UI
├── benchmarking/     # Performance benchmarks
└── utils/            # Shared utilities (OpenRouter, etc.)
```

## Pre-commit Hooks
The repository uses pre-commit with the following hooks:
- `ruff`: Linting and auto-fix
- `ruff-format`: Code formatting
- `mypy`: Type checking (excludes tests/examples)
- `bandit`: Security scanning
- Standard hooks: end-of-file fixer, trailing whitespace, YAML/JSON validation

## CI/CD Pipeline
- GitHub Actions workflows in `.github/workflows/`
- `cdci.yml`: Continuous integration (lint, test, security)
- `release.yml`: Release automation with semantic release
- `benchmark.yml`: Performance benchmarking

## Special Notes
- **No comments**: Code should be self-documenting
- **Test paths**: `tests/` at project root (not in `src/`)
- **Examples excluded**: From linting/type checking (configured in pyproject.toml)
- **Authentication**: JWT tokens with 4h expiry, HS256 algorithm
- **Database**: Neo4j for persistent student data, vocabulary, grammar errors
