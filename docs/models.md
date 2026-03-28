# Model Management

Guide to using and managing LLM models with hellmholtz.

## Available Blablador Models

ItalianOllama uses the Helmholtz Blablador service as the primary LLM provider. Here's the current model list:

### Alias Models (Recommended)

| Model | Aliases | Tokens | Description |
|-------|---------|--------|-------------|
| alias-fast | fast | 32k | Fastest available model |
| alias-large | large | 128k | Most capable model |
| alias-huge | huge | 128k | Maximum capability |
| alias-code | code | 128k | Optimized for coding |
| alias-apertus | apertus | 32k | Apertus models |
| alias-embeddings | embeddings | 8k | Text embeddings |

### Base Models

| Model | Tokens | Description |
|-------|--------|-------------|
| MiniMax-M2.5 | 128k | Best model as of Feb 2026 |
| GPT-OSS-120b | 128k | OpenAI open model (Aug 2025) |
| Qwen3.5-35B-A3B | 128k | Multimodal model (Feb 2026) |
| Qwen3.5-122B-A10B-FP8 | 128k | General purpose large model |
| Qwen3-Coder-Next-FP8 | 128k | Code model (Feb 2026) |
| Apertus-8B-Instruct-2509 | 32k | Swiss model (Sep 2025) |

### Legacy Models

| Model | Tokens | Description |
|-------|--------|-------------|
| gpt-3.5-turbo | 16k | Legacy GPT-3.5 |
| text-davinci-003 | 4k | Legacy text model |
| text-embedding-ada-002 | 8k | Legacy embeddings |

## Using Models

### CLI

```bash
# List available models
poetry run hellm models

# Check specific model
poetry run hellm monitor --test-accessibility
```

### API

```bash
# Use specific model
curl -X POST http://localhost:8000/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "model": "alias-large"}'
```

### Python

```python
from italianollama.llm.client import LLMClient

# Use different model
client = LLMClient(provider="helmholtz", model="alias-large")
response = await client.generate("Ciao, come stai?")
```

## Model Selection Guide

### By Use Case

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| Quick questions | alias-fast | Speed |
| Complex explanations | alias-large | Capability |
| Long conversations | alias-large | Context |
| Code generation | alias-code | Specialized |
| Vocabulary teaching | alias-large | Better explanations |

### By Token Budget

| Available Budget | Model | Max Context |
|------------------|-------|-------------|
| < 4k tokens | alias-fast | 32k |
| 4k-16k tokens | gpt-3.5-turbo | 16k |
| > 16k tokens | alias-large | 128k |

## Checking Model Status

### CLI Commands

```bash
# List all configured models
poetry run hellm models

# Test model accessibility
poetry run hellm monitor --test-accessibility

# Check configuration
poetry run hellm monitor --check-config

# Update YAML status
poetry run hellm monitor --update-yaml
```

### Programmatic

```python
from italianollama.utils.models import get_model_manager

manager = get_model_manager()

# Get available models from API
available = manager.get_available_models()

# Test specific model
accessible, latency = manager.check_model_accessibility("alias-large")

# Get status from YAML
status = manager.get_model_status()
```

## Token Limits

### Why Token Limits Matter

- **Context window**: Max tokens the model can process at once
- **Input + Output**: Combined limit for prompt + response
- **Memory**: Larger context = more GPU memory needed

### Current Token Limits

The token limits are stored in `hellmholtz.providers.blablador_config.py`. Current limits:

- Alias models: 8k - 128k depending on routing
- Base models: 32k - 128k
- Legacy models: 4k - 16k

To update, edit the `max_context_tokens` field in the model definitions.

## Troubleshooting

### Model Not Found

```bash
# Check if model is available
poetry run hellm models | grep model_name

# Check API status
curl -H "Authorization: Bearer $BLABLADOR_API_KEY" \
  https://api.helmholtz-blablador.fz-juelich.de/v1/models
```

### Token Limit Errors

If you get context length errors:
1. Use a model with larger context
2. Reduce conversation history
3. Split long inputs

### Slow Responses

- Switch to `alias-fast` for speed
- Check network latency to Blablador
- Consider local Ollama for certain tasks

## Future Models

To add new models:

1. Update `hellmholtz/providers/blablador_config.py` with new model entries
2. Set appropriate `max_context_tokens`
3. Test accessibility with `hellm monitor`
4. Commit changes to hellmholtz repository

## Comparison with Ollama

| Feature | Blablador | Ollama |
|---------|-----------|--------|
| Performance | High | Depends on hardware |
| Availability | Always on | Local only |
| Model variety | Many models | Limited |
| Privacy | Cloud | Local only |
| Cost | Free (Helmholtz) | Hardware |

For production, Blablador is recommended. For development/testing without internet, Ollama can be used.
