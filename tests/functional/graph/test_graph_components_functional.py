"""Functional tests for graph components and node behavior."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from italianollama.graph.graph import chat_node, router_node
from italianollama.graph.nodes import placement_node, vocabulary_node

pytestmark = pytest.mark.functional


@dataclass
class GraphFakeNeo4j:
    level_updates: list[tuple[str, str, float]]
    added_words: list[tuple[str, str, str, str, str]]

    async def set_student_level(self, student_id: str, level: str, confidence: float):
        self.level_updates.append((student_id, level, confidence))

    async def get_student_vocabulary(self, student_id: str, limit: int = 10):
        return [{"word": "ciao", "translation": "hello"}]

    async def add_vocabulary(
        self,
        student_id: str,
        word: str,
        translation: str,
        topic: str,
        level: str,
    ):
        self.added_words.append((student_id, word, translation, topic, level))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("state", "expected_route"),
    [
        ({"messages": [{"role": "user", "content": "ciao"}], "current_level": None}, "placement"),
        (
            {
                "messages": [{"role": "user", "content": "facciamo flashcard"}],
                "current_level": "A2",
                "exercise_type": None,
            },
            "vocabulary",
        ),
        (
            {
                "messages": [{"role": "user", "content": "voglio una traduzione"}],
                "current_level": "B1",
                "exercise_type": None,
            },
            "translation",
        ),
    ],
)
async def test_router_node_selects_expected_route(state, expected_route):
    updated = await router_node(state)
    assert updated["router_decision"] == expected_route


@pytest.mark.asyncio
async def test_chat_node_appends_assistant_response(monkeypatch: pytest.MonkeyPatch):
    async def fake_chat(self, messages, system_prompt=None):
        return "Risposta Sofia"

    monkeypatch.setattr("italianollama.graph.nodes.base.LLMClient.chat", fake_chat)

    state = {
        "student_id": "s1",
        "messages": [{"role": "user", "content": "Ciao"}],
    }

    fake_db = GraphFakeNeo4j(level_updates=[], added_words=[])
    updated = await chat_node(state, fake_db)

    assert updated["response"] == "Risposta Sofia"
    assert updated["messages"][-1]["role"] == "assistant"
    assert updated["should_continue"] is True


@pytest.mark.asyncio
async def test_placement_node_sets_level_and_persists(monkeypatch: pytest.MonkeyPatch):
    async def fake_chat_with_json(self, messages, response_schema, system_prompt=None):
        return {"level": "B1", "confidence": 0.87, "reasoning": "Strong comprehension"}

    monkeypatch.setattr("italianollama.graph.nodes.base.LLMClient.chat_with_json", fake_chat_with_json)

    state = {
        "student_id": "s2",
        "messages": [
            {"role": "assistant", "content": "Domanda di placement"},
            {"role": "user", "content": "Risposta studente"},
        ],
        "current_level": None,
    }

    fake_db = GraphFakeNeo4j(level_updates=[], added_words=[])
    updated = await placement_node(state, fake_db)

    assert updated["current_level"] == "B1"
    assert updated["level_confidence"] == 0.87
    assert fake_db.level_updates == [("s2", "B1", 0.87)]
    assert updated["should_continue"] is True


@pytest.mark.asyncio
async def test_vocabulary_node_updates_exercise_state(monkeypatch: pytest.MonkeyPatch):
    async def fake_chat(self, messages, system_prompt=None):
        return "Nuova flashcard: ciao = hello"

    async def fake_chat_with_json(self, messages, response_schema, system_prompt=None):
        return {
            "words": [
                {
                    "italian": "biblioteca",
                    "english": "library",
                    "topic": "daily_conversation",
                }
            ]
        }

    monkeypatch.setattr("italianollama.graph.nodes.base.LLMClient.chat", fake_chat)
    monkeypatch.setattr(
        "italianollama.graph.nodes.base.LLMClient.chat_with_json",
        fake_chat_with_json,
    )

    state = {
        "student_id": "s3",
        "messages": [{"role": "user", "content": "Vorrei parlare della biblioteca in citta"}],
        "current_level": "A2",
        "exercise_state": {},
    }

    fake_db = GraphFakeNeo4j(level_updates=[], added_words=[])
    updated = await vocabulary_node(state, fake_db)

    assert updated["exercise_state"]["exercise"] == "vocabulary"
    assert updated["response"] == "Nuova flashcard: ciao = hello"
    assert fake_db.added_words[0][1] == "biblioteca"
    assert updated["should_continue"] is True
