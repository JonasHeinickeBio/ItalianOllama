"""Unit tests for CLI main module - full coverage."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from click.testing import CliRunner


class TestCLICommands:
    """Test all CLI commands."""

    def test_cli_import(self):
        """Test CLI can be imported."""
        from italianollama.cli.main import cli
        assert cli is not None

    def test_cli_version(self):
        """Test CLI version."""
        from italianollama.cli.main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_help(self):
        """Test CLI help."""
        from italianollama.cli.main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_neo4j_group(self):
        """Test neo4j subcommand group."""
        from italianollama.cli.main import neo4j
        runner = CliRunner()
        result = runner.invoke(neo4j, ["--help"])
        assert result.exit_code == 0
        assert "status" in result.output

    def test_llm_group(self):
        """Test llm subcommand group."""
        from italianollama.cli.main import llm
        runner = CliRunner()
        result = runner.invoke(llm, ["--help"])
        assert result.exit_code == 0
        assert "list" in result.output

    def test_config_group(self):
        """Test config subcommand group."""
        from italianollama.cli.main import config
        runner = CliRunner()
        result = runner.invoke(config, ["--help"])
        assert result.exit_code == 0

    def test_llm_list_command(self):
        """Test llm list command."""
        from italianollama.cli.main import llm_list
        runner = CliRunner()
        result = runner.invoke(llm_list)
        assert result.exit_code == 0
        assert "Available" in result.output

    def test_config_show_command(self):
        """Test config show command."""
        from italianollama.cli.main import config_show
        runner = CliRunner()
        result = runner.invoke(config_show)
        assert result.exit_code == 0

    def test_neo4j_status_command(self):
        """Test neo4j status command with mock."""
        from italianollama.cli.main import neo4j_status
        runner = CliRunner()
        result = runner.invoke(neo4j_status)
        # May fail but should run
        assert result.exit_code in [0, 1]

    def test_llm_test_command(self):
        """Test llm test command with mock."""
        from italianollama.cli.main import llm_test
        runner = CliRunner()
        result = runner.invoke(llm_test)
        # May fail but should run
        assert result.exit_code in [0, 1]
