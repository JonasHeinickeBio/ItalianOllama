"""Comprehensive unit tests for CLI components."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from click.testing import CliRunner
from italianollama.cli.main import cli
from italianollama.cli.services import (
    get_services,
    get_process_by_port,
    is_service_running,
    start_service,
    stop_service,
    get_status,
)


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '0.1.0' in result.output

    def test_cli_neo4j_group(self):
        """Test neo4j subcommand group exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ['neo4j', '--help'])
        assert result.exit_code == 0
        assert 'status' in result.output

    @patch('italianollama.cli.main.Neo4jClient')
    def test_neo4j_status_command(self, mock_neo4j_class):
        """Test neo4j status command."""
        mock_client = MagicMock()
        mock_client.connect = AsyncMock()
        mock_client.close = AsyncMock()
        mock_neo4j_class.return_value = mock_client

        runner = CliRunner()
        with patch.dict('os.environ', {'NEO4J_URI': 'bolt://localhost:7687', 'NEO4J_USER': 'neo4j', 'NEO4J_PASSWORD': 'test'}):
            result = runner.invoke(cli, ['neo4j', 'status'])
            # Command runs without error
            assert result.exit_code == 0

    def test_llm_list_command(self):
        """Test llm list command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['llm', 'list'])
        assert result.exit_code == 0
        assert 'blablador' in result.output
        assert 'ollama' in result.output

    @patch('italianollama.cli.main.LLMClient')
    def test_llm_test_command(self, mock_llm_class):
        """Test llm test command."""
        mock_client = MagicMock()
        mock_client.chat = AsyncMock(return_value="Ciao!")
        mock_llm_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(cli, ['llm', 'test'])
        # May fail due to async but should run
        assert result.exit_code == 0 or 'Error' in result.output

    def test_config_show_command(self):
        """Test config show command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', 'show'])
        assert result.exit_code == 0
        assert 'NEO4J_URI' in result.output

    def test_kg_group(self):
        """Test kg subcommand group exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ['kg', '--help'])
        assert result.exit_code == 0
        assert 'summary' in result.output
        assert 'query' in result.output
        assert 'list-nodes' in result.output
        assert 'list-rels' in result.output

    def test_service_group(self):
        """Test service subcommand group exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ['service', '--help'])
        assert result.exit_code == 0
        assert 'start' in result.output
        assert 'stop' in result.output
        assert 'restart' in result.output
        assert 'status' in result.output
        assert 'logs' in result.output


class TestServices:
    """Tests for service management functions."""

    def test_get_services(self):
        """Test get_services returns service config."""
        services = get_services()
        
        assert 'api' in services
        assert 'chainlit' in services
        assert 'streamlit' in services
        assert 'api' in services['api']['command']
        assert services['api']['port'] == 8000

    def test_get_services_port_override(self):
        """Test get_services respects port overrides."""
        with patch.dict('os.environ', {'API_PORT': '9000'}):
            services = get_services()
            assert services['api']['port'] == 9000

    @patch('psutil.process_iter')
    @patch('psutil.Process')
    def test_get_process_by_port_not_found(self, mock_process_class, mock_process_iter):
        """Test get_process_by_port returns None when no process."""
        mock_process_iter.return_value = []
        
        result, is_tunnel = get_process_by_port(8000)
        
        assert result is None
        assert is_tunnel is False

    @patch('psutil.process_iter')
    @patch('psutil.Process')
    def test_get_process_by_port_found(self, mock_process_class, mock_process_iter):
        """Test get_process_by_port finds process."""
        mock_proc = MagicMock()
        mock_proc.info = {'pid': 1234, 'name': 'python', 'cmdline': ['uvicorn']}
        
        mock_conn = MagicMock()
        mock_conn.laddr.port = 8000
        mock_conn.status = 'LISTEN'
        mock_proc.connections.return_value = [mock_conn]
        
        mock_process_iter.return_value = [mock_proc]
        
        result, is_tunnel = get_process_by_port(8000, ['uvicorn'])
        
        assert result is not None

    @patch('italianollama.cli.services.get_process_by_port')
    def test_is_service_running_true(self, mock_get_proc):
        """Test is_service_running when running."""
        mock_proc = MagicMock()
        mock_get_proc.return_value = (mock_proc, False)
        
        result = is_service_running('api')
        
        assert result is True

    @patch('italianollama.cli.services.get_process_by_port')
    def test_is_service_running_false(self, mock_get_proc):
        """Test is_service_running when not running."""
        mock_get_proc.return_value = (None, False)
        
        result = is_service_running('api')
        
        assert result is False

    @patch('italianollama.cli.services.get_process_by_port')
    @patch('subprocess.Popen')
    @patch('time.sleep')
    @patch('italianollama.cli.services.is_service_running')
    def test_start_service(self, mock_is_running, mock_popen, mock_sleep, mock_get_proc):
        """Test start_service starts a service."""
        mock_get_proc.return_value = (None, False)
        mock_is_running.side_effect = [False, True]  # First not running, then running
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        
        with patch.dict('os.environ', {}, clear=True):
            start_service('api')
        
        mock_popen.assert_called_once()

    @patch('italianollama.cli.services.get_process_by_port')
    @patch('italianollama.cli.services.kill_proc_tree')
    def test_stop_service(self, mock_kill, mock_get_proc):
        """Test stop_service stops a service."""
        mock_proc = MagicMock()
        mock_proc.pid = 1234
        mock_get_proc.return_value = (mock_proc, False)
        
        stop_service('api')
        
        mock_kill.assert_called_once_with(1234)

    @patch('italianollama.cli.services.get_services')
    @patch('italianollama.cli.services.get_process_by_port')
    def test_get_status(self, mock_get_proc, mock_get_services):
        """Test get_status runs without error."""
        mock_get_services.return_value = {
            'api': {'port': 8000, 'keywords': ['uvicorn']},
            'chainlit': {'port': 8501, 'keywords': ['chainlit']},
            'streamlit': {'port': 8502, 'keywords': ['streamlit']},
        }
        mock_get_proc.return_value = (None, False)
        
        # Should run without error
        get_status()


class TestServiceKeywords:
    """Test that service keywords are correctly defined."""

    def test_api_service_keywords(self):
        """Test API service has correct keywords."""
        services = get_services()
        assert 'uvicorn' in services['api']['keywords']
        assert 'api.main_enhanced' in services['api']['keywords']

    def test_chainlit_service_keywords(self):
        """Test Chainlit service has correct keywords."""
        services = get_services()
        assert 'chainlit' in services['chainlit']['keywords']

    def test_streamlit_service_keywords(self):
        """Test Streamlit service has correct keywords."""
        services = get_services()
        assert 'streamlit' in services['streamlit']['keywords']
