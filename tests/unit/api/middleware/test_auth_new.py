"""Unit tests for auth middleware module."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone
import jwt

from italianollama.api.middleware.auth import (
    create_access_token,
    verify_access_token,
    get_current_student,
    require_api_key,
    security,
)
from italianollama.api.exceptions import AuthenticationError


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_basic(self):
        """Test basic token creation."""
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4
            )

            token = create_access_token("student123")

            assert token is not None
            assert isinstance(token, str)

    def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiry."""
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4
            )

            expires = timedelta(hours=2)
            token = create_access_token("student123", expires)

            assert token is not None

    def test_create_access_token_payload(self):
        """Test token contains correct payload."""
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256",
                jwt_expiration_hours=4
            )

            token = create_access_token("student456")

            # Decode and verify payload
            payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
            assert payload["sub"] == "student456"
            assert "exp" in payload
            assert "iat" in payload


class TestVerifyAccessToken:
    """Tests for verify_access_token function."""

    def test_verify_valid_token(self):
        """Test verification of valid token."""
        # Create token without mocking settings
        from datetime import datetime, timedelta, timezone
        import jwt

        secret = "test-secret-key-that-is-long-enough"
        payload = {
            "sub": "student123",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")

        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret=secret,
                jwt_algorithm="HS256"
            )

            payload = verify_access_token(token)
            assert payload["sub"] == "student123"

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256"
            )

            # Create expired token
            expired_payload = {
                "sub": "student123",
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),
                "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            }
            token = jwt.encode(expired_payload, "test-secret", algorithm="HS256")

            with pytest.raises(AuthenticationError) as exc_info:
                verify_access_token(token)

            assert "expired" in str(exc_info.value.detail).lower()

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256"
            )

            with pytest.raises(AuthenticationError):
                verify_access_token("invalid-token-string")

    def test_verify_wrong_secret(self):
        """Test verification with wrong secret."""
        secret = "test-secret-key-that-is-long-enough"
        wrong_secret = "different-secret-key-that-is-also-long"

        # Create token with one secret
        payload = {
            "sub": "student123",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")

        # Verify with different secret
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret=wrong_secret,
                jwt_algorithm="HS256"
            )

            with pytest.raises(AuthenticationError):
                verify_access_token(token)


class TestGetCurrentStudent:
    """Tests for get_current_student dependency."""

    @pytest.mark.asyncio
    async def test_get_current_student_with_valid_token(self):
        """Test extraction of student from valid token."""
        from datetime import datetime, timedelta, timezone
        import jwt

        secret = "test-secret-key-that-is-long-enough"
        payload = {
            "sub": "student123",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, secret, algorithm="HS256")

        # Create mock request and credentials
        mock_request = MagicMock()
        mock_request.query_params = {}

        mock_credentials = MagicMock()
        mock_credentials.credentials = token

        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(

                auth_secret=secret,
                jwt_algorithm="HS256"
            )










            student_id = await get_current_student(mock_request, mock_credentials)

            assert student_id == "student123"

    @pytest.mark.asyncio
    async def test_get_current_student_no_credentials(self):
        """Test error when no credentials provided."""
        mock_request = MagicMock()
        mock_request.query_params = {}

        with pytest.raises(AuthenticationError):
            await get_current_student(mock_request, None)

    @pytest.mark.asyncio
    async def test_get_current_student_query_param_fallback(self):
        """Test fallback to query parameter."""
        mock_request = MagicMock()
        mock_request.query_params = {"student_id": "query-student"}

        student_id = await get_current_student(mock_request, None)

        assert student_id == "query-student"

    @pytest.mark.asyncio
    async def test_get_current_student_invalid_token(self):
        """Test error with invalid token."""
        mock_request = MagicMock()
        mock_request.query_params = {}

        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"

        with pytest.raises(AuthenticationError):
            await get_current_student(mock_request, mock_credentials)

    @pytest.mark.asyncio
    async def test_get_current_student_empty_sub(self):
        """Test error when token has no sub claim."""
        with patch('italianollama.api.middleware.auth.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(
                auth_secret="test-secret",
                jwt_algorithm="HS256"
            )

            # Create token without sub
            payload = {
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            }
            token = jwt.encode(payload, "test-secret", algorithm="HS256")

            mock_request = MagicMock()
            mock_request.query_params = {}

            mock_credentials = MagicMock()
            mock_credentials.credentials = token

            with pytest.raises(AuthenticationError):
                await get_current_student(mock_request, mock_credentials)


class TestRequireAPIKey:
    """Tests for require_api_key dependency."""

    @pytest.mark.asyncio
    async def test_require_api_key_valid(self):
        """Test with valid API key."""
        mock_request = MagicMock()

        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid-api-key"

        result = await require_api_key(mock_request, mock_credentials)

        assert result == "valid-api-key"

    @pytest.mark.asyncio
    async def test_require_api_key_missing(self):
        """Test error when API key missing."""
        mock_request = MagicMock()

        with pytest.raises(AuthenticationError):
            await require_api_key(mock_request, None)

    @pytest.mark.asyncio
    async def test_require_api_key_empty(self):
        """Test error when API key is empty."""
        mock_request = MagicMock()

        mock_credentials = MagicMock()
        mock_credentials.credentials = ""

        with pytest.raises(AuthenticationError):
            await require_api_key(mock_request, mock_credentials)
