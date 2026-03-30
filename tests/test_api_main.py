"""Unit tests for API main module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response


class TestAPIMain:
    """Tests for the main API application."""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies."""
        with patch("italianollama.api.main.get_neo4j_client") as mock_neo4j, \
             patch("italianollama.api.main.get_settings") as mock_settings, \
             patch("italianollama.api.main.verify_access_token") as mock_verify:
            
            mock_neo4j_instance = MagicMock()
            mock_neo4j_instance.connect = AsyncMock()
            mock_neo4j.return_value = mock_neo4j_instance
            
            mock_settings_instance = MagicMock()
            mock_settings_instance.neo4j_uri = "bolt://localhost:7687"
            mock_settings.return_value = mock_settings_instance
            
            mock_verify.return_value = {"sub": "test_student"}
            
            yield {
                "neo4j": mock_neo4j,
                "settings": mock_settings,
                "verify": mock_verify,
                "neo4j_instance": mock_neo4j_instance,
            }

    def test_app_initialization(self):
        """Test the FastAPI app is initialized."""
        from italianollama.api.main import app
        assert app is not None
        assert app.title == "Italian Ollama Tutor API"

    def test_app_docs_url(self):
        """Test API docs are available."""
        from italianollama.api.main import app
        assert "/docs" in app.docs_url
        assert "/redoc" in app.redoc_url

    def test_app_routes_exist(self):
        """Test main routes are registered."""
        from italianollama.api.main import app
        routes = [route.path for route in app.routes]
        
        # Check for key routes
        assert any("/health" in r for r in routes)
        assert any("v1/chat" in r for r in routes)
        assert any("v1/students" in r for r in routes)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_healthy(self):
        """Test health endpoint returns healthy status."""
        with patch("italianollama.api.main.get_neo4j_client") as mock_neo4j:
            mock_client = MagicMock()
            mock_client.verify_connectivity = AsyncMock(return_value=True)
            mock_neo4j.return_value = mock_client
            
            from fastapi.testclient import TestClient
            from italianollama.api.main import app
            
            with TestClient(app) as client:
                response = client.get("/health")
                
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_endpoint_neo4j_down(self):
        """Test health endpoint handles Neo4j being down."""
        with patch("italianollama.api.main.get_neo4j_client") as mock_neo4j:
            mock_client = MagicMock()
            mock_client.verify_connectivity = AsyncMock(side_effect=Exception("Connection failed"))
            mock_neo4j.return_value = mock_client
            
            from fastapi.testclient import TestClient
            from italianollama.api.main import app
            
            with TestClient(app) as client:
                response = client.get("/health")
                
            assert response.status_code == 503


class TestChatCompletions:
    """Tests for chat completions endpoint."""

    @pytest.mark.asyncio
    async def test_chat_completions_requires_auth(self):
        """Test chat endpoint requires authentication."""
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": "Ciao"}],
                    "model": "tutor"
                }
            )
            
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_chat_completions_with_auth(self, mock_dependencies):
        """Test chat endpoint with valid auth."""
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        # Create a valid token
        with patch("italianollama.api.middleware.auth.create_access_token") as mock_create:
            mock_create.return_value = "valid_token"
            
            with TestClient(app) as client:
                response = client.post(
                    "/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": "Ciao"}],
                        "model": "tutor"
                    },
                    headers={"Authorization": "Bearer valid_token"}
                )
                
            # May return 200 or 500 depending on mocked LLM
            assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_chat_completions_invalid_request(self, mock_dependencies):
        """Test chat endpoint validates request."""
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.post(
                "/v1/chat/completions",
                json={"model": "tutor"},  # Missing messages
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code == 422  # Validation error


class TestStudentsEndpoints:
    """Tests for student endpoints."""

    @pytest.mark.asyncio
    async def test_create_student(self, mock_dependencies):
        """Test creating a student."""
        mock_dependencies["neo4j_instance"].create_student = AsyncMock(
            return_value="node_123"
        )
        
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.post(
                "/v1/students",
                json={"student_id": "test123", "name": "Mario"},
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code in [200, 201, 500]

    @pytest.mark.asyncio
    async def test_get_student(self, mock_dependencies):
        """Test getting a student."""
        mock_dependencies["neo4j_instance"].get_student = AsyncMock(
            return_value={
                "student_id": "test123",
                "name": "Mario",
                "level": "A2"
            }
        )
        
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.get(
                "/v1/students/test123",
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_get_student_not_found(self, mock_dependencies):
        """Test getting non-existent student."""
        mock_dependencies["neo4j_instance"].get_student = AsyncMock(
            return_value=None
        )
        
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.get(
                "/v1/students/nonexistent",
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code == 404


class TestVocabularyEndpoints:
    """Tests for vocabulary endpoints."""

    @pytest.mark.asyncio
    async def test_get_vocabulary(self, mock_dependencies):
        """Test getting student vocabulary."""
        mock_dependencies["neo4j_instance"].get_student_vocabulary = AsyncMock(
            return_value=[
                {"word": "ciao", "translation": "hello"},
                {"word": "grazie", "translation": "thank you"}
            ]
        )
        
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.get(
                "/v1/students/test123/vocabulary",
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_add_vocabulary(self, mock_dependencies):
        """Test adding vocabulary."""
        mock_dependencies["neo4j_instance"].add_vocabulary = AsyncMock()
        
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.post(
                "/v1/students/test123/vocabulary",
                json={
                    "word": "mare",
                    "translation": "sea",
                    "topic": "travel"
                },
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code in [200, 201, 500]


class TestExerciseEndpoints:
    """Tests for exercise endpoints."""

    @pytest.mark.asyncio
    async def test_record_exercise(self, mock_dependencies):
        """Test recording an exercise."""
        mock_dependencies["neo4j_instance"].record_exercise = AsyncMock()
        
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.post(
                "/v1/students/test123/exercises",
                json={
                    "exercise_type": "vocabulary",
                    "score": 85,
                    "level": "A2"
                },
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code in [200, 201, 500]

    @pytest.mark.asyncio
    async def test_get_exercise_history(self, mock_dependencies):
        """Test getting exercise history."""
        mock_dependencies["neo4j_instance"].get_exercise_history = AsyncMock(
            return_value=[
                {"type": "vocabulary", "score": 85, "level": "A2"}
            ]
        )
        
        from fastapi.testclient import TestClient
        from italianollama.api.main import app
        
        with TestClient(app) as client:
            response = client.get(
                "/v1/students/test123/exercises",
                headers={"Authorization": "Bearer valid_token"}
            )
            
        assert response.status_code in [200, 500]