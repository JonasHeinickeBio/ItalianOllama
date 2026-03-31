"""Unit tests for API main module with full mocking.

Tests all endpoints in main.py with mocked dependencies to avoid
requiring actual Neo4j or LiteLLM connections.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test root endpoint."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app for testing."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password",
                neo4j_database="neo4j",
                litellm_base_url="http://litellm:4000",
                jwt_expiration_hours=4,
            )
            
            from italianollama.api.main import app
            return app

    def test_root_endpoint(self, mock_app):
        """Test root endpoint returns API info."""
        with TestClient(mock_app) as client:
            response = client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Italian Tutor API"
            assert data["version"] == "0.2.0"
            assert "docs" in data


class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.fixture
    def mock_app_with_neo4j(self):
        """Create mock app with Neo4j mocked."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password",
                neo4j_database="neo4j",
                litellm_base_url="http://litellm:4000",
                jwt_expiration_hours=4,
            )
                
            with patch("italianollama.api.main.get_neo4j_client") as mock_neo4j:
                mock_client = MagicMock()
                mock_client.verify_connectivity = AsyncMock(return_value=True)
                mock_neo4j.return_value = mock_client
                
                from italianollama.api.main import app
                return app

    def test_health_endpoint_connected(self, mock_app_with_neo4j):
        """Test health endpoint when Neo4j is connected."""
        with patch("italianollama.api.main.settings") as mock_settings:
            mock_settings.litellm_base_url = "http://litellm:4000"
            
            with patch("httpx.AsyncClient") as mock_http:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_async_context = MagicMock()
                mock_async_context.__aenter__ = AsyncMock(return_value=mock_response)
                mock_async_context.__aexit__ = AsyncMock(return_value=None)
                mock_http.return_value = mock_async_context
                
                with TestClient(mock_app_with_neo4j) as client:
                    response = client.get("/health")
                    assert response.status_code == 200
                    data = response.json()
                    assert "status" in data
                    assert "neo4j" in data
                    assert "litellm" in data


class TestAuthTokenEndpoint:
    """Test authentication token endpoints."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password",
                neo4j_database="neo4j",
                litellm_base_url="http://litellm:4000",
                jwt_expiration_hours=4,
            )
            from italianollama.api.main import app
            return app

    def test_get_token_success(self, mock_app):
        """Test successful token generation."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/auth/token",
                json={"student_id": "test_student_123"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data

    def test_get_token_empty_student_id(self, mock_app):
        """Test token generation with empty student_id."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/auth/token",
                json={"student_id": ""}
            )
            assert response.status_code == 400

    def test_get_token_with_custom_expiry(self, mock_app):
        """Test token generation with custom expiration."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/auth/token",
                json={"student_id": "test_student", "expires_in_hours": 8}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data


class TestVerifyTokenEndpoint:
    """Test token verification endpoint."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
                jwt_expiration_hours=4,
            )
            from italianollama.api.main import app
            return app

    def test_verify_token_missing_header(self, mock_app):
        """Test verify with missing authorization header."""
        with TestClient(mock_app) as client:
            response = client.post("/auth/verify")
            assert response.status_code == 400

    def test_verify_token_invalid_format(self, mock_app):
        """Test verify with invalid header format."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/auth/verify",
                headers={"Authorization": "InvalidFormat"}
            )
            assert response.status_code == 400


