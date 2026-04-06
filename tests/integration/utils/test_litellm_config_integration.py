"""Integration tests for LiteLLM config generation and validation."""

import os
import tempfile
from unittest.mock import patch

import pytest
import yaml

from italianollama.utils.openrouter import format_model_for_litellm, update_litellm_config


@pytest.fixture
def temp_config_path():
    """Create temporary config file path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("model_list: []\n")
        return f.name


@pytest.fixture
def sample_model():
    """Sample OpenRouter model for testing."""
    return {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "pricing": {"prompt": "0", "completion": "0"},
    }


@pytest.mark.asyncio
async def test_format_model_for_litellm_os_environ_prefix(sample_model):
    """Test that format_model_for_litellm uses os.environ/ prefix for API key."""
    result = format_model_for_litellm(sample_model)
    
    assert result["litellm_params"]["api_key"] == "os.environ/OPENROUTER_API_KEY"


@pytest.mark.asyncio
async def test_format_model_for_litellm_rpm_tpm_set(sample_model):
    """Test that rpm and tpm values are set in formatted model."""
    result = format_model_for_litellm(sample_model)
    
    assert "rpm" in result["litellm_params"]
    assert "tpm" in result["litellm_params"]
    assert result["litellm_params"]["rpm"] == 60
    assert result["litellm_params"]["tpm"] == 100000


@pytest.mark.asyncio
async def test_format_model_for_litellm_model_info(sample_model):
    """Test that model_info section is present."""
    result = format_model_for_litellm(sample_model)
    
    assert "model_info" in result
    assert "id" in result["model_info"]
    assert "provider" in result["model_info"]
    assert result["model_info"]["id"] == "openai/gpt-4o-mini"
    assert result["model_info"]["provider"] == "openai"


@pytest.mark.asyncio
async def test_format_model_for_litellm_model_name_formatting(sample_model):
    """Test model name formatting."""
    result = format_model_for_litellm(sample_model)
    
    assert result["model_name"] == "openrouter-openai-gpt-4o-mini"


@pytest.mark.asyncio
async def test_format_model_for_litellm_litellm_params_model(sample_model):
    """Test litellm_params.model path formatting."""
    result = format_model_for_litellm(sample_model)
    
    assert result["litellm_params"]["model"] == "openrouter/openai/gpt-4o-mini"


@pytest.mark.asyncio
async def test_format_model_for_litellm_timeout(sample_model):
    """Test timeout is set correctly."""
    result = format_model_for_litellm(sample_model)
    
    assert result["litellm_params"]["timeout"] == 120


@pytest.mark.asyncio
async def test_update_litellm_config_syntax(temp_config_path):
    """Test that updated config file has valid YAML syntax."""
    models = [
        {
            "model_name": "test-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    update_litellm_config(models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        content = f.read()
    
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML syntax: {e}")


@pytest.mark.asyncio
async def test_update_litellm_config_preserves_existing(temp_config_path):
    """Test that existing models are preserved."""
    initial_models = [
        {
            "model_name": "existing-model",
            "litellm_params": {"model": "ollama/llama3"},
            "rpm": 30,
        }
    ]
    
    with open(temp_config_path, "w") as f:
        yaml.dump({"model_list": initial_models}, f)
    
    new_models = [
        {
            "model_name": "new-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    update_litellm_config(new_models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 2
    
    existing = next((m for m in config["model_list"] if m["model_name"] == "existing-model"), None)
    assert existing is not None
    assert existing["rpm"] == 30


@pytest.mark.asyncio
async def test_update_litellm_config_no_duplicates(temp_config_path):
    """Test that duplicate models are not added."""
    initial_models = [
        {
            "model_name": "test-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    with open(temp_config_path, "w") as f:
        yaml.dump({"model_list": initial_models}, f)
    
    new_models = [
        {
            "model_name": "test-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    update_litellm_config(new_models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 1


@pytest.mark.asyncio
async def test_update_litellm_config_multiple_models(temp_config_path):
    """Test adding multiple models at once."""
    initial_models = [
        {
            "model_name": "existing-model",
            "litellm_params": {"model": "ollama/llama3"},
        }
    ]
    
    with open(temp_config_path, "w") as f:
        yaml.dump({"model_list": initial_models}, f)
    
    new_models = [
        {
            "model_name": "model-1",
            "litellm_params": {"model": "openrouter/model/1"},
        },
        {
            "model_name": "model-2",
            "litellm_params": {"model": "openrouter/model/2"},
        },
        {
            "model_name": "model-3",
            "litellm_params": {"model": "openrouter/model/3"},
        },
    ]
    
    update_litellm_config(new_models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 4
    
    model_names = [m["model_name"] for m in config["model_list"]]
    assert "model-1" in model_names
    assert "model-2" in model_names
    assert "model-3" in model_names


@pytest.mark.asyncio
async def test_update_litellm_config_mixed_existing_new(temp_config_path):
    """Test adding mix of existing and new models."""
    initial_models = [
        {
            "model_name": "existing-1",
            "litellm_params": {"model": "openrouter/existing/1"},
        }
    ]
    
    with open(temp_config_path, "w") as f:
        yaml.dump({"model_list": initial_models}, f)
    
    new_models = [
        {
            "model_name": "existing-1",
            "litellm_params": {"model": "openrouter/existing/1"},
        },
        {
            "model_name": "new-1",
            "litellm_params": {"model": "openrouter/new/1"},
        },
        {
            "model_name": "new-2",
            "litellm_params": {"model": "openrouter/new/2"},
        },
    ]
    
    update_litellm_config(new_models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 3
    assert config["model_list"][0]["model_name"] == "existing-1"
    
    new_model_names = [m["model_name"] for m in config["model_list"][1:]]
    assert "new-1" in new_model_names
    assert "new-2" in new_model_names


@pytest.mark.asyncio
async def test_update_litellm_config_empty_list(temp_config_path):
    """Test updating with empty model list."""
    initial_models = [
        {
            "model_name": "existing-model",
            "litellm_params": {"model": "ollama/llama3"},
        }
    ]
    
    with open(temp_config_path, "w") as f:
        yaml.dump({"model_list": initial_models}, f)
    
    update_litellm_config([], temp_config_path)
    
    with open(temp_config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 1
    assert config["model_list"][0]["model_name"] == "existing-model"


@pytest.mark.asyncio
async def test_update_litellm_config_yml_extension(temp_config_path):
    """Test config file with .yml extension."""
    yml_path = temp_config_path.replace(".yaml", ".yml")
    os.rename(temp_config_path, yml_path)
    
    models = [
        {
            "model_name": "test-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    update_litellm_config(models, yml_path)
    
    with open(yml_path, "r") as f:
        content = f.read()
    
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML syntax: {e}")


@pytest.mark.asyncio
async def test_format_model_for_litellm_provider_extraction():
    """Test that provider is correctly extracted from model ID."""
    models = [
        {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "pricing": {"prompt": "0", "completion": "0"}},
        {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "pricing": {"prompt": "0", "completion": "0"}},
        {"id": "google/gemini-flash-1.5", "name": "Gemini Flash 1.5", "pricing": {"prompt": "0", "completion": "0"}},
        {"id": "mistralai/mistral-7b-instruct", "name": "Mistral 7B", "pricing": {"prompt": "0", "completion": "0"}},
        {"id": "meta-llama/llama-3-8b-instruct", "name": "Llama 3 8B", "pricing": {"prompt": "0", "completion": "0"}},
    ]
    
    for model in models:
        result = format_model_for_litellm(model)
        
        expected_provider = model["id"].split("/")[0]
        assert result["model_info"]["provider"] == expected_provider, f"Failed for {model['id']}"


@pytest.mark.asyncio
async def test_format_model_for_litellm_comprehensive_validation(sample_model):
    """Test comprehensive model formatting structure."""
    result = format_model_for_litellm(sample_model)
    
    assert result["model_name"].startswith("openrouter-")
    assert result["model_name"].count("-") >= 2
    
    assert result["litellm_params"]["model"].startswith("openrouter/")
    assert result["litellm_params"]["model"].count("/") == 2
    
    assert result["litellm_params"]["api_key"] == "os.environ/OPENROUTER_API_KEY"
    assert result["litellm_params"]["rpm"] == 60
    assert result["litellm_params"]["tpm"] == 100000
    assert result["litellm_params"]["timeout"] == 120
    
    assert "model_info" in result
    assert "id" in result["model_info"]
    assert "provider" in result["model_info"]


@pytest.mark.asyncio
async def test_update_litellm_config_yaml_structure_validation(temp_config_path):
    """Test that config maintains valid YAML structure after multiple updates."""
    initial_config = {
        "model_list": [],
        "general_settings": {
            "master_key": "sk-123456",
            "debug": False,
        },
        "litellm_settings": {
            "num_retries": 3,
        }
    }
    
    with open(temp_config_path, "w") as f:
        yaml.dump(initial_config, f)
    
    models = [
        {
            "model_name": "model-1",
            "litellm_params": {"model": "openrouter/test/1"},
        },
        {
            "model_name": "model-2",
            "litellm_params": {"model": "openrouter/test/2"},
        },
    ]
    
    update_litellm_config(models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        content = f.read()
        config = yaml.safe_load(content)
    
    assert config["general_settings"]["master_key"] == "sk-123456"
    assert config["general_settings"]["debug"] is False
    assert config["litellm_settings"]["num_retries"] == 3
    assert len(config["model_list"]) == 2


@pytest.mark.asyncio
async def test_update_litellm_config_special_characters_in_id(temp_config_path):
    """Test handling model IDs with special characters."""
    models = [
        {
            "model_name": "test-model",
            "litellm_params": {"model": "openrouter/test/model-with-dash"},
        }
    ]
    
    update_litellm_config(models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert config["model_list"][0]["model_name"] == "test-model"


@pytest.mark.asyncio
async def test_update_litellm_config_large_model_list(temp_config_path):
    """Test adding a large number of models."""
    initial_models = [{"model_name": f"model-{i}", "litellm_params": {"model": f"ollama/model-{i}"}} for i in range(5)]
    
    with open(temp_config_path, "w") as f:
        yaml.dump({"model_list": initial_models}, f)
    
    new_models = [
        {
            "model_name": f"openrouter-model-{i}",
            "litellm_params": {"model": f"openrouter/test/model-{i}"},
        }
        for i in range(10)
    ]
    
    update_litellm_config(new_models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 15


@pytest.mark.asyncio
async def test_update_litellm_config_yaml_roundtrip(temp_config_path):
    """Test that config can be written and read multiple times without corruption."""
    models = [
        {
            "model_name": "test-model",
            "litellm_params": {
                "model": "openrouter/test/model",
                "rpm": 60,
                "tpm": 100000,
            },
        }
    ]
    
    update_litellm_config(models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        content1 = f.read()
        config1 = yaml.safe_load(content1)
    
    update_litellm_config(models, temp_config_path)
    
    with open(temp_config_path, "r") as f:
        content2 = f.read()
        config2 = yaml.safe_load(content2)
    
    assert len(config1["model_list"]) == len(config2["model_list"])
    assert config1["model_list"][0]["model_name"] == config2["model_list"][0]["model_name"]


@pytest.mark.asyncio
async def test_format_model_for_litellm_empty_name(sample_model):
    """Test formatting when model name is empty."""
    sample_model["name"] = ""
    result = format_model_for_litellm(sample_model)
    
    assert result["model_name"] == "openrouter-openai-gpt-4o-mini"
    expected_model_name = f"openrouter-{sample_model['id'].replace('/', '-')}"
    assert result["model_name"] == expected_model_name


@pytest.mark.asyncio
async def test_format_model_for_litellm_all_fields_present(sample_model):
    """Test that all required fields are present in formatted model."""
    result = format_model_for_litellm(sample_model)
    
    assert "model_name" in result
    assert "litellm_params" in result
    assert "model_info" in result
    
    assert "model" in result["litellm_params"]
    assert "api_key" in result["litellm_params"]
    assert "rpm" in result["litellm_params"]
    assert "tpm" in result["litellm_params"]
    assert "timeout" in result["litellm_params"]
    
    assert "id" in result["model_info"]
    assert "provider" in result["model_info"]


@pytest.mark.asyncio
async def test_update_litellm_config_multiple_yaml_files(tmp_path):
    """Test updating multiple YAML config files."""
    config_files = []
    for i in range(3):
        config_path = tmp_path / f"config_{i}.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"model_list": []}, f)
        config_files.append(config_path)
    
    models = [
        {
            "model_name": "openrouter-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    for config_path in config_files:
        update_litellm_config(models, str(config_path))
    
    for config_path in config_files:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        assert len(config["model_list"]) == 1
        assert config["model_list"][0]["model_name"] == "openrouter-model"


@pytest.mark.asyncio
async def test_format_model_for_litellm_timeout_value():
    """Test that timeout is set to 120 seconds."""
    model = {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "pricing": {"prompt": "0", "completion": "0"},
    }
    
    result = format_model_for_litellm(model)
    
    assert result["litellm_params"]["timeout"] == 120


@pytest.mark.asyncio
async def test_format_model_for_litellm_special_characters():
    """Test formatting models with special characters in name."""
    model = {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini (2024)",
        "pricing": {"prompt": "0", "completion": "0"},
    }
    
    result = format_model_for_litellm(model)
    
    assert result["model_name"] == "openrouter-openai-gpt-4o-mini"
    assert "2024" not in result["model_name"]


@pytest.mark.asyncio
async def test_update_litellm_config_preserves_metadata(tmp_path):
    """Test that metadata fields are preserved during update."""
    initial_config = {
        "model_list": [
            {
                "model_name": "ollama-llama3",
                "litellm_params": {
                    "model": "ollama/llama3",
                    "api_key": "dummy",
                    "rpm": 30,
                    "tpm": 50000,
                    "timeout": 60,
                },
                "model_info": {
                    "id": "ollama/llama3",
                    "provider": "ollama",
                },
            }
        ],
        "general_settings": {
            "master_key": "sk-123456",
            "debug": False,
        },
        "litellm_settings": {
            "num_retries": 3,
            "success_callbacks": ["prometheus"],
        }
    }
    
    config_path = tmp_path / "litellm_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(initial_config, f)
    
    new_models = [
        {
            "model_name": "openrouter-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    update_litellm_config(new_models, str(config_path))
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert config["general_settings"]["master_key"] == "sk-123456"
    assert config["general_settings"]["debug"] is False
    assert config["litellm_settings"]["num_retries"] == 3
    assert config["litellm_settings"]["success_callbacks"] == ["prometheus"]


@pytest.mark.asyncio
async def test_format_model_for_litellm_custom_provider():
    """Test provider extraction for custom provider patterns."""
    model = {
        "id": "custom-provider/custom-model",
        "name": "Custom Model",
        "pricing": {"prompt": "0", "completion": "0"},
    }
    
    result = format_model_for_litellm(model)
    
    assert result["model_info"]["provider"] == "custom-provider"


@pytest.mark.asyncio
async def test_update_litellm_config_yaml_structure_stable(tmp_path):
    """Test that config maintains stable YAML structure after update."""
    config_content = """model_list: []
"""
    
    config_path = tmp_path / "litellm_config.yaml"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    models = [
        {
            "model_name": "openrouter-model",
            "litellm_params": {"model": "openrouter/test/model"},
        }
    ]
    
    update_litellm_config(models, str(config_path))
    
    with open(config_path, "r") as f:
        content = f.read()
        config = yaml.safe_load(content)
    
    assert "model_list" in config
    assert len(config["model_list"]) == 1
