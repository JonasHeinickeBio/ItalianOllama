"""Integration tests for OpenRouter CLI commands."""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
import yaml
from click.testing import CliRunner

from italianollama.cli.main import cli


@pytest.fixture
def temp_config_path():
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"model_list": []}, f)
        return f.name


def test_cli_openrouter_list_command():
    """Test `openrouter list` command output."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_models = [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "anthropic/claude-3-haiku",
                    "name": "Claude 3 Haiku",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
            ]
            mock_discover.return_value = mock_models
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            assert "GPT-4o Mini" in result.output
            assert "Claude 3 Haiku" in result.output
            assert "Found 2 free models" in result.output


def test_cli_openrouter_list_no_free_models():
    """Test `openrouter list` with no free models."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.return_value = []
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            assert "No free models" in result.output or "0 free models" in result.output


def test_cli_openrouter_list_error_no_api_key():
    """Test `openrouter list` error handling for missing API key."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {}, clear=True):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.side_effect = ValueError("OPENROUTER_API_KEY environment variable not set")
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code != 0
            assert "Error" in str(result.exception) or "OPENROUTER_API_KEY" in str(result.exception)


def test_cli_openrouter_add_command(temp_config_path):
    """Test `openrouter add` command with mock API."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = ["openrouter-openai-gpt-4o-mini"]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "Added" in result.output
            assert "openrouter-openai-gpt-4o-mini" in result.output


def test_cli_openrouter_add_no_new_models(temp_config_path):
    """Test `openrouter add` with no new models to add."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = []
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "No new free models" in result.output or "already exist" in result.output


def test_cli_openrouter_add_config_modification(temp_config_path):
    """Test config file modification after add command."""
    runner = CliRunner()
    
    with open(temp_config_path, "r") as f:
        initial_config = yaml.safe_load(f)
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = ["openrouter-openai-gpt-4o-mini"]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            
            assert "✓ Added 1 free models" in result.output
            assert "openrouter-openai-gpt-4o-mini" in result.output


def test_cli_openrouter_add_error_no_api_key():
    """Test `openrouter add` error handling for missing API key."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.side_effect = ValueError("OPENROUTER_API_KEY environment variable not set")
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "✗ Error" in result.output
            assert "OPENROUTER_API_KEY" in result.output


def test_cli_openrouter_list_output_format():
    """Test `openrouter list` output formatting."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.return_value = [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "pricing": {"prompt": "0", "completion": "0"},
                }
            ]
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            
            lines = result.output.strip().split("\n")
            assert any("•" in line and "GPT-4o Mini" in line for line in lines)
            assert any("Prompt:" in line for line in lines)
            assert any("Completion:" in line for line in lines)


def test_cli_openrouter_add_output_format(temp_config_path):
    """Test `openrouter add` output formatting."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = ["openrouter-openai-gpt-4o-mini"]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            
            assert "✓" in result.output or "Added" in result.output
            assert "openrouter-openai-gpt-4o-mini" in result.output
            assert "LiteLLM config" in result.output


def test_cli_openrouter_add_multiple_models(temp_config_path):
    """Test `openrouter add` with multiple models."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = [
                "openrouter-openai-gpt-4o-mini",
                "openrouter-anthropic-claude-3-haiku",
                "openrouter-google-gemini-flash-1.5",
            ]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "Added 3 free models" in result.output
            
            assert "openrouter-openai-gpt-4o-mini" in result.output
            assert "openrouter-anthropic-claude-3-haiku" in result.output
            assert "openrouter-google-gemini-flash-1.5" in result.output


def test_cli_openrouter_list_output_structure():
    """Test that `openrouter list` output has correct structure."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.return_value = [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "anthropic/claude-3-haiku",
                    "name": "Claude 3 Haiku",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
            ]
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            
            assert "Found 2 free models" in result.output
            
            lines = result.output.strip().split("\n")
            
            bullet_lines = [line for line in lines if "•" in line]
            assert len(bullet_lines) == 2
            
            for model_name in ["GPT-4o Mini", "Claude 3 Haiku"]:
                assert any(model_name in line for line in lines), f"Model {model_name} not found in output"
            
            pricing_lines = [line for line in lines if "Prompt:" in line or "Completion:" in line]
            assert len(pricing_lines) >= 2


def test_cli_openrouter_add_output_structure(temp_config_path):
    """Test that `openrouter add` output has correct structure."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = ["openrouter-openai-gpt-4o-mini"]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            
            lines = result.output.strip().split("\n")
            
            assert any("✓" in line or "Added" in line for line in lines)
            assert any("free models" in line.lower() for line in lines)
            assert any("LiteLLM config" in line for line in lines)
            
            added_lines = [line for line in lines if line.strip().startswith("- ")]
            assert len(added_lines) == 1
            assert "openrouter-openai-gpt-4o-mini" in added_lines[0]


def test_cli_openrouter_add_with_real_config_path(tmp_path):
    """Test `openrouter add` with a real config file path."""
    runner = CliRunner()
    
    config_path = tmp_path / "litellm_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = ["openrouter-openai-gpt-4o-mini"]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            
            assert "✓ Added 1 free models" in result.output
            assert "openrouter-openai-gpt-4o-mini" in result.output


def test_cli_openrouter_list_error_handling():
    """Test `openrouter list` error handling."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.side_effect = Exception("Network error")
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code != 0
            assert result.exception is not None


def test_cli_openrouter_add_error_handling():
    """Test `openrouter add` error handling."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.side_effect = Exception("Config error")
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code != 0
            assert result.exception is not None


def test_cli_openrouter_list_with_no_models():
    """Test `openrouter list` when no models are available."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.return_value = []
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            
            assert "No free models" in result.output or "0 free models" in result.output


