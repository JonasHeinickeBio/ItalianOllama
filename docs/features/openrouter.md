# OpenRouter Integration

ItalianOllama includes built-in support for OpenRouter, allowing you to automatically discover and add free models to your LiteLLM configuration.

## Overview

OpenRouter provides access to multiple LLM providers through a unified API. ItalianOllama's OpenRouter integration:

- Discovers free models from OpenRouter
- Automatically adds them to your LiteLLM configuration
- Maintains a unified LLM interface through LiteLLM

## Prerequisites

1. **OpenRouter API Key**: Get your API key from openrouter.ai

2. **Set Environment Variable**:
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```

## Usage

### List Free Models

Discover available free models from OpenRouter:

```bash
italianollama openrouter list
```

This will show:
- Model name and ID
- Pricing information (should all be $0 for free models)

### Add Free Models to Config

Automatically add all free models to your LiteLLM configuration:

```bash
italianollama openrouter add
```

This will:
1. Fetch all free models from OpenRouter
2. Check your existing LiteLLM config
3. Add any new free models (avoiding duplicates)
4. Update `backend/litellm/litellm_config.yaml`

## How It Works

### Model Discovery

The `discover_free_models()` function:
1. Connects to OpenRouter API
2. Fetches all available models
3. Filters models where both prompt and completion pricing are $0
4. Returns list of free model information

### Configuration Update

The `add_free_models_to_config()` function:
1. Discovers free models from OpenRouter
2. Formats each model for LiteLLM compatibility
3. Updates `litellm_config.yaml` with new models
4. Avoids adding duplicate model names

### LiteLLM Format

Models are formatted as:
```yaml
- model_name: openrouter-openai-gpt-4o-mini
  litellm_params:
    model: openrouter/openai/gpt-4o-mini
    api_key: os.environ/OPENROUTER_API_KEY
    rpm: 60
    tpm: 100000
    timeout: 120
  model_info:
    id: openai/gpt-4o-mini
    provider: openai
```

**Best practices implemented:**
- `os.environ/` prefix for lazy environment variable evaluation
- `tpm` (tokens per minute) for proper load balancing with `rpm`
- `model_info` for metadata about the model

## API Reference

### Python API

```python
from italianollama.utils.openrouter import (
    OpenRouterAPI,
    discover_free_models,
    add_free_models_to_config,
    format_model_for_litellm,
)

# Discover free models
free_models = await discover_free_models()

# Add to LiteLLM config
added = await add_free_models_to_config()

# Get detailed pricing for a model
api = OpenRouterAPI()
pricing = await api.get_model_pricing("openai/gpt-3.5-turbo")
await api.close()
```

### Functions

#### `discover_free_models() -> list[dict]`

Discovers and returns free models from OpenRouter.

**Returns**: List of model information dictionaries with keys:
- `id`: Model identifier (e.g., "openai/gpt-4o-mini")
- `name`: Display name
- `pricing`: Pricing information

#### `add_free_models_to_config(config_path: str = "backend/litellm/litellm_config.yaml") -> list[str]`

Discovers free models and adds them to LiteLLM config.

**Parameters**:
- `config_path`: Path to LiteLLM configuration file (default: backend/litellm/litellm_config.yaml)

**Returns**: List of model names that were added

**Best practices**:
- Uses lazy environment variable evaluation for API keys
- Adds both `rpm` and `tpm` for proper load balancing
- Maintains model metadata in `model_info`

#### `format_model_for_litellm(model: dict) -> dict`

Formats an OpenRouter model for LiteLLM configuration.

**Parameters**:
- `model`: OpenRouter model information

**Returns**: LiteLLM-compatible model configuration dictionary

## Best Practices

### API Configuration
- Use `os.environ/` prefix for secrets in config files for lazy evaluation
- Set both `rpm` (requests per minute) and `tpm` (tokens per minute) for optimal load balancing
- Configure proper timeout values (120s recommended for OpenRouter free models)

### Model Discovery
- Free models are determined by checking `pricing.prompt == 0 AND pricing.completion == 0`
- Run `list` command regularly to see current free models
- Check OpenRouter dashboard for pricing updates

### Configuration Management
- Models are only added if not already present (no duplicates)
- Use `add_free_models_to_config()` to sync with current OpenRouter offerings
- Test LiteLLM config after updates: `litellm --config backend/litellm/litellm_config.yaml --debug`

### Performance Optimization
- Set `rpm` and `tpm` values appropriate for your usage tier
- Use `fallbacks` in LiteLLM config for automatic failover
- Consider implementing retry logic for production use

## Troubleshooting

### API Key Not Set

If you see `ValueError: OPENROUTER_API_KEY environment variable not set`:

```bash
export OPENROUTER_API_KEY="your-key-here"
```

### No Free Models Found

If no free models are returned, it means:
- OpenRouter has no currently free models
- Pricing has changed since last check
- Check the OpenRouter dashboard for available models

### Connection Error

If you see network errors:
- Check your internet connection
- Verify OpenRouter API is accessible
- Ensure your API key has the necessary permissions
