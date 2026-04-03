"""Functional test: Complete API cycle testing all endpoints."""

import pytest

pytestmark = pytest.mark.functional


def test_complete_api_cycle(api_client):
    """Test complete API cycle: create student, interact, retrieve data, verify analytics."""

    student_id = "cycle-test-student"
    student_name = "Cycle Test Student"

    # 1. Test root endpoint
    root_response = api_client.get("/")
    assert root_response.status_code == 200
    root_data = root_response.json()
    assert root_data["name"] == "Italian Tutor API"
    assert "docs" in root_data

    # 2. Test health endpoint
    health_response = api_client.get("/health")
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert "status" in health_data
    assert health_data["status"] in {"ok", "degraded"}

    # 3. Create student
    create_response = api_client.post(
        "/students",
        json={"student_id": student_id, "name": student_name},
    )
    assert create_response.status_code == 200
    create_data = create_response.json()
    assert create_data["status"] == "created"
    assert create_data["student_id"] == student_id
    assert create_data["name"] == student_name

    # 4. Get student (verify creation)
    get_response = api_client.get(f"/students/{student_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["student_id"] == student_id
    assert get_data["name"] == student_name

    # 5. Test chat endpoint (free conversation)
    chat_response = api_client.post(
        "/chat",
        json={
            "message": "Ciao, come stai?",
            "student_id": student_id,
            "session_id": "session-1",
        },
    )
    assert chat_response.status_code == 200
    chat_data = chat_response.json()
    assert "response" in chat_data
    assert chat_data["session_id"] == "session-1"
    assert "student_level" in chat_data

    # 6. Test OpenAI-compatible chat endpoint (non-streaming)
    chat_completions_response = api_client.post(
        "/v1/chat/completions",
        json={
            "model": "tutor",
            "messages": [
                {"role": "system", "content": f"student_id: {student_id}"},
                {"role": "user", "content": "Parli italiano?"},
            ],
            "stream": False,
        },
    )
    assert chat_completions_response.status_code == 200
    chat_completions_data = chat_completions_response.json()
    assert chat_completions_data["object"] == "chat.completion"
    assert "choices" in chat_completions_data
    assert "message" in chat_completions_data["choices"][0]

    # 7. Generate auth token
    token_response = api_client.post(
        "/auth/token",
        json={"student_id": student_id, "expires_in_hours": 4},
    )
    assert token_response.status_code == 200
    token_data = token_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "expires_in" in token_data

    token = token_data["access_token"]

    # 8. Verify token
    verify_response = api_client.post(
        "/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["valid"] is True
    assert verify_data["student_id"] == student_id

    # 9. Get student stats
    stats_response = api_client.get(
        f"/api/student/{student_id}/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert "total_exercises" in stats_data
    assert "total_vocab" in stats_data
    assert "avg_score" in stats_data

    # 10. Get student vocabulary
    vocab_response = api_client.get(
        f"/api/student/{student_id}/vocabulary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert vocab_response.status_code == 200
    vocab_data = vocab_response.json()
    assert isinstance(vocab_data, list)

    # 11. Get student grammar errors
    errors_response = api_client.get(
        f"/api/student/{student_id}/grammar-errors",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert errors_response.status_code == 200
    errors_data = errors_response.json()
    assert isinstance(errors_data, list)

    # 12. Get student knowledge graph
    graph_response = api_client.get(
        f"/api/student/{student_id}/graph",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert graph_response.status_code == 200
    graph_data = graph_response.json()
    assert "nodes" in graph_data
    assert "links" in graph_data

    # 13. Get student test readiness
    readiness_response = api_client.get(
        f"/api/student/{student_id}/test-readiness",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert readiness_response.status_code == 200
    readiness_data = readiness_response.json()
    assert isinstance(readiness_data, list)

    # 14. Get learning velocity
    velocity_response = api_client.get(
        f"/analytics/velocity/{student_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert velocity_response.status_code == 200
    velocity_data = velocity_response.json()
    assert "student_id" in velocity_data
    assert "velocity" in velocity_data

    # 15. Get student skills
    skills_response = api_client.get(
        f"/analytics/skills/{student_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert skills_response.status_code == 200
    skills_data = skills_response.json()
    assert "student_id" in skills_data
    assert "grammar" in skills_data
    assert "vocabulary" in skills_data

    # 16. Get common errors
    common_errors_response = api_client.get(
        f"/analytics/errors/{student_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert common_errors_response.status_code == 200
    common_errors_data = common_errors_response.json()
    assert isinstance(common_errors_data, list)

    # 17. Get next module recommendation
    recommendations_response = api_client.get(
        f"/recommendations/next-module/{student_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert recommendations_response.status_code == 200
    recommendations_data = recommendations_response.json()
    assert "student_id" in recommendations_data
    assert "recommended_module" in recommendations_data

    # 18. Test streaming chat endpoint
    with api_client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "tutor",
            "messages": [
                {"role": "system", "content": f"student_id: {student_id}"},
                {"role": "user", "content": "Test streaming"},
            ],
            "stream": True,
        },
    ) as response:
        assert response.status_code == 200
        stream_content = "".join(response.iter_text())
        assert "data: [DONE]" in stream_content

    # 19. Test refresh token
    refresh_response = api_client.post(
        "/auth/refresh",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Student-ID": student_id,
        },
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data

    # 20. Verify student can only access their own data (negative test)
    other_student_response = api_client.get(
        "/api/student/other-student/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    # Should fail because student can't access other student's data
    assert other_student_response.status_code in {401, 403}

    # 21. Test invalid token verification
    invalid_verify_response = api_client.post(
        "/auth/verify",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert invalid_verify_response.status_code in {401, 422}

    # 22. Test missing student
    missing_student_response = api_client.get("/students/nonexistent-student")
    assert missing_student_response.status_code == 404

    # 23. Test chat with empty message
    empty_chat_response = api_client.post(
        "/chat",
        json={
            "message": "",
            "student_id": student_id,
        },
    )
    assert empty_chat_response.status_code in {400, 422}

    # 24. Test placement test (no level yet)
    placement_response = api_client.post(
        "/chat",
        json={
            "message": "Fai il placement test",
            "student_id": student_id,
            "session_id": "session-placement",
        },
    )
    assert placement_response.status_code == 200

    print("\n✓ All API endpoints tested successfully in complete cycle")