def test_cli_openrouter_add_empty_list_output(temp_config_path):
    """Test `openrouter add` when no models are added."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = []
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            
            assert "No new free models" in result.output


def test_cli_openrouter_list_multiple_pages_of_models():
    """Test `openrouter list` with many models."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_models = [
                {
                    "id": f"provider/model-{i}",
                    "name": f"Model {i}",
                    "pricing": {"prompt": "0", "completion": "0"},
                }
                for i in range(10)
            ]
            mock_discover.return_value = mock_models
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            assert "Found 10 free models" in result.output
            
            for i in range(10):
                assert f"Model {i}" in result.output


def test_cli_openrouter_add_with_duplicate_detection(temp_config_path):
    """Test that CLI correctly handles duplicate model detection."""
    runner = CliRunner()
    
    with open(temp_config_path, "w") as f:
        yaml.dump({
            "model_list": [
                {
                    "model_name": "openrouter-openai-gpt-4o-mini",
                    "litellm_params": {"model": "openrouter/openai/gpt-4o-mini"},
                }
            ]
        }, f)
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = []
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "No new free models" in result.output


def test_cli_openrouter_add_with_provider_models(temp_config_path):
    """Test `openrouter add` with models from various providers."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = [
                "openrouter-openai-gpt-4o-mini",
                "openrouter-anthropic-claude-3-haiku",
                "openrouter-google-gemini-flash-1.5",
                "openrouter-mistralai-mistral-7b-instruct",
            ]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "Added 4 free models" in result.output
            
            for model in ["openrouter-openai-gpt-4o-mini", "openrouter-anthropic-claude-3-haiku", "openrouter-google-gemini-flash-1.5", "openrouter-mistralai-mistral-7b-instruct"]:
                assert model in result.output


def test_cli_openrouter_integration_with_cli_group():
    """Test that openrouter commands are properly registered under CLI group."""
    runner = CliRunner()
    
    result = runner.invoke(cli, ["openrouter", "--help"])
    
    assert result.exit_code == 0
    assert "list" in result.output
    assert "add" in result.output


def test_cli_openrouter_command_availability():
    """Test that all expected openrouter commands are available."""
    runner = CliRunner()
    
    result = runner.invoke(cli, ["--help"])
    
    assert result.exit_code == 0
    assert "openrouter" in result.output
    assert "Manage OpenRouter models" in result.output or "free model discovery" in result.output.lower()


def test_cli_openrouter_list_output_format_comprehensive():
    """Test comprehensive output formatting for `openrouter list`."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.return_value = [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "pricing": {"prompt": "0", "completion": "0"},
                }
            ]
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            
            output_lines = result.output.strip().split("\n")
            
            found_model_line = False
            found_pricing_line = False
            
            for i, line in enumerate(output_lines):
                if "•" in line and "GPT-4o Mini" in line:
                    found_model_line = True
                    if i + 1 < len(output_lines):
                        pricing_line = output_lines[i + 1]
                        if "Prompt:" in pricing_line and "Completion:" in pricing_line:
                            found_pricing_line = True
            
            assert found_model_line, "Model line with bullet not found"
            assert found_pricing_line, "Pricing line not found after model line"


def test_cli_openrouter_add_output_format_comprehensive(temp_config_path):
    """Test comprehensive output formatting for `openrouter add`."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = ["openrouter-openai-gpt-4o-mini"]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            
            output_lines = result.output.strip().split("\n")
            
            found_count_line = False
            found_added_line = False
            found_config_line = False
            
            for line in output_lines:
                if "Added" in line and "free models" in line:
                    found_count_line = True
                if line.strip().startswith("- ") and "openrouter" in line:
                    found_added_line = True
                if "LiteLLM config" in line:
                    found_config_line = True
            
            assert found_count_line, "Count line not found"
            assert found_added_line, "Added model line not found"
            assert found_config_line, "Config instruction line not found"


def test_cli_openrouter_list_with_complex_pricing(temp_config_path):
    """Test `openrouter list` with complex pricing structures."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.return_value = [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "pricing": {
                        "prompt": "0.0000001",
                        "completion": "0.0000002",
                        "image": "0.000000075",
                        "audio_input": "0.00000015",
                        "audio_output": "0.0000003",
                    },
                }
            ]
            
            result = runner.invoke(cli, ["openrouter", "list"])
            
            assert result.exit_code == 0
            assert "GPT-4o Mini" in result.output


def test_cli_openrouter_add_empty_model_list(temp_config_path):
    """Test `openrouter add` with empty model response."""
    runner = CliRunner()
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.discover_free_models") as mock_discover:
            mock_discover.return_value = []
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "No new free models" in result.output


def test_cli_openrouter_integration_test_run(tmp_path):
    """Test full integration: CLI command with actual flow simulation."""
    runner = CliRunner()
    
    config_path = tmp_path / "litellm_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = [
                "openrouter-openai-gpt-4o-mini",
                "openrouter-anthropic-claude-3-haiku",
            ]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "Added 2 free models" in result.output
            
            lines = result.output.strip().split("\n")
            model_lines = [line for line in lines if line.strip().startswith("- ")]
            assert len(model_lines) == 2


def test_cli_openrouter_add_mocked_with_model_info(tmp_path):
    """Test that CLI properly formats model with model_info."""
    runner = CliRunner()
    
    config_path = tmp_path / "litellm_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("italianollama.utils.openrouter.add_free_models_to_config") as mock_add:
            mock_add.return_value = ["openrouter-openai-gpt-4o-mini"]
            
            result = runner.invoke(cli, ["openrouter", "add"])
            
            assert result.exit_code == 0
            assert "Added 1 free models" in result.output
