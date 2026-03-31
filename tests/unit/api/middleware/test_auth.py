"""Unit tests for API middleware auth module using pytest mock and magic mock."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, AsyncMock
import jwt


class TestCreateAccessToken:
    """Unit tests for create_access_token function."""

    @patch('italianollama.api.middleware.auth.get_settings')
    def test_create_access_token_default_expiry(self, mock_settings):
        """Test creating token with default expiry."""
        from italianollama.api.middleware.auth import create_access_token
        
        mock_settings.return_value.jwt_expiration_hours = 4
        mock_settings.return_value.auth_secret = "test-secret-key-that-is-long-enough-32chars"
        mock_settings.return_value.jwt_algorithm = "HS256"
        
        token = create_access_token("student123")
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        decoded = jwt.decode(token, "test-secret-key-that-is-long-enough-32chars", algorithms=["HS256"])
        assert decoded["sub"] == "student123"
        assert "exp" in decoded

    @patch('italianollama.api.middleware.auth.get_settings')
    def test_create_access_token_custom_expiry(self, mock_settings):
        """Test creating token with custom expiry."""
        from italianollama.api.middleware.auth import create_access_token
        
        mock_settings.return_value.jwt_expiration_hours = 4
        mock_settings.return_value.auth_secret = "test-secret-key-that-is-long-enough-32chars"
        mock_settings.return_value.jwt_algorithm = "HS256"
        
        custom_delta = timedelta(hours=2)
        token = create_access_token("student123", custom_delta)
        
        assert token is not None
        
        # Decode and verify expiry
        decoded = jwt.decode(token, "test-secret-key-that-is-long-enough-32chars", algorithms=["HS256"])
        expected_exp = datetime.now(timezone.utc) + custom_delta
        # Allow 5 second tolerance
        assert abs(decoded["exp"] - expected_exp.timestamp()) < 5


class TestVerifyAccessToken:
    """Unit tests for verify_access_token function."""

    @patch('italianollama.api.middleware.auth.get_settings')
    def test_verify_valid_token(self, mock_settings):
        """Test verifying a valid token."""
        from italianollama.api.middleware.auth import create_access_token, verify_access_token
        
        mock_settings.return_value.auth_secret = "test-secret-key-that-is-long-enough-32chars"
        mock_settings.return_value.jwt_algorithm = "HS256"
        mock_settings.return_value.jwt_expiration_hours = 4
        
        token = create_access_token("student123")
        payload = verify_access_token(token)
        
        assert payload["sub"] == "student123"

    @patch('italianollama.api.middleware.auth.get_settings')
    def test_verify_expired_token(self, mock_settings):
        """Test verifying an expired token."""
        from italianollama.api.middleware.auth import verify_access_token
        from italianollama.api.exceptions import AuthenticationError
        
        mock_settings.return_value.auth_secret = "test-secret-key-that-is-long-enough-32chars"
        mock_settings.return_value.jwt_algorithm = "HS256"
        
        # Create expired token
        expired_payload = {
            "sub": "student123",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        expired_token = jwt.encode(expired_payload, "test-secret-key-that-is-long-enough-32chars", algorithm="HS256")
        
        with pytest.raises(AuthenticationError) as exc_info:
            verify_access_token(expired_token)
        
        assert "expired" in str(exc_info.value.detail).lower()

    @patch('italianollama.api.middleware.auth.get_settings')
    def test_verify_invalid_token(self, mock_settings):
        """Test verifying an invalid token."""
        from italianollama.api.middleware.auth import verify_access_token
        from italianollama.api.exceptions import AuthenticationError
        
        mock_settings.return_value.auth_secret = "test-secret-key-that-is-long-enough-32chars"
        mock_settings.return_value.jwt_algorithm = "HS256"
        
        with pytest.raises(AuthenticationError):
            verify_access_token("invalid.token.here")


class TestGetCurrentStudent:
    """Unit tests for get_current_student dependency."""

    @pytest.mark.asyncio
    @patch('italianollama.api.middleware.auth.verify_access_token')
    async def test_get_current_student_from_bearer(self, mock_verify):
        """Test extracting student from Bearer token."""
        from italianollama.api.middleware.auth import get_current_student
        from fastapi.security import HTTPAuthorizationCredentials
        
        mock_verify.return_value = {"sub": "student123"}
        
        mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "Bearer token123"
        
        mock_request = MagicMock()
        mock_request.query_params = {}
        
        result = await get_current_student(mock_request, mock_credentials)
        
        assert result == "student123"

    @pytest.mark.asyncio
    async def test_get_current_student_missing_credentials(self):
        """Test error when credentials missing."""
        from italianollama.api.middleware.auth import get_current_student
        from italianollama.api.exceptions import AuthenticationError
        
        mock_request = MagicMock()
        mock_request.query_params = {}
        
        with pytest.raises(AuthenticationError):
            await get_current_student(mock_request, None)

    @pytest.mark.asyncio
    async def test_get_current_student_query_param_fallback(self):
        """Test fallback to query parameter."""
        from italianollama.api.middleware.auth import get_current_student
        
        mock_request = MagicMock()
        mock_request.query_params = {"student_id": "query_student"}
        
        result = await get_current_student(mock_request, None)
        
        assert result == "query_student"


class TestRequireApiKey:
    """Unit tests for require_api_key dependency."""

    @pytest.mark.asyncio
    async def test_require_api_key_valid(self):
        """Test valid API key."""
        from italianollama.api.middleware.auth import require_api_key
        from fastapi.security import HTTPAuthorizationCredentials
        
        mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "valid-api-key"
        
        mock_request = MagicMock()
        
        result = await require_api_key(mock_request, mock_credentials)
        
        assert result == "valid-api-key"

    @pytest.mark.asyncio
    async def test_require_api_key_missing(self):
        """Test missing API key."""
        from italianollama.api.middleware.auth import require_api_key
        from italianollama.api.exceptions import AuthenticationError
        
        mock_request = MagicMock()
        
        with pytest.raises(AuthenticationError):
            await require_api_key(mock_request, None)

    @pytest.mark.asyncio
    async def test_require_api_key_empty(self):
        """Test empty API key."""
        from italianollama.api.middleware.auth import require_api_key
        from fastapi.security import HTTPAuthorizationCredentials
        from italianollama.api.exceptions import AuthenticationError
        
        mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = ""
        
        mock_request = MagicMock()
        
        with pytest.raises(AuthenticationError):
            await require_api_key(mock_request, mock_credentials)
