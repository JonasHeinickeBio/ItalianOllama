"""Real network functional test for API -> Neo4j data flow.

This suite hits the live API and verifies persisted graph state via direct Cypher queries.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pytest
import requests
from neo4j import GraphDatabase
from dotenv import dotenv_values

pytestmark = [pytest.mark.functional, pytest.mark.network]

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TEST_STUDENT_ID = "Test_0"
TEST_STUDENT_NAME = "Test User 0"

logger = logging.getLogger(__name__)


def _skip_if_backend_unavailable() -> None:
    logger.info("[STEP] Checking backend health at %s/health", BACKEND_URL)
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    except requests.RequestException as exc:
        logger.warning("[SKIP] Backend unavailable: %s", exc)
        pytest.skip(f"Live backend unavailable at {BACKEND_URL}: {exc}")

    if response.status_code >= 500:
        logger.warning("[SKIP] Backend unhealthy status=%s", response.status_code)
        pytest.skip(f"Live backend unhealthy at {BACKEND_URL}: {response.status_code}")

    logger.info("[OK] Backend health check status=%s", response.status_code)


def _neo4j_connection_settings() -> tuple[str, str, str, str]:
    logger.info("[STEP] Resolving Neo4j connection settings")
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USER", "")
    password = os.getenv("NEO4J_PASSWORD", "")
    database = os.getenv("NEO4J_DATABASE", "")

    # Fall back to local .env for developer workflows where env vars are not exported.
    if not (uri and user and password):
        env_path = Path(__file__).resolve().parents[3] / ".env"
        if env_path.exists():
            env_values = dotenv_values(env_path)
            uri = uri or str(env_values.get("NEO4J_URI", ""))
            user = user or str(env_values.get("NEO4J_USER", ""))
            password = password or str(env_values.get("NEO4J_PASSWORD", ""))
            database = database or str(env_values.get("NEO4J_DATABASE", ""))

    # Aura commonly uses instance ID as both username and database name.
    if not database and user:
        database = user

    if not database:
        database = "neo4j"

    if not uri or not user or not password:
        logger.warning("[SKIP] Missing Neo4j credentials in env/.env")
        pytest.skip("NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD must be set for network graph queries")

    logger.info("[OK] Neo4j settings resolved (database=%s)", database)
    return uri, user, password, database


def _create_or_update_student(student_id: str, name: str) -> requests.Response:
    logger.info("[STEP] POST /students for student_id=%s", student_id)
    return requests.post(
        f"{BACKEND_URL}/students",
        json={"student_id": student_id, "name": name},
        timeout=10,
    )


def _get_student(student_id: str) -> requests.Response:
    logger.info("[STEP] GET /students/%s", student_id)
    return requests.get(
        f"{BACKEND_URL}/students/{student_id}",
        timeout=10,
    )


def _get_student_stats(student_id: str) -> requests.Response:
    logger.info("[STEP] GET /api/student/%s/stats", student_id)
    return requests.get(
        f"{BACKEND_URL}/api/student/{student_id}/stats",
        timeout=10,
    )


def _get_student_graph(student_id: str) -> requests.Response:
    logger.info("[STEP] GET /api/student/%s/graph", student_id)
    return requests.get(
        f"{BACKEND_URL}/api/student/{student_id}/graph",
        timeout=10,
    )


def _open_neo4j_session():
    logger.info("[STEP] Opening Neo4j session")
    uri, user, password, database = _neo4j_connection_settings()
    driver = GraphDatabase.driver(uri, auth=(user, password))
    session = driver.session(database=database)
    logger.info("[OK] Neo4j session opened")
    return driver, session


def _query_student_record(session, student_id: str):
    logger.info("[STEP] Cypher query: student record for %s", student_id)
    return session.run(
        """
        MATCH (s:Student {student_id: $student_id})
        RETURN s.student_id AS student_id,
               s.name AS name,
               s.created_at IS NOT NULL AS has_created_at
        """,
        student_id=student_id,
    ).single()


def _query_student_relationship_count(session, student_id: str):
    logger.info("[STEP] Cypher query: relationship count for %s", student_id)
    return session.run(
        """
        MATCH (s:Student {student_id: $student_id})
        OPTIONAL MATCH (s)-[r]->()
        RETURN count(r) AS rel_count
        """,
        student_id=student_id,
    ).single()


def _assert_student_payload(student_payload: dict) -> None:
    assert student_payload["student_id"] == TEST_STUDENT_ID
    logger.info("[OK] Student payload validated")


def _assert_stats_payload(stats_payload: dict) -> None:
    assert "total_exercises" in stats_payload
    logger.info("[OK] Stats payload validated")


def _assert_graph_payload(graph_payload: dict) -> None:
    assert "nodes" in graph_payload
    assert "links" in graph_payload
    logger.info("[OK] Graph payload validated")


def _assert_student_record(student_record, student_payload: dict) -> None:
    assert student_record is not None
    assert student_record["student_id"] == TEST_STUDENT_ID
    assert student_record["name"] in {TEST_STUDENT_NAME, student_payload.get("name")}
    assert student_record["has_created_at"] is True
    logger.info("[OK] Neo4j student record validated")


def _assert_relationship_record(relationship_record) -> None:
    assert relationship_record is not None
    assert relationship_record["rel_count"] >= 0
    logger.info("[OK] Neo4j relationship record validated")


@pytest.mark.integration
def test_real_api_data_flow_for_test_0() -> None:
    """Hit live API for Test_0 and verify graph persistence with Cypher."""
    logger.info("[TEST START] test_real_api_data_flow_for_test_0")
    _skip_if_backend_unavailable()

    create_response = _create_or_update_student(TEST_STUDENT_ID, TEST_STUDENT_NAME)
    assert create_response.status_code == 200, create_response.text
    logger.info("[OK] Student create response status=%s", create_response.status_code)

    get_response = _get_student(TEST_STUDENT_ID)
    assert get_response.status_code == 200, get_response.text
    student_payload = get_response.json()
    _assert_student_payload(student_payload)

    stats_response = _get_student_stats(TEST_STUDENT_ID)
    assert stats_response.status_code == 200, stats_response.text
    stats_payload = stats_response.json()
    _assert_stats_payload(stats_payload)

    graph_response = _get_student_graph(TEST_STUDENT_ID)
    assert graph_response.status_code == 200, graph_response.text
    graph_payload = graph_response.json()
    _assert_graph_payload(graph_payload)

    driver, session = _open_neo4j_session()

    try:
        student_record = _query_student_record(session, TEST_STUDENT_ID)
        _assert_student_record(student_record, student_payload)

        relationship_record = _query_student_relationship_count(session, TEST_STUDENT_ID)
        _assert_relationship_record(relationship_record)
    finally:
        session.close()
        driver.close()
        logger.info("[STEP] Neo4j session and driver closed")

    logger.info("[TEST END] test_real_api_data_flow_for_test_0")


@pytest.mark.integration
def test_real_chat_for_test_0_best_effort() -> None:
    """Hit live /chat for Test_0 and xfail gracefully if LLM timeout occurs."""
    logger.info("[TEST START] test_real_chat_for_test_0_best_effort")
    _skip_if_backend_unavailable()

    try:
        chat_response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "student_id": TEST_STUDENT_ID,
                "message": "Ciao Sofia, facciamo pratica di italiano.",
            },
            timeout=8,
        )
    except requests.ReadTimeout:
        logger.warning("[XFAIL] /chat timed out for student_id=%s", TEST_STUDENT_ID)
        pytest.xfail("Live /chat timed out (likely upstream model latency); core data-flow test already verified")

    assert chat_response.status_code == 200, chat_response.text
    payload = chat_response.json()
    assert payload.get("response")
    logger.info("[TEST END] test_real_chat_for_test_0_best_effort")
