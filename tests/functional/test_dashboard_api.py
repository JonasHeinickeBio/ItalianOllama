import pytest
import requests
import os
import uuid

# Use the backend URL from environment or default to localhost
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

@pytest.fixture(scope="module")
def test_student_id():
    """Generate a unique student ID for this test session."""
    return f"test_user_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="module")
def auth_token(test_student_id):
    """Obtain a real JWT token for the test student."""
    response = requests.post(
        f"{BACKEND_URL}/auth/token",
        json={"student_id": test_student_id}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

class TestDashboardFunctional:
    """Functional tests for endpoints used by the Streamlit Dashboard."""

    def test_backend_health(self):
        """Verify backend is reachable and healthy."""
        response = requests.get(f"{BACKEND_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "degraded"]

    def test_student_lifecycle(self, test_student_id):
        """Test student creation and retrieval (Steps 1 & 2 of UX)."""
        # 1. Verify student doesn't exist yet
        resp = requests.get(f"{BACKEND_URL}/students/{test_student_id}")
        assert resp.status_code == 404

        # 2. Create student
        resp = requests.post(
            f"{BACKEND_URL}/students",
            json={"student_id": test_student_id, "name": "Functional Test Student"}
        )
        assert resp.status_code == 200
        assert resp.json()["student_id"] == test_student_id

        # 3. Retrieve student profile
        resp = requests.get(f"{BACKEND_URL}/students/{test_student_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_id"] == test_student_id
        assert data["name"] == "Functional Test Student"

    def test_onboarding_set_level(self, test_student_id):
        """Test level setting via chat endpoint (Step 3 & 4 of UX)."""
        # The /set_level command should be handled quickly. 
        # We set a low recursion limit to catch issues.
        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "student_id": test_student_id, 
                "message": "/set_level B2",
                "config": {"recursion_limit": 20}
            }
        )
        assert resp.status_code == 200
        # Check if level updated in profile
        resp = requests.get(f"{BACKEND_URL}/students/{test_student_id}")
        assert resp.json()["level"] == "B2"

    def test_dashboard_stats(self, test_student_id):
        """Test statistics endpoint (Progress Page)."""
        resp = requests.get(f"{BACKEND_URL}/api/student/{test_student_id}/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_exercises" in data
        assert "total_vocab" in data
        assert "avg_score" in data

    def test_dashboard_vocabulary(self, test_student_id):
        """Test vocabulary endpoint (Vocabulary Page)."""
        resp = requests.get(f"{BACKEND_URL}/api/student/{test_student_id}/vocabulary")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_dashboard_grammar_errors(self, test_student_id):
        """Test grammar errors endpoint (Grammar Page)."""
        resp = requests.get(f"{BACKEND_URL}/api/student/{test_student_id}/grammar-errors")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_dashboard_knowledge_graph(self, test_student_id):
        """Test graph endpoint (Knowledge Graph Page)."""
        resp = requests.get(f"{BACKEND_URL}/api/student/{test_student_id}/graph")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "links" in data

    def test_dashboard_test_readiness(self, test_student_id):
        """Test readiness endpoint (Test Readiness Page)."""
        resp = requests.get(f"{BACKEND_URL}/api/student/{test_student_id}/test-readiness")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_auth_verification(self, auth_token, test_student_id):
        """Test JWT verification endpoint."""
        resp = requests.post(
            f"{BACKEND_URL}/auth/verify",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["valid"] is True
        assert resp.json()["student_id"] == test_student_id