class TestChatCompletionsEndpoint:
    """Test chat completions endpoint."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app with all dependencies mocked."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password",
                neo4j_database="neo4j",
                litellm_base_url="http://litellm:4000",
                jwt_expiration_hours=4,
            )
            
            from italianollama.api.main import app
            return app

    def test_chat_completions_no_messages(self, mock_app):
        """Test chat completions with no messages."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/v1/chat/completions",
                json={"messages": []}
            )
            assert response.status_code == 400

    def test_chat_completions_no_user_message(self, mock_app):
        """Test chat completions with no user message."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "You are a tutor"}
                    ]
                }
            )
            assert response.status_code == 400

    @patch("italianollama.api.main.get_tutor_graph")
    def test_chat_completions_non_streaming(self, mock_graph, mock_app):
        """Test non-streaming chat completions."""
        mock_graph_instance = MagicMock()
        mock_result = {
            "messages": [
                {"role": "assistant", "content": "Ciao! Come stai?"}
            ],
            "current_level": "A2"
        }
        mock_graph_instance.ainvoke = AsyncMock(return_value=mock_result)
        mock_graph.return_value = mock_graph_instance

        with TestClient(mock_app) as client:
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "tutor",
                    "messages": [
                        {"role": "user", "content": "Ciao"}
                    ],
                    "stream": False
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "choices" in data
            assert len(data["choices"]) > 0

    @patch("italianollama.api.main.get_tutor_graph")
    def test_chat_completions_with_system_prompt_student_id(self, mock_graph, mock_app):
        """Test extraction of student_id from system prompt."""
        mock_graph_instance = MagicMock()
        mock_result = {
            "messages": [
                {"role": "assistant", "content": "Ciao!"}
            ],
            "current_level": "A2"
        }
        mock_graph_instance.ainvoke = AsyncMock(return_value=mock_result)
        mock_graph.return_value = mock_graph_instance

        with TestClient(mock_app) as client:
            response = client.post(
                "/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "student_id: test_student_456"},
                        {"role": "user", "content": "Ciao"}
                    ]
                }
            )
            assert response.status_code == 200


class TestSimpleChatEndpoint:
    """Test simple chat endpoint."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
            )
            from italianollama.api.main import app
            return app

    @patch("italianollama.api.main.get_tutor_graph")
    def test_chat_endpoint_success(self, mock_graph, mock_app):
        """Test successful chat."""
        mock_graph_instance = MagicMock()
        mock_result = {
            "messages": [
                {"role": "assistant", "content": "Ciao! Sono il tuo tutore."}
            ],
            "current_level": "B1"
        }
        mock_graph_instance.ainvoke = AsyncMock(return_value=mock_result)
        mock_graph.return_value = mock_graph_instance

        with TestClient(mock_app) as client:
            response = client.post(
                "/chat",
                json={
                    "message": "Ciao",
                    "student_id": "test_student"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "session_id" in data

    def test_chat_endpoint_empty_message(self, mock_app):
        """Test chat with empty message."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/chat",
                json={
                    "message": "",
                    "student_id": "test_student"
                }
            )
            assert response.status_code == 400


class TestStudentManagementEndpoints:
    """Test student management endpoints."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
            )
            from italianollama.api.main import app
            return app

    @patch("italianollama.api.main.get_neo4j_client")
    def test_create_student_success(self, mock_neo4j, mock_app):
        """Test successful student creation."""
        mock_client = MagicMock()
        mock_client.create_student = AsyncMock()
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.post(
                "/students",
                json={
                    "student_id": "new_student",
                    "name": "Test Student"
                }
            )
            assert response.status_code == 200

    def test_create_student_empty_id(self, mock_app):
        """Test create student with empty ID."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/students",
                json={
                    "student_id": "",
                    "name": "Test Student"
                }
            )
            assert response.status_code == 400

    def test_create_student_empty_name(self, mock_app):
        """Test create student with empty name."""
        with TestClient(mock_app) as client:
            response = client.post(
                "/students",
                json={
                    "student_id": "student123",
                    "name": ""
                }
            )
            assert response.status_code == 400

    @patch("italianollama.api.main.get_neo4j_client")
    def test_get_student_success(self, mock_neo4j, mock_app):
        """Test successful student retrieval."""
        mock_client = MagicMock()
        mock_client.get_student = AsyncMock(return_value={
            "student_id": "test_student",
            "name": "Test",
            "level": "A2"
        })
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.get("/students/test_student")
            assert response.status_code == 200

    @patch("italianollama.api.main.get_neo4j_client")
    def test_get_student_not_found(self, mock_neo4j, mock_app):
        """Test student not found."""
        mock_client = MagicMock()
        mock_client.get_student = AsyncMock(return_value=None)
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.get("/students/nonexistent")
            assert response.status_code == 404


class TestStudentStatsEndpoints:
    """Test student stats API endpoints."""

    @pytest.fixture
    def mock_app(self):
        """Create mock app."""
        with patch("italianollama.api.main.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["http://localhost:3000"],
                cors_credentials=True,
            )
            from italianollama.api.main import app
            return app

    @patch("italianollama.api.main.get_neo4j_client")
    def test_get_student_stats(self, mock_neo4j, mock_app):
        """Test student stats endpoint."""
        mock_client = MagicMock()
        mock_client.get_student_stats = AsyncMock(return_value={
            "total_exercises": 10,
            "avg_score": 85.5,
            "total_vocab": 50
        })
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.get("/api/student/test_student/stats")
            assert response.status_code == 200

    @patch("italianollama.api.main.get_neo4j_client")
    def test_get_student_vocabulary(self, mock_neo4j, mock_app):
        """Test student vocabulary endpoint."""
        mock_client = MagicMock()
        mock_client.get_student_vocabulary = AsyncMock(return_value=[
            {"word": "ciao", "translation": "hello", "confidence": 0.8}
        ])
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.get("/api/student/test_student/vocabulary")
            assert response.status_code == 200

    @patch("italianollama.api.main.get_neo4j_client")
    def test_get_student_grammar_errors(self, mock_neo4j, mock_app):
        """Test student grammar errors endpoint."""
        mock_client = MagicMock()
        mock_client.get_common_errors = AsyncMock(return_value=[
            {"rule": "verb_conjugation", "seen_count": 5}
        ])
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.get("/api/student/test_student/grammar-errors")
            assert response.status_code == 200

    @patch("italianollama.api.main.get_neo4j_client")
    def test_get_student_graph(self, mock_neo4j, mock_app):
        """Test student knowledge graph endpoint."""
        mock_client = MagicMock()
        mock_client.get_full_knowledge_graph = AsyncMock(return_value={
            "nodes": [],
            "links": []
        })
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.get("/api/student/test_student/graph")
            assert response.status_code == 200

    @patch("italianollama.api.main.get_neo4j_client")
    def test_get_student_test_readiness(self, mock_neo4j, mock_app):
        """Test student test readiness endpoint."""
        mock_client = MagicMock()
        mock_client.get_test_readiness = AsyncMock(return_value=[
            {"type": "TELC", "readiness": 0.75}
        ])
        mock_neo4j.return_value = mock_client

        with TestClient(mock_app) as client:
            response = client.get("/api/student/test_student/test-readiness")
            assert response.status_code == 200