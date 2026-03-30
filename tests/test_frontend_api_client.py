"""Unit tests for frontend API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


class TestAPIClient:
    """Tests for the API client."""

    def test_api_client_import(self):
        """Test APIClient can be imported."""
        from italianollama.frontend.api.client import APIClient
        assert APIClient is not None

    def test_api_client_init(self):
        """Test APIClient initialization."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30.0

    def test_api_client_init_with_defaults(self):
        """Test APIClient with default values."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        assert client.base_url == "http://localhost:8000"
        assert client.timeout > 0


class TestAPIClientChat:
    """Tests for chat functionality."""

    @pytest.mark.asyncio
    async def test_chat_requires_auth(self):
        """Test chat requires authentication."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        
        with pytest.raises(Exception):  # No auth token
            await client.chat(
                messages=[{"role": "user", "content": "Ciao"}],
                student_id="test"
            )

    @pytest.mark.asyncio
    async def test_chat_with_auth(self):
        """Test chat with authentication."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "choices": [{"message": {"content": "Ciao!"}}]
            }
            
            result = await client.chat(
                messages=[{"role": "user", "content": "Ciao"}],
                student_id="test"
            )
            
            assert result is not None

    @pytest.mark.asyncio
    async def test_stream_chat(self):
        """Test streaming chat."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        async def mock_stream():
            yield "Ciao"
            yield "!"
        
        with patch.object(client, "_stream_request") as mock_stream_req:
            mock_stream_req.return_value = mock_stream()
            
            result = []
            async for chunk in client.stream_chat(
                messages=[{"role": "user", "content": "Ciao"}],
                student_id="test"
            ):
                result.append(chunk)
            
            assert len(result) >= 0


class TestAPIClientStudents:
    """Tests for student API methods."""

    @pytest.mark.asyncio
    async def test_create_student(self):
        """Test creating a student."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "student_id": "test123",
                "name": "Mario"
            }
            
            result = await client.create_student(
                student_id="test123",
                name="Mario"
            )
            
            assert result["student_id"] == "test123"

    @pytest.mark.asyncio
    async def test_get_student(self):
        """Test getting a student."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "student_id": "test123",
                "name": "Mario",
                "level": "A2"
            }
            
            result = await client.get_student("test123")
            
            assert result["student_id"] == "test123"

    @pytest.mark.asyncio
    async def test_set_student_level(self):
        """Test setting student level."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": "ok"}
            
            result = await client.set_student_level(
                student_id="test123",
                level="B1",
                confidence=0.8
            )
            
            assert result is not None


class TestAPIClientVocabulary:
    """Tests for vocabulary API methods."""

    @pytest.mark.asyncio
    async def test_get_vocabulary(self):
        """Test getting vocabulary."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = [
                {"word": "ciao", "translation": "hello"},
                {"word": "grazie", "translation": "thank you"}
            ]
            
            result = await client.get_vocabulary("test123")
            
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_add_vocabulary(self):
        """Test adding vocabulary."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": "ok"}
            
            result = await client.add_vocabulary(
                student_id="test123",
                word="mare",
                translation="sea",
                topic="travel"
            )
            
            assert result is not None

    @pytest.mark.asyncio
    async def test_update_vocabulary_confidence(self):
        """Test updating vocabulary confidence."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": "ok"}
            
            result = await client.update_vocabulary_confidence(
                student_id="test123",
                word="ciao",
                confidence=0.9
            )
            
            assert result is not None


class TestAPIClientExercises:
    """Tests for exercise API methods."""

    @pytest.mark.asyncio
    async def test_record_exercise(self):
        """Test recording an exercise."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": "ok"}
            
            result = await client.record_exercise(
                student_id="test123",
                exercise_type="vocabulary",
                score=85,
                level="A2"
            )
            
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_exercise_history(self):
        """Test getting exercise history."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = [
                {"type": "vocabulary", "score": 85, "level": "A2"}
            ]
            
            result = await client.get_exercise_history("test123")
            
            assert len(result) == 1


class TestAPIErrorHandling:
    """Tests for API error handling."""

    @pytest.mark.asyncio
    async def test_handle_401_error(self):
        """Test handling 401 error."""
        from italianollama.frontend.api.client import APIClient
        from italianollama.frontend.api.errors import APIError
        
        client = APIClient()
        client.set_auth_token("invalid_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = Exception("401 Unauthorized")
            
            with pytest.raises(Exception):
                await client.get_student("test")

    @pytest.mark.asyncio
    async def test_handle_404_error(self):
        """Test handling 404 error."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = Exception("404 Not Found")
            
            with pytest.raises(Exception):
                await client.get_student("nonexistent")

    @pytest.mark.asyncio
    async def test_handle_timeout(self):
        """Test handling timeout."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        with patch.object(client, "_request") as mock_request:
            import asyncio
            mock_request.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(Exception):
                await client.get_student("test")


class TestAuthToken:
    """Tests for authentication token handling."""

    def test_set_auth_token(self):
        """Test setting auth token."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token_123")
        
        assert client.auth_token == "test_token_123"

    def test_clear_auth_token(self):
        """Test clearing auth token."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        client.clear_auth_token()
        
        assert client.auth_token is None

    def test_auth_header(self):
        """Test auth header is generated."""
        from italianollama.frontend.api.client import APIClient
        
        client = APIClient()
        client.set_auth_token("test_token")
        
        headers = client._get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token"
