"""Comprehensive tests for frontend API client with mocking."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


class TestBackendClientMethods:
    """Tests for BackendClient methods."""

    @pytest.mark.asyncio
    async def test_get_student_profile_http_error(self):
        """Test HTTP error handling in get_student_profile."""
        from italianollama.frontend.api.client import BackendClient
        from italianollama.frontend.api.errors import BackendError

        with patch('italianollama.frontend.api.client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(backend_url="http://localhost:8000")

            client = BackendClient()
            mock_httpx = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_httpx.get = AsyncMock(return_value=mock_response)
            client._client = mock_httpx

            with pytest.raises(BackendError):
                await client.get_student_profile("test")

    @pytest.mark.asyncio
    async def test_get_student_profile_httpx_error(self):
        """Test httpx error handling in get_student_profile."""
        from italianollama.frontend.api.client import BackendClient
        from italianollama.frontend.api.errors import BackendConnectionError

        with patch('italianollama.frontend.api.client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(backend_url="http://localhost:8000")

            client = BackendClient()
            mock_httpx = AsyncMock()
            mock_httpx.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            client._client = mock_httpx

            with pytest.raises(BackendConnectionError):
                await client.get_student_profile("test")

    @pytest.mark.asyncio
    async def test_create_student_http_error(self):
        """Test HTTP error in create_student."""
        from italianollama.frontend.api.client import BackendClient
        from italianollama.frontend.api.errors import BackendError

        with patch('italianollama.frontend.api.client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(backend_url="http://localhost:8000")

            client = BackendClient()
            mock_httpx = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_httpx.post = AsyncMock(return_value=mock_response)
            client._client = mock_httpx

            with pytest.raises(BackendError):
                await client.create_student("test", "Test")

    @pytest.mark.asyncio
    async def test_create_student_connection_error(self):
        """Test connection error in create_student."""
        from italianollama.frontend.api.client import BackendClient
        from italianollama.frontend.api.errors import BackendConnectionError

        with patch('italianollama.frontend.api.client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(backend_url="http://localhost:8000")

            client = BackendClient()
            mock_httpx = AsyncMock()
            mock_httpx.post = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
            client._client = mock_httpx

            with pytest.raises(BackendConnectionError):
                await client.create_student("test", "Test")

    @pytest.mark.asyncio
    async def test_get_auth_token_http_error(self):
        """Test HTTP error in get_auth_token."""
        from italianollama.frontend.api.client import BackendClient

        with patch('italianollama.frontend.api.client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(backend_url="http://localhost:8000")

            client = BackendClient()
            mock_httpx = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_httpx.post = AsyncMock(return_value=mock_response)
            client._client = mock_httpx

            result = await client.get_auth_token("test")
            assert result is None

    @pytest.mark.asyncio
    async def test_stream_chat_completions_http_error(self):
        """Test HTTP error in stream_chat_completions."""
        from italianollama.frontend.api.client import BackendClient
        from italianollama.frontend.api.errors import StreamingError

        with patch('italianollama.frontend.api.client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(backend_url="http://localhost:8000")

            client = BackendClient()
            mock_httpx = AsyncMock()
            import httpx
            mock_httpx.stream = MagicMock(side_effect=httpx.HTTPError("Stream error"))
            client._client = mock_httpx

            with pytest.raises(StreamingError):
                # Need to iterate the async generator
                async for _ in client.stream_chat_completions([{"role": "user", "content": "test"}]):
                    pass

    @pytest.mark.asyncio
    async def test_stream_chat_completions_json_error(self):
        """Test JSON error in stream_chat_completions."""
        from italianollama.frontend.api.client import BackendClient

        with patch('italianollama.frontend.api.client.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(backend_url="http://localhost:8000")

            client = BackendClient()
            mock_httpx = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            # Return invalid JSON
            mock_response.aiter_lines = AsyncMock(
                return_value=iter(["data: invalid json"])
            )
            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.stream = MagicMock(return_value=mock_context)
            client._client = mock_httpx

            # Should skip the invalid line and not raise
            tokens = []
            async for token in client.stream_chat_completions([{"role": "user", "content": "test"}]):
                tokens.append(token)
            # No tokens from invalid JSON
            assert len(tokens) == 0


class TestClientConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_get_student_profile_connection(self):
        """Test get_student_profile returns None on connection error."""
        from italianollama.frontend.api.errors import BackendConnectionError

        with patch('italianollama.frontend.api.client.get_backend_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_student_profile = AsyncMock(
                side_effect=BackendConnectionError("Connection failed")
            )
            mock_get_client.return_value = mock_client

            from italianollama.frontend.api.client import get_student_profile
            result = await get_student_profile("test")
            assert result is None

    @pytest.mark.asyncio
    async def test_create_student_backend_error(self):
        """Test create_student returns None on backend error."""
        from italianollama.frontend.api.errors import BackendError

        with patch('italianollama.frontend.api.client.get_backend_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.create_student = AsyncMock(
                side_effect=BackendError("Backend error")
            )
            mock_get_client.return_value = mock_client

            from italianollama.frontend.api.client import create_student
            result = await create_student("test", "Test")
            assert result is None
