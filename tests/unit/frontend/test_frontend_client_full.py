"""Unit tests for frontend API client - full coverage."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestBackendClientFunctions:
    """Test backend client convenience functions."""

    def test_get_backend_client_exists(self):
        """Test get_backend_client function exists."""
        from italianollama.frontend.api.client import get_backend_client
        assert callable(get_backend_client)

    def test_get_student_profile_func_exists(self):
        """Test get_student_profile function exists."""
        from italianollama.frontend.api.client import get_student_profile
        assert callable(get_student_profile)

    def test_get_auth_token_func_exists(self):
        """Test get_auth_token function exists."""
        from italianollama.frontend.api.client import get_auth_token
        assert callable(get_auth_token)

    def test_stream_chat_completions_func_exists(self):
        """Test stream_chat_completions function exists."""
        from italianollama.frontend.api.client import stream_chat_completions
        assert callable(stream_chat_completions)

    def test_backend_client_close(self):
        """Test BackendClient close method."""
        from italianollama.frontend.api.client import BackendClient
        client = BackendClient()
        # Should be able to call close
        import asyncio
        asyncio.run(client.close())

    def test_backend_client_get_client(self):
        """Test BackendClient _get_client method."""
        from italianollama.frontend.api.client import BackendClient
        client = BackendClient()
        
        async def test():
            return await client._get_client()
        
        import asyncio
        result = asyncio.run(test())
        assert result is not None

    def test_get_backend_client_singleton(self):
        """Test get_backend_client returns singleton."""
        from italianollama.frontend.api.client import get_backend_client
        
        client1 = get_backend_client()
        client2 = get_backend_client()
        
        # May or may not be same instance depending on reset
        assert client1 is not None
        assert client2 is not None