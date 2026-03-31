"""Unit tests for CLI services module - using actual source functions."""

import pytest
from unittest.mock import MagicMock, patch
from italianollama.cli import services


class TestServicesModule:
    """Tests for services module using get_services() function."""

    def test_services_defined(self):
        """Test that services are defined via get_services()."""
        result = services.get_services()

        assert "api" in result
        assert "chainlit" in result
        assert "streamlit" in result

    def test_services_have_ports(self):
        """Test that services have correct default ports."""
        result = services.get_services()

        assert result["api"]["port"] == 8000
        assert result["chainlit"]["port"] == 8501
        assert result["streamlit"]["port"] == 8502

    def test_services_have_commands(self):
        """Test that services have commands."""
        result = services.get_services()

        assert "command" in result["api"]
        assert "command" in result["chainlit"]
        assert "command" in result["streamlit"]

    def test_services_have_keywords(self):
        """Test that services have keywords for process detection."""
        result = services.get_services()

        assert "keywords" in result["api"]
        assert "keywords" in result["chainlit"]
        assert "keywords" in result["streamlit"]

    def test_api_service_command_contains_port(self):
        """Test API service command includes port variable."""
        result = services.get_services()

        assert "8000" in result["api"]["command"]

    def test_chainlit_service_command_contains_port(self):
        """Test Chainlit service command includes port variable."""
        result = services.get_services()

        assert "8501" in result["chainlit"]["command"]

    def test_streamlit_service_command_contains_port(self):
        """Test Streamlit service command includes port variable."""
        result = services.get_services()

        assert "8502" in result["streamlit"]["command"]

    def test_streamlit_service_has_env_vars(self):
        """Test Streamlit service has environment variables for URLs."""
        result = services.get_services()

        assert "env" in result["streamlit"]
        assert "CHAINLIT_URL" in result["streamlit"]["env"]
        assert "BACKEND_URL" in result["streamlit"]["env"]


class TestServiceFunctionsImport:
    """Test that service functions can be imported."""

    def test_get_process_by_port_import(self):
        """Test get_process_by_port can be imported."""
        from italianollama.cli.services import get_process_by_port
        assert callable(get_process_by_port)

    def test_is_service_running_import(self):
        """Test is_service_running can be imported."""
        from italianollama.cli.services import is_service_running
        assert callable(is_service_running)

    def test_start_service_import(self):
        """Test start_service can be imported."""
        from italianollama.cli.services import start_service
        assert callable(start_service)

    def test_stop_service_import(self):
        """Test stop_service can be imported."""
        from italianollama.cli.services import stop_service
        assert callable(stop_service)

    def test_get_status_import(self):
        """Test get_status can be imported."""
        from italianollama.cli.services import get_status
        assert callable(get_status)

    def test_kill_proc_tree_import(self):
        """Test kill_proc_tree can be imported."""
        from italianollama.cli.services import kill_proc_tree
        assert callable(kill_proc_tree)


class TestServicePortOverrides:
    """Test port override via environment variables."""

    def test_api_port_override(self):
        """Test API port can be overridden via env var."""
        with patch.dict('os.environ', {'API_PORT': '9000'}):
            result = services.get_services()
            assert result["api"]["port"] == 9000

    def test_chainlit_port_override(self):
        """Test Chainlit port can be overridden via env var."""
        with patch.dict('os.environ', {'CHAINLIT_PORT': '9001'}):
            result = services.get_services()
            assert result["chainlit"]["port"] == 9001

    def test_streamlit_port_override(self):
        """Test Streamlit port can be overridden via env var."""
        with patch.dict('os.environ', {'STREAMLIT_PORT': '9002'}):
            result = services.get_services()
            assert result["streamlit"]["port"] == 9002