"""Tests for chainlit app module."""

import pytest
from unittest.mock import MagicMock, patch


class TestChainlitApp:
    """Tests for chainlit app."""

    def test_chainlit_app_exists(self):
        """Test chainlit_app module can be imported."""
        # Just verify the module exists
        import italianollama.frontend.chainlit_app
        assert italianollama.frontend.chainlit_app is not None


class TestChainlitConfig:
    """Tests for chainlit config."""

    def test_config_exists(self):
        """Test config module exists."""
        import italianollama.frontend.config
        assert italianollama.frontend.config is not None

    def test_get_settings_exists(self):
        """Test get_settings exists."""
        from italianollama.frontend.config import get_settings
        assert callable(get_settings)


class TestFrontendErrors:
    """Tests for frontend errors."""

    def test_backend_error_exists(self):
        """Test BackendError exists."""
        from italianollama.frontend.api.errors import BackendError
        assert BackendError is not None

    def test_backend_connection_error_exists(self):
        """Test BackendConnectionError exists."""
        from italianollama.frontend.api.errors import BackendConnectionError
        assert BackendConnectionError is not None

    def test_streaming_error_exists(self):
        """Test StreamingError exists."""
        from italianollama.frontend.api.errors import StreamingError
        assert StreamingError is not None

    def test_student_not_found_error_exists(self):
        """Test StudentNotFoundError exists."""
        from italianollama.frontend.api.errors import StudentNotFoundError
        assert StudentNotFoundError is not None

    def test_error_inheritance(self):
        """Test error inheritance."""
        from italianollama.frontend.api.errors import (
            BackendError,
            BackendConnectionError,
            StreamingError,
            StudentNotFoundError,
        )
        assert issubclass(BackendConnectionError, BackendError)
        assert issubclass(StreamingError, BackendError)
        assert issubclass(StudentNotFoundError, BackendError)


class TestFrontendAPIImports:
    """Tests for frontend API imports."""

    def test_client_import(self):
        """Test client module import."""
        from italianollama.frontend.api import client
        assert client is not None

    def test_errors_import(self):
        """Test errors module import."""
        from italianollama.frontend.api import errors
        assert errors is not None

    def test_backend_client_class_exists(self):
        """Test BackendClient class exists."""
        from italianollama.frontend.api.client import BackendClient
        assert BackendClient is not None

    def test_get_backend_client_exists(self):
        """Test get_backend_client function exists."""
        from italianollama.frontend.api.client import get_backend_client
        assert callable(get_backend_client)

    def test_get_student_profile_exists(self):
        """Test get_student_profile function exists."""
        from italianollama.frontend.api.client import get_student_profile
        assert callable(get_student_profile)

    def test_create_student_exists(self):
        """Test create_student function exists."""
        from italianollama.frontend.api.client import create_student
        assert callable(create_student)

    def test_get_auth_token_exists(self):
        """Test get_auth_token function exists."""
        from italianollama.frontend.api.client import get_auth_token
        assert callable(get_auth_token)

    def test_stream_chat_completions_exists(self):
        """Test stream_chat_completions function exists."""
        from italianollama.frontend.api.client import stream_chat_completions
        assert callable(stream_chat_completions)
