"""Functional tests for API endpoints using in-process FastAPI app."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.functional


def test_root_endpoint_returns_api_info(api_client):
    response = api_client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Italian Tutor API"
    assert payload["docs"] == "/docs"
    assert "request_id" in payload


def test_health_endpoint_reports_connected_neo4j(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["neo4j"] == "connected"
    assert payload["status"] in {"ok", "degraded"}


def test_auth_token_and_verify_roundtrip(api_client):
    token_response = api_client.post("/auth/token", json={"student_id": "s-functional"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    verify_response = api_client.post(
        "/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert verify_payload["valid"] is True
    assert verify_payload["student_id"] == "s-functional"


def test_student_create_then_get(api_client):
    missing_response = api_client.get("/students/student-functional")
    assert missing_response.status_code == 404

    create_response = api_client.post(
        "/students",
        json={"student_id": "student-functional", "name": "Functional Student"},
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == "created"

    get_response = api_client.get("/students/student-functional")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["student_id"] == "student-functional"
    assert payload["name"] == "Functional Student"


def test_chat_endpoint_returns_response_and_level(api_client):
    response = api_client.post(
        "/chat",
        json={"message": "Ciao Sofia", "student_id": "student-functional"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["response"] == "Echo: Ciao Sofia"
    assert payload["student_level"] == "A2"


def test_chat_completions_endpoint_non_streaming(api_client):
    response = api_client.post(
        "/v1/chat/completions",
        json={
            "model": "tutor",
            "messages": [{"role": "user", "content": "Parliamo italiano"}],
            "stream": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "chat.completion"
    assert payload["choices"][0]["message"]["content"] == "Echo: Parliamo italiano"


def test_chat_completions_endpoint_streaming(api_client):
    with api_client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "tutor",
            "messages": [{"role": "user", "content": "Streaming test"}],
            "stream": True,
        },
    ) as response:
        body = "".join(chunk for chunk in response.iter_text())

    assert response.status_code == 200
    assert "data: [DONE]" in body


def test_dashboard_endpoints_return_expected_shapes(api_client):
    assert api_client.get("/api/student/student-functional/stats").json().keys() >= {
        "total_exercises",
        "total_vocab",
        "avg_score",
    }

    vocabulary_response = api_client.get("/api/student/student-functional/vocabulary")
    assert vocabulary_response.status_code == 200
    assert isinstance(vocabulary_response.json(), list)

    errors_response = api_client.get("/api/student/student-functional/grammar-errors")
    assert errors_response.status_code == 200
    assert isinstance(errors_response.json(), list)

    graph_response = api_client.get("/api/student/student-functional/graph")
    assert graph_response.status_code == 200
    graph_payload = graph_response.json()
    assert "nodes" in graph_payload
    assert "links" in graph_payload

    readiness_response = api_client.get("/api/student/student-functional/test-readiness")
    assert readiness_response.status_code == 200
    assert isinstance(readiness_response.json(), list)
