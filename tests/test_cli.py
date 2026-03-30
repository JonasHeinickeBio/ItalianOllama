"""Unit tests for CLI."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from click.testing import CliRunner


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_import(self):
        """Test CLI module can be imported."""
        from italianollama.cli.main import cli
        assert cli is not None

    def test_cli_help(self):
        """Test CLI help output."""
        from italianollama.cli.main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_neo4j_group(self):
        """Test neo4j subcommand exists."""
        from italianollama.cli.main import cli, neo4j
        runner = CliRunner()
        result = runner.invoke(cli, ["neo4j", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output

    def test_llm_group(self):
        """Test llm subcommand exists."""
        from italianollama.cli.main import cli, llm
        runner = CliRunner()
        result = runner.invoke(cli, ["llm", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output

    def test_config_group(self):
        """Test config subcommand exists."""
        from italianollama.cli.main import cli, config
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])
        assert result.exit_code == 0
        assert "show" in result.output


class TestCLIVersion:
    """Tests for CLI version."""

    def test_version_command(self):
        """Test version command."""
        from italianollama.cli.main import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
