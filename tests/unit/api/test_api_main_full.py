"""Unit tests for API main module with mocking."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient


class TestAPIMain:
    """Tests for main API endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Import the app
        with patch('italianollama.api.main.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["*"],
                cors_credentials=True,
                jwt_expiration_hours=4,
                log_level="INFO",
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password",
                neo4j_database="neo4j",
            )
            with patch('italianollama.api.main.get_neo4j_client') as mock_neo4j:
                with patch('italianollama.api.main.get_tutor_graph'):
                    # Import after patching
                    from italianollama.api.main import app
                    
                    client = TestClient(app)
                    response = client.get("/")
                    
                    assert response.status_code == 200
                    assert "Italian Tutor API" in response.json()["name"]

    @pytest.mark.asyncio
    async def test_health_endpoint_connected(self):
        """Test health endpoint when services are connected."""
        with patch('italianollama.api.main.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                cors_origins=["*"],
                cors_credentials=True,
                jwt_expiration_hours=4,
                log_level="INFO",
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password",
                neo4j_database="neo4j",
                litellm_base_url="http://litellm:4000",
            )
            with patch('italianollama.api.main.get_neo4j_client') as mock_neo4j:
                mock_client = AsyncMock()
                mock_client.verify_connectivity = AsyncMock(return_value=True)
                mock_neo4j.return_value = mock_client
                
                with patch('italianollama.api.main.get_tutor_graph'):
                    from italianollama.api.main import app
                    
                    client = TestClient(app)
                    with patch('httpx.AsyncClient') as mock_http:
                        mock_response = MagicMock()
                        mock_response.status_code = 200
                        mock_http.return_value.__aenter__.return_value.get = AsyncMock(
                            return_value=mock_response
                        )
                        
                        response = client.get("/health")
                        assert response.status_code == 200

    def test_chat_message_model(self):
        """Test ChatMessage pydantic model."""
        from italianollama.api.main import ChatMessage
        
        msg = ChatMessage(message="Ciao", student_id="student1")
        assert msg.message == "Ciao"
        assert msg.student_id == "student1"
        assert msg.session_id is None

    def test_chat_message_with_session(self):
        """Test ChatMessage with session."""
        from italianollama.api.main import ChatMessage
        
        msg = ChatMessage(message="Ciao", student_id="student1", session_id="session1")
        assert msg.session_id == "session1"

    def test_chat_response_model(self):
        """Test ChatResponse pydantic model."""
        from italianollama.api.main import ChatResponse
        
        resp = ChatResponse(response="Ciao!", session_id="session1")
        assert resp.response == "Ciao!"
        assert resp.session_id == "session1"
        assert resp.student_level is None

    def test_student_create_model(self):
        """Test StudentCreate pydantic model."""
        from italianollama.api.main import StudentCreate
        
        student = StudentCreate(student_id="student1", name="John")
        assert student.student_id == "student1"
        assert student.name == "John"

    def test_token_request_model(self):
        """Test TokenRequest pydantic model."""
        from italianollama.api.main import TokenRequest
        
        req = TokenRequest(student_id="student1")
        assert req.student_id == "student1"
        assert req.expires_in_hours is None

    def test_token_response_model(self):
        """Test TokenResponse pydantic model."""
        from italianollama.api.main import TokenResponse
        
        resp = TokenResponse(access_token="token123", expires_in=3600)
        assert resp.access_token == "token123"
        assert resp.token_type == "bearer"
        assert resp.expires_in == 3600

    def test_health_response_model(self):
        """Test HealthResponse pydantic model."""
        from italianollama.api.main import HealthResponse
        
        resp = HealthResponse(status="ok", neo4j="connected", litellm="connected")
        assert resp.status == "ok"
        assert resp.neo4j == "connected"
        assert resp.litellm == "connected"


class TestAuthMiddleware:
    """Tests for auth middleware."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        from datetime import timedelta
        from unittest.mock import patch, MagicMock
        
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            from italianollama.api.middleware.auth import create_access_token
            
            token = create_access_token("student1")
            assert token is not None
            assert isinstance(token, str)

    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry."""
        from datetime import timedelta
        from unittest.mock import patch, MagicMock
        
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            from italianollama.api.middleware.auth import create_access_token
            
            token = create_access_token("student1", timedelta(hours=2))
            assert token is not None

    def test_verify_access_token_valid(self):
        """Test JWT token verification with valid token."""
        from datetime import timedelta
        from unittest.mock import patch, MagicMock
        import jwt
        
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            from italianollama.api.middleware.auth import create_access_token, verify_access_token
            
            token = create_access_token("student1")
            payload = verify_access_token(token)
            
            assert payload["sub"] == "student1"

    def test_verify_access_token_expired(self):
        """Test JWT token verification with expired token."""
        from datetime import datetime, timedelta, timezone
        from unittest.mock import patch, MagicMock
        import jwt
        
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            from italianollama.api.middleware.auth import verify_access_token
            from italianollama.api.exceptions import AuthenticationError
            
            # Create expired token
            expired_payload = {
                "sub": "student1",
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),
                "iat": datetime.now(timezone.utc) - timedelta(hours=5),
            }
            expired_token = jwt.encode(expired_payload, "test-secret", algorithm="HS256")
            
            with pytest.raises(AuthenticationError) as exc_info:
                verify_access_token(expired_token)
            assert "expired" in str(exc_info.value.detail).lower()

    def test_verify_access_token_invalid(self):
        """Test JWT token verification with invalid token."""
        from unittest.mock import patch, MagicMock
        
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4,
            )
            from italianollama.api.middleware.auth import verify_access_token
            from italianollama.api.exceptions import AuthenticationError
            
            with pytest.raises(AuthenticationError):
                verify_access_token("invalid-token")
