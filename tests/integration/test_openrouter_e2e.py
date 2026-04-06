"""End-to-end integration tests for OpenRouter model discovery and configuration."""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
import yaml

from italianollama.utils.openrouter import (
    discover_free_models,
    add_free_models_to_config,
    format_model_for_litellm,
    update_litellm_config,
)


@pytest.mark.asyncio
async def test_e2e_discover_format_update_flow():
    """Test complete flow: discover → format → update config."""
    import os as os_module
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
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
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            free_models = await discover_free_models()
            
            assert len(free_models) == 2
            assert free_models[0]["id"] == "openai/gpt-4o-mini"
            assert free_models[1]["id"] == "anthropic/claude-3-haiku"
            
            formatted_models = [format_model_for_litellm(m) for m in free_models]
            
            assert len(formatted_models) == 2
            assert all("model_info" in m for m in formatted_models)
            assert all("rpm" in m["litellm_params"] for m in formatted_models)
            assert all("tpm" in m["litellm_params"] for m in formatted_models)
            
            assert any(m["model_name"] == "openrouter-openai-gpt-4o-mini" for m in formatted_models)
            assert any(m["model_name"] == "openrouter-anthropic-claude-3-haiku" for m in formatted_models)


@pytest.mark.asyncio
async def test_e2e_full_workflow(tmp_path):
    """Test full end-to-end workflow with config file."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    initial_config = {
        "model_list": [
            {
                "model_name": "ollama-llama3",
                "litellm_params": {
                    "model": "ollama/llama3",
                    "api_key": "dummy-key",
                },
            }
        ],
        "general_settings": {"master_key": "sk-123456"},
    }
    
    with open(config_path, "w") as f:
        yaml.dump(initial_config, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
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
    
    ollama_model = next((m for m in updated_config["model_list"] if m["model_name"] == "ollama-llama3"), None)
    assert ollama_model is not None
    assert ollama_model["litellm_params"]["api_key"] == "dummy-key"
    
    openrouter_model = next((m for m in updated_config["model_list"] if m["model_name"] == "openrouter-openai-gpt-4o-mini"), None)
    assert openrouter_model is not None
    assert openrouter_model["litellm_params"]["api_key"] == "os.environ/OPENROUTER_API_KEY"
    assert openrouter_model["model_info"]["provider"] == "openai"


@pytest.mark.asyncio
async def test_e2e_yaml_validation(tmp_path):
    """Test that config file is properly formatted YAML."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    initial_config = {"model_list": []}
    
    with open(config_path, "w") as f:
        yaml.dump(initial_config, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
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
            await add_free_models_to_config(str(config_path))
    
    with open(config_path, "r") as f:
        content = f.read()
    
    try:
        parsed = yaml.safe_load(content)
        assert parsed is not None
        assert "model_list" in parsed
        assert isinstance(parsed["model_list"], list)
    except yaml.YAMLError as e:
        pytest.fail(f"Config file has invalid YAML syntax: {e}")


@pytest.mark.asyncio
async def test_e2e_cli_command_integration(tmp_path):
    """Test CLI command integration simulation."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
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
            assert added[0].startswith("openrouter-")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 1
    assert "openrouter" in config["model_list"][0]["model_name"]


@pytest.mark.asyncio
async def test_e2e_multiple_models_discovery(tmp_path):
    """Test discovery of multiple free models."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
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
                {
                    "id": "google/gemini-flash-1.5",
                    "name": "Gemini Flash 1.5",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "mistralai/mistral-7b-instruct",
                    "name": "Mistral 7B Instruct",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
                {
                    "id": "meta-llama/llama-3-8b-instruct",
                    "name": "Llama 3 8B Instruct",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            added = await add_free_models_to_config(str(config_path))
            
            assert len(added) == 5
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 5
    
    model_names = {m["model_name"] for m in config["model_list"]}
    assert "openrouter-openai-gpt-4o-mini" in model_names
    assert "openrouter-anthropic-claude-3-haiku" in model_names
    assert "openrouter-google-gemini-flash-1.5" in model_names
    assert "openrouter-mistralai-mistral-7b-instruct" in model_names
    assert "openrouter-meta-llama-llama-3-8b-instruct" in model_names


@pytest.mark.asyncio
async def test_e2e_duplicate_prevention(tmp_path):
    """Test that running workflow twice doesn't create duplicates."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
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
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            added_first = await add_free_models_to_config(str(config_path))
            added_second = await add_free_models_to_config(str(config_path))
            
            assert len(added_first) == 1
            assert len(added_second) == 1
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 1


@pytest.mark.asyncio
async def test_e2e_model_info_validation(tmp_path):
    """Test that model_info section is correctly populated."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
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
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            await add_free_models_to_config(str(config_path))
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    for model in config["model_list"]:
        assert "model_info" in model
        assert "provider" in model["model_info"]
        assert model["model_info"]["provider"] in ["openai", "anthropic"]


@pytest.mark.asyncio
async def test_e2e_rpm_tpm_validation(tmp_path):
    """Test that rpm and tpm are correctly set in all models."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
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
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            await add_free_models_to_config(str(config_path))
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    for model in config["model_list"]:
        assert "rpm" in model["litellm_params"]
        assert "tpm" in model["litellm_params"]
        assert model["litellm_params"]["rpm"] == 60
        assert model["litellm_params"]["tpm"] == 100000


@pytest.mark.asyncio
async def test_e2e_all_free_models_discovery_28_models(tmp_path):
    """Test discovery of all 28 known free models from OpenRouter."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    mock_models_data = {
        "data": [
            {
                "id": "openai/gpt-4o-mini",
                "name": "GPT-4o Mini",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "openai/gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "openai/gpt-4",
                "name": "GPT-4",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "anthropic/claude-3-haiku",
                "name": "Claude 3 Haiku",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "anthropic/claude-3-opus",
                "name": "Claude 3 Opus",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "anthropic/claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "google/gemini-flash-1.5",
                "name": "Gemini Flash 1.5",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "google/gemini-pro",
                "name": "Gemini Pro",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "google/gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "mistralai/mistral-7b-instruct",
                "name": "Mistral 7B Instruct",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "mistralai/mistral-8x7b-instruct",
                "name": "Mistral 8x7B Instruct",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "mistralai/mixtral-8x7b-instruct",
                "name": "Mixtral 8x7B Instruct",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "meta-llama/llama-3-8b-instruct",
                "name": "Llama 3 8B Instruct",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "meta-llama/llama-3-70b-instruct",
                "name": "Llama 3 70B Instruct",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "meta-llama/llama-2-70b-chat",
                "name": "Llama 2 70B Chat",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "codellama/codellama-34b-instruct",
                "name": "CodeLlama 34B Instruct",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "teknium/openhermes-2.5-mistral",
                "name": "OpenHermes 2.5 Mistral",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",
                "name": "Nous Hermes 2 Mistral",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "nvidia/Llama3-ChatQA-1.5-8B",
                "name": "Llama3 ChatQA 1.5 8B",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "openchat/openchat-3.5",
                "name": "OpenChat 3.5",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "phind/phind-codellama-34b",
                "name": "Phind CodeLlama 34B",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "xwinai/xwin-lm-70b-chat",
                "name": "Xwin LM 70B Chat",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "Gryphe/MythoMax-L2-13b",
                "name": "MythoMax-L2 13B",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "Gryphe/MythoMax-L2-70b",
                "name": "MythoMax-L2 70B",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "togethercomputer/StripedHyena-Hessian-70B",
                "name": "StripedHyena Hessian 70B",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "Qwen/Qwen1.5-0.5B-Chat",
                "name": "Qwen 1.5 0.5B Chat",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "Qwen/Qwen1.5-7B-Chat",
                "name": "Qwen 1.5 7B Chat",
                "pricing": {"prompt": "0", "completion": "0"},
            },
            {
                "id": "Qwen/Qwen1.5-14B-Chat",
                "name": "Qwen 1.5 14B Chat",
                "pricing": {"prompt": "0", "completion": "0"},
            },
        ]
    }
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = mock_models_data
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            added = await add_free_models_to_config(str(config_path))
            
            assert len(added) == 28
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 28
    
    model_names = {m["model_name"] for m in config["model_list"]}
    expected_names = {
        "openrouter-openai-gpt-4o-mini",
        "openrouter-openai-gpt-3.5-turbo",
        "openrouter-openai-gpt-4",
        "openrouter-anthropic-claude-3-haiku",
        "openrouter-anthropic-claude-3-opus",
        "openrouter-anthropic-claude-3-sonnet",
        "openrouter-google-gemini-flash-1.5",
        "openrouter-google-gemini-pro",
        "openrouter-google-gemini-1.5-pro",
        "openrouter-mistralai-mistral-7b-instruct",
        "openrouter-mistralai-mistral-8x7b-instruct",
        "openrouter-mistralai-mixtral-8x7b-instruct",
        "openrouter-meta-llama-llama-3-8b-instruct",
        "openrouter-meta-llama-llama-3-70b-instruct",
        "openrouter-meta-llama-llama-2-70b-chat",
        "openrouter-codellama-codellama-34b-instruct",
        "openrouter-teknium-openhermes-2.5-mistral",
        "openrouter-NousResearch-Nous-Hermes-2-Mistral-7B-DPO",
        "openrouter-nvidia-Llama3-ChatQA-1.5-8B",
        "openrouter-openchat-openchat-3.5",
        "openrouter-phind-phind-codellama-34b",
        "openrouter-xwinai-xwin-lm-70b-chat",
        "openrouter-Gryphe-MythoMax-L2-13b",
        "openrouter-Gryphe-MythoMax-L2-70b",
        "openrouter-togethercomputer-StripedHyena-Hessian-70B",
        "openrouter-Qwen-Qwen1.5-0.5B-Chat",
        "openrouter-Qwen-Qwen1.5-7B-Chat",
        "openrouter-Qwen-Qwen1.5-14B-Chat",
    }
    assert model_names == expected_names


@pytest.mark.asyncio
async def test_e2e_model_validation_structure(tmp_path):
    """Test comprehensive validation of model structure in config."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "pricing": {"prompt": "0", "completion": "0"},
                },
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            await add_free_models_to_config(str(config_path))
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    model = config["model_list"][0]
    
    assert "model_name" in model
    assert "litellm_params" in model
    assert "model_info" in model
    
    assert model["model_name"].startswith("openrouter-")
    
    litellm_params = model["litellm_params"]
    assert "model" in litellm_params
    assert "api_key" in litellm_params
    assert "rpm" in litellm_params
    assert "tpm" in litellm_params
    assert "timeout" in litellm_params
    
    assert litellm_params["model"].startswith("openrouter/")
    assert litellm_params["api_key"] == "os.environ/OPENROUTER_API_KEY"
    assert litellm_params["rpm"] == 60
    assert litellm_params["tpm"] == 100000
    assert litellm_params["timeout"] == 120
    
    assert "id" in model["model_info"]
    assert "provider" in model["model_info"]


@pytest.mark.asyncio
async def test_e2e_config_file_extension_validation(tmp_path):
    """Test that config file works with both .yaml and .yml extensions."""
    import os as os_module
    
    for extension in [".yaml", ".yml"]:
        config_path = tmp_path / f"config{extension}"
        
        with open(config_path, "w") as f:
            yaml.dump({"model_list": []}, f)
        
        with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": [
                    {
                        "id": "openai/gpt-4o-mini",
                        "name": "GPT-4o Mini",
                        "pricing": {"prompt": "0", "completion": "0"},
                    },
                ]
            }
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.aclose = AsyncMock()
            
            with patch("httpx.AsyncClient", return_value=mock_client):
                await add_free_models_to_config(str(config_path))
        
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        assert len(config["model_list"]) == 1
        assert "openrouter" in config["model_list"][0]["model_name"]


@pytest.mark.asyncio
async def test_e2e_full_workflow_with_real_yaml_syntax(tmp_path):
    """Test full workflow with proper YAML syntax validation."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    initial_config = {
        "model_list": [
            {
                "model_name": "ollama-llama3",
                "litellm_params": {
                    "model": "ollama/llama3",
                    "api_key": "dummy-key",
                    "rpm": 30,
                    "tpm": 50000,
                    "timeout": 60,
                },
            }
        ],
        "general_settings": {
            "master_key": "sk-123456",
            "debug": False,
            "num_retries": 3,
        },
        "litellm_settings": {
            "default_policy": "default",
            "callbacks": ["prometheus"],
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(initial_config, f, default_flow_style=False, sort_keys=False)
    
    with open(config_path, "r") as f:
        initial_content = f.read()
    
    try:
        yaml.safe_load(initial_content)
    except yaml.YAMLError as e:
        pytest.fail(f"Initial config has invalid YAML: {e}")
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
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
    
    with open(config_path, "r") as f:
        content = f.read()
    
    try:
        config = yaml.safe_load(content)
    except yaml.YAMLError as e:
        pytest.fail(f"Updated config has invalid YAML syntax: {e}")
    
    assert "model_list" in config
    assert "general_settings" in config
    assert "litellm_settings" in config
    assert config["general_settings"]["master_key"] == "sk-123456"
    assert len(config["model_list"]) == 2
    
    ollama_model = next((m for m in config["model_list"] if "ollama" in m["model_name"]), None)
    assert ollama_model is not None
    assert ollama_model["litellm_params"]["api_key"] == "dummy-key"
    
    openrouter_model = next((m for m in config["model_list"] if "openrouter" in m["model_name"]), None)
    assert openrouter_model is not None
    assert openrouter_model["litellm_params"]["api_key"] == "os.environ/OPENROUTER_API_KEY"


@pytest.mark.asyncio
async def test_e2e_large_scale_model_discovery(tmp_path):
    """Test discovery and configuration of 50+ models."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    mock_models = []
    for i in range(50):
        mock_models.append({
            "id": f"provider{i%5}/model-{i}",
            "name": f"Model {i}",
            "pricing": {"prompt": "0", "completion": "0"},
        })
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {"data": mock_models}
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            added = await add_free_models_to_config(str(config_path))
            
            assert len(added) == 50
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 50


@pytest.mark.asyncio
async def test_e2e_sequential_config_updates(tmp_path):
    """Test that sequential config updates work correctly."""
    import os as os_module
    import asyncio
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    async def add_models_for_provider(provider, count):
        with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
            mock_models = []
            for i in range(count):
                mock_models.append({
                    "id": f"{provider}/model-{i}",
                    "name": f"{provider} Model {i}",
                    "pricing": {"prompt": "0", "completion": "0"},
                })
            
            mock_response = Mock()
            mock_response.json.return_value = {"data": mock_models}
            mock_response.raise_for_status = Mock()
            
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.aclose = AsyncMock()
            
            with patch("httpx.AsyncClient", return_value=mock_client):
                return await add_free_models_to_config(str(config_path))
    
    results = await asyncio.gather(
        add_models_for_provider("openai", 10),
        add_models_for_provider("anthropic", 10),
        add_models_for_provider("google", 10),
    )
    
    all_added = results[0] + results[1] + results[2]
    assert len(all_added) == 30
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    assert len(config["model_list"]) == 30


@pytest.mark.asyncio
async def test_e2e_api_key_security_in_config(tmp_path):
    """Test that API key is never stored in config file."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "sk-real-secret-key-12345"}):
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
            await add_free_models_to_config(str(config_path))
    
    with open(config_path, "r") as f:
        content = f.read()
    
    assert "sk-real-secret-key-12345" not in content
    assert "os.environ/OPENROUTER_API_KEY" in content


@pytest.mark.asyncio
async def test_e2e_format_model_name_variations():
    """Test model name formatting with various ID formats."""
    test_cases = [
        ("openai/gpt-4o-mini", "openrouter-openai-gpt-4o-mini"),
        ("anthropic/claude-3-haiku", "openrouter-anthropic-claude-3-haiku"),
        ("google/gemini-flash-1.5", "openrouter-google-gemini-flash-1.5"),
        ("meta-llama/llama-3-8b-instruct", "openrouter-meta-llama-llama-3-8b-instruct"),
        ("Qwen/Qwen1.5-7B-Chat", "openrouter-Qwen-Qwen1.5-7B-Chat"),
    ]
    
    for model_id, expected_name in test_cases:
        model = {
            "id": model_id,
            "name": f"Model {model_id}",
            "pricing": {"prompt": "0", "completion": "0"},
        }
        result = format_model_for_litellm(model)
        assert result["model_name"] == expected_name, f"Failed for {model_id}"


@pytest.mark.asyncio
async def test_e2e_rpm_tpm_validation_full(tmp_path):
    """Test that rpm and tpm are correctly set for all provider models."""
    import os as os_module
    
    config_path = tmp_path / "litellm_config.yaml"
    
    with open(config_path, "w") as f:
        yaml.dump({"model_list": []}, f)
    
    with patch.dict(os_module.environ, {"OPENROUTER_API_KEY": "test-key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "pricing": {"prompt": "0", "completion": "0"}},
                {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "pricing": {"prompt": "0", "completion": "0"}},
                {"id": "google/gemini-flash-1.5", "name": "Gemini Flash 1.5", "pricing": {"prompt": "0", "completion": "0"}},
                {"id": "mistralai/mistral-7b-instruct", "name": "Mistral 7B", "pricing": {"prompt": "0", "completion": "0"}},
                {"id": "meta-llama/llama-3-8b-instruct", "name": "Llama 3 8B", "pricing": {"prompt": "0", "completion": "0"}},
            ]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.aclose = AsyncMock()
        
        with patch("httpx.AsyncClient", return_value=mock_client):
            await add_free_models_to_config(str(config_path))
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    for model in config["model_list"]:
        assert model["litellm_params"]["rpm"] == 60, f"rpm mismatch for {model['model_name']}"
        assert model["litellm_params"]["tpm"] == 100000, f"tpm mismatch for {model['model_name']}"
        assert model["litellm_params"]["timeout"] == 120, f"timeout mismatch for {model['model_name']}"
        assert model["litellm_params"]["api_key"] == "os.environ/OPENROUTER_API_KEY"
