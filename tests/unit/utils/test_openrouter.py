"""Tests for OpenRouter API utilities."""

import pytest
from unittest.mock import AsyncMock, Mock, patch





@pytest.mark.asyncio
async def test_discover_free_models():
    """Test discovering free models from OpenRouter."""
    import os

    from italianollama.utils.openrouter import discover_free_models

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "test/model",
                    "name": "Test Model",
                    "pricing": {"prompt": "0", "completion": "0"},
                }
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            models = await discover_free_models()

            assert len(models) == 1
            assert models[0]["id"] == "test/model"
            assert models[0]["name"] == "Test Model"


@pytest.mark.asyncio
async def test_discover_free_models_no_api_key():
    """Test that discovering models raises error without API key."""
    import os

    from italianollama.utils.openrouter import discover_free_models

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=True):
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable not set"):
            await discover_free_models()


@pytest.mark.asyncio
async def test_format_model_for_litellm():
    """Test formatting OpenRouter model for LiteLLM."""
    from italianollama.utils.openrouter import format_model_for_litellm

    model = {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "pricing": {"prompt": "0", "completion": "0"},
    }

    result = format_model_for_litellm(model)

    assert result["model_name"] == "openrouter-openai-gpt-4o-mini"
    assert result["litellm_params"]["model"] == "openrouter/openai/gpt-4o-mini"
    assert result["litellm_params"]["rpm"] == 60
    assert result["litellm_params"]["timeout"] == 120


@pytest.mark.asyncio
async def test_update_litellm_config(tmp_path):
    """Test updating LiteLLM config with new models."""
    import yaml

    from italianollama.utils.openrouter import update_litellm_config

    config_path = tmp_path / "litellm_config.yaml"
    initial_config = {
        "model_list": [
            {"model_name": "existing-model", "litellm_params": {"model": "ollama/llama3"}}
        ]
    }

    with open(config_path, "w") as f:
        yaml.dump(initial_config, f)

    new_models = [
        {
            "model_name": "new-openrouter-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]

    update_litellm_config(new_models, str(config_path))

    with open(config_path, "r") as f:
        updated_config = yaml.safe_load(f)

    assert len(updated_config["model_list"]) == 2
    assert any(m["model_name"] == "existing-model" for m in updated_config["model_list"])
    assert any(m["model_name"] == "new-openrouter-model" for m in updated_config["model_list"])


@pytest.mark.asyncio
async def test_update_litellm_config_duplicate(tmp_path):
    """Test that duplicate models are not added."""
    import yaml

    from italianollama.utils.openrouter import update_litellm_config

    config_path = tmp_path / "litellm_config.yaml"
    initial_config = {
        "model_list": [
            {"model_name": "existing-model", "litellm_params": {"model": "ollama/llama3"}}
        ]
    }

    with open(config_path, "w") as f:
        yaml.dump(initial_config, f)

    new_models = [
        {
            "model_name": "existing-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]

    update_litellm_config(new_models, str(config_path))

    with open(config_path, "r") as f:
        updated_config = yaml.safe_load(f)

    assert len(updated_config["model_list"]) == 1


@pytest.mark.asyncio
async def test_add_free_models_to_config(tmp_path):
    """Test adding free models to config."""
    import os
    import yaml

    from italianollama.utils.openrouter import add_free_models_to_config

    config_path = tmp_path / "litellm_config.yaml"
    initial_config = {
        "model_list": [
            {"model_name": "existing-model", "litellm_params": {"model": "ollama/llama3"}}
        ]
    }

    with open(config_path, "w") as f:
        yaml.dump(initial_config, f)

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "pricing": {"prompt": "0", "completion": "0"},
                }
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()

        with patch("httpx.AsyncClient", return_value=mock_client):
            added = await add_free_models_to_config(str(config_path))

            assert len(added) == 1
            assert added[0] == "openrouter-openai-gpt-4o-mini"

            with open(config_path, "r") as f:
                updated_config = yaml.safe_load(f)

            assert len(updated_config["model_list"]) == 2
