"""Tests for italianollama.api.middleware.auth module."""
from datetime import timedelta
from unittest.mock import MagicMock

import pytest

import italianollama.api.config as config_module
from italianollama.api.middleware.auth import (
    create_access_token,
    get_current_student,
    require_api_key,
    verify_access_token,
)


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch):
    monkeypatch.setattr(config_module, "_settings", None)
    yield
    monkeypatch.setattr(config_module, "_settings", None)


class TestCreateAccessToken:
    def test_creates_token(self):
        token = create_access_token("student123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_subject(self):
        token = create_access_token("student123")
        payload = verify_access_token(token)
        assert payload["sub"] == "student123"

    def test_custom_expiry(self):
        token = create_access_token("student123", expires_delta=timedelta(hours=1))
        payload = verify_access_token(token)
        assert payload["sub"] == "student123"

    def test_default_expiry(self):
        token = create_access_token("student123")
        payload = verify_access_token(token)
        assert "exp" in payload
        assert "iat" in payload


class TestVerifyAccessToken:
    def test_valid_token(self):
        token = create_access_token("student123")
        payload = verify_access_token(token)
        assert payload["sub"] == "student123"

    def test_expired_token(self):
        from italianollama.api.exceptions import AuthenticationError

        token = create_access_token("student123", expires_delta=timedelta(seconds=-1))
        with pytest.raises(AuthenticationError) as exc_info:
            verify_access_token(token)
        assert "expired" in str(exc_info.value.detail).lower()

    def test_invalid_token(self):
        from italianollama.api.exceptions import AuthenticationError

        with pytest.raises(AuthenticationError):
            verify_access_token("invalid.token.here")

    def test_tampered_token(self):
        from italianollama.api.exceptions import AuthenticationError

        token = create_access_token("student123")
        tampered = token[:-5] + "xxxxx"
        with pytest.raises(AuthenticationError):
            verify_access_token(tampered)


class TestGetCurrentStudent:
    @pytest.mark.asyncio
    async def test_valid_credentials(self):
        from fastapi.security import HTTPAuthorizationCredentials

        token = create_access_token("student123")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        request = MagicMock()

        result = await get_current_student(request, credentials)
        assert result == "student123"

    @pytest.mark.asyncio
    async def test_missing_credentials(self):
        from italianollama.api.exceptions import AuthenticationError

        request = MagicMock()
        with pytest.raises(AuthenticationError) as exc_info:
            await get_current_student(request, None)
        assert "missing" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        from fastapi.security import HTTPAuthorizationCredentials
        from italianollama.api.exceptions import AuthenticationError

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.token.here"
        )
        request = MagicMock()
        with pytest.raises(AuthenticationError):
            await get_current_student(request, credentials)

    @pytest.mark.asyncio
    async def test_token_without_sub(self):
        import jwt
        from italianollama.api.config import get_settings
        from italianollama.api.exceptions import AuthenticationError
        from fastapi.security import HTTPAuthorizationCredentials

        settings = get_settings()
        # Create token without 'sub' claim
        token = jwt.encode(
            {"exp": 9999999999, "iat": 1000000000},
            settings.auth_secret,
            algorithm=settings.jwt_algorithm,
        )
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        request = MagicMock()
        with pytest.raises(AuthenticationError) as exc_info:
            await get_current_student(request, credentials)
        assert "payload" in str(exc_info.value.detail).lower()


class TestRequireApiKey:
    @pytest.mark.asyncio
    async def test_missing_credentials(self):
        from italianollama.api.exceptions import AuthenticationError

        request = MagicMock()
        with pytest.raises(AuthenticationError) as exc_info:
            await require_api_key(request, None)
        detail_str = str(exc_info.value.detail).lower()
        assert "missing" in detail_str or "api key" in detail_str

    @pytest.mark.asyncio
    async def test_api_key_not_implemented(self):
        from fastapi.security import HTTPAuthorizationCredentials
        from italianollama.api.exceptions import AuthenticationError

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="some-api-key")
        request = MagicMock()
        with pytest.raises(AuthenticationError) as exc_info:
            await require_api_key(request, credentials)
        assert "not implemented" in str(exc_info.value.detail).lower()
