"""Shared fixtures for functional tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from fastapi.testclient import TestClient

from italianollama.api import main as api_main


@dataclass
class FakeNeo4jClient:
    """In-memory fake Neo4j client for functional endpoint tests."""

    students: dict[str, dict[str, Any]] = field(default_factory=dict)

    async def verify_connectivity(self) -> bool:
        return True

    async def setup_schema(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def create_student(self, student_id: str, name: str) -> str:
        self.students[student_id] = {
            "student_id": student_id,
            "name": name,
            "level": "A2",
            "level_confidence": 0.7,
            "vocab_count": 0,
            "exercise_count": 0,
        }
        return student_id

    async def get_student(self, student_id: str) -> dict[str, Any] | None:
        return self.students.get(student_id)

    async def get_student_stats(self, student_id: str) -> dict[str, Any]:
        return {"total_exercises": 4, "total_vocab": 12, "avg_score": 0.82}

    async def get_student_vocabulary(self, student_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return [{"word": "ciao", "translation": "hello", "confidence": 0.6}][:limit]

    async def get_common_errors(self, student_id: str, limit: int = 10) -> list[dict[str, Any]]:
        return [{"rule": "articles", "count": 2}][:limit]

    async def get_full_knowledge_graph(self, student_id: str) -> dict[str, list[dict[str, Any]]]:
        return {
            "nodes": [{"id": "student", "label": "Student"}],
            "links": [{"source": "student", "target": "A2", "label": "HAS_LEVEL"}],
        }

    async def get_test_readiness(self, student_id: str) -> list[dict[str, Any]]:
        return [{"exam": "CILS B1", "readiness": 0.7}]


class FakeGraph:
    """Simple fake tutor graph for API functional tests."""

    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
        user_text = state.get("messages", [{"content": ""}])[-1].get("content", "")
        return {
            "messages": state.get("messages", [])
            + [{"role": "assistant", "content": f"Echo: {user_text}"}],
            "current_level": "A2",
        }


@pytest.fixture
def fake_neo4j_client() -> FakeNeo4jClient:
    return FakeNeo4jClient()


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch, fake_neo4j_client: FakeNeo4jClient):
    """FastAPI TestClient with real routes and fake dependencies."""

    monkeypatch.setattr(api_main, "get_neo4j_client", lambda: fake_neo4j_client)
    monkeypatch.setattr(api_main, "get_tutor_graph", lambda: FakeGraph())

    with TestClient(api_main.app) as client:
        yield client
