# LLM Providers

ItalianOllama supports multiple LLM providers through LiteLLM, giving you flexibility in choosing the best model for your needs.

## Supported Providers

| Provider | Type | Recommended For | Setup Difficulty |
|----------|------|-----------------|------------------|
| **Blablador** | Cloud (Helmholtz) | Production | Easy |
| **OpenRouter** | Cloud (Aggregator) | Free Models | Easy |
| **Ollama** | Local | Development | Easy |
| **OpenAI** | Cloud | Production | Easy |
| **Anthropic** | Cloud | Advanced features | Easy |

## Blablador (Recommended)

Blablador is the recommended LLM provider, provided by Helmholtz AI at Jülich.

### Features
- High-performance GPU infrastructure
- Optimized for European languages
- Free for research institutions
- Fast response times

### Configuration

```bash
# Environment variables
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_api_key
BLABLADOR_MODEL=alias-fast
```

### Getting Access

1. Request access at: https://gitlab.jsc.fz-juelich.de/se-paper匿/llm-api
2. Wait for approval (usually 24-48 hours)
3. Receive API key via email

### LiteLLM Configuration

```yaml
# backend/litellm/litellm_config.yaml
model_list:
  - model_name: tutor
    litellm_params:
      model: openai/fake
      api_base: ${BLABLADOR_API_URL}
      api_key: ${BLABLADOR_API_KEY}
```

## OpenRouter (Free Models)

OpenRouter is an aggregator that provides free access to many models through various providers. It's excellent for development and testing without costs.

### Features
- Access to 100+ models
- Many free models available
- Unified API across providers
- No setup required for some models

### Getting Access

1. Sign up at: https://openrouter.ai/
2. Get your API key from the dashboard
3. Some models are free, some require credits

### Free Models Available

| Model | Provider | Context | Notes |
|-------|----------|---------|-------|
| **step-3.5-flash** | StepFun | 32K | Recommended - Fast & capable |
| **qwen-2.5-7b-instruct** | Qwen | 32K | Great for Italian |
| **llama-3.1-8b-instruct** | Meta | 128K | High quality |
| **mistral-nemo-2407** | Mistral | 128K | Good reasoning |
| **gemma-2-9b-it** | Google | 8K | Efficient |

### Configuration

```bash
# Environment variables
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=stepfun/step-3.5-flash:free
```

### LiteLLM Configuration

```yaml
# backend/litellm/litellm_config.yaml
model_list:
  - model_name: tutor
    litellm_params:
      model: openai/step-3.5-flash
      api_base: https://openrouter.ai/api/v1
      api_key: ${OPENROUTER_API_KEY}
      headers:
        "HTTP-Referer": "https://your-domain.com"
        "X-Title": "ItalianOllama"
```

Or using the `:free` model suffix:

```yaml
model_list:
  - model_name: tutor-free
    litellm_params:
      model: stepfun/step-3.5-flash:free
      api_base: https://openrouter.ai/api/v1
      api_key: ${OPENROUTER_API_KEY}
```

### Important Headers

OpenRouter requires specific headers for tracking:

```yaml
headers:
  "HTTP-Referer": "https://your-domain.com"  # Your app URL
  "X-Title": "ItalianOllama"  # Your app name
```

### Cost Considerations

| Model | Cost per 1M input | Cost per 1M output |
|-------|-------------------|---------------------|
| step-3.5-flash:free | $0 | $0 |
| qwen-2.5-7b:free | $0 | $0 |
| llama-3.1-8b:free | $0 | $0 |

## Ollama (Local)

Ollama runs models locally on your machine, perfect for development and testing.

### Installation

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download/windows
```

### Supported Models

| Model | Size | Parameters | Notes |
|-------|------|------------|-------|
| llama3.2 | ~4GB | 3B | Recommended |
| llama3.1 | ~4GB | 8B | More capable |
| mistral | ~4GB | 7B | Good balance |
| codellama | ~4GB | 7B | Code-focused |

### Pull a Model

```bash
ollama pull llama3.2
ollama list
```

### Configuration

```bash
# Environment variables
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Direct Usage (without LiteLLM)

```python
from llama import Llama

llama = Llama(model_path="models/llama3.2")
response = llama.create_chat_completion(
    messages=[{"role": "user", "content": "Ciao!"}]
)
```

## OpenAI

OpenAI provides GPT-4 and GPT-3.5 models via their API.

### Configuration

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

### LiteLLM Configuration

```yaml
model_list:
  - model_name: gpt-4-turbo
    litellm_params:
      model: openai/gpt-4-turbo
      api_key: ${OPENAI_API_KEY}
```

### Cost Considerations

| Model | Input (1K tokens) | Output (1K tokens) |
|-------|-------------------|--------------------|
| GPT-4 Turbo | $0.01 | $0.03 |
| GPT-3.5 Turbo | $0.001 | $0.002 |

## Anthropic (Claude)

Anthropic provides Claude models known for excellent reasoning.

### Configuration

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229
```

### LiteLLM Configuration

```yaml
model_list:
  - model_name: claude-opus
    litellm_params:
      model: anthropic/claude-3-opus-20240229
      api_key: ${ANTHROPIC_API_KEY}
```

## LiteLLM Configuration

### Full Configuration

```yaml
# backend/litellm/litellm_config.yaml
model_list:
  # Blablador (primary)
  - model_name: tutor
    litellm_params:
      model: openai/fake
      api_base: ${BLABLADOR_API_URL}
      api_key: ${BLABLADOR_API_KEY}


  # OpenRouter (free models)
  - model_name: tutor-free
    litellm_params:
      model: stepfun/step-3.5-flash:free
      api_base: https://openrouter.ai/api/v1
      api_key: ${OPENROUTER_API_KEY}
      headers:
        "HTTP-Referer": "https://your-domain.com"
        "X-Title": "ItalianOllama"

  # Ollama (local fallback)
  - model_name: ollama-local
    litellm_params:
      model: ollama/llama3.2
      api_base: ${OLLAMA_BASE_URL}


  # OpenAI (paid fallback)
  - model_name: gpt-4
    litellm_params:
      model: gpt-4
      api_key: ${OPENAI_API_KEY}

litellm_settings:
  drop_params: true
  set_verbose: false
  request_timeout: 120
  telemetry: false

general_settings:
  master_key: ${LITELLM_MASTER_KEY}
  database_url: "postgres://user:pass@db/litellm"
```

### Environment Variables

```bash
# Required
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy

# Optional
LITELLM_MASTER_KEY=your-master-key
LITELLM_DROP_PARAMS=true
LITELLM_MAX_PARALLEL_REQUESTS=100
```

## Provider Comparison

### Response Quality

| Provider | Italian | Speed | Reasoning | Cost |
|----------|---------|-------|-----------|------|
| Blablador | ⭐⭐⭐⭐⭐ | Fast | ⭐⭐⭐⭐ | Free* |
| Ollama | ⭐⭐⭐ | Medium | ⭐⭐⭐ | Local |
| OpenAI | ⭐⭐⭐⭐ | Fast | ⭐⭐⭐⭐⭐ | Pay |
| Anthropic | ⭐⭐⭐⭐ | Fast | ⭐⭐⭐⭐⭐ | Pay |

*For Helmholtz research institutions

### Use Cases

| Scenario | Recommended Provider |
|----------|---------------------|
| Production (research) | Blablador |
| Development | Ollama |
| Maximum quality | OpenAI GPT-4 |
| Complex reasoning | Anthropic Claude |

## Switching Providers

### Runtime Fallback

LiteLLM supports automatic fallback:

```python
from litellm import completion

response = completion(
    model="tutor",
    messages=[...],
    fallbacks=[
        {"model": "ollama-local"},
        {"model": "gpt-3.5-turbo"}
    ]
)
```

### Environment-Based

```python
import os

model = os.getenv("LITELLM_MODEL", "tutor")
# Override based on environment
if os.getenv("USE_OLLAMA"):
    model = "ollama-local"
```

## Troubleshooting

### Rate Limits

```python
from litellm import RateLimitError

try:
    response = completion(model="tutor", messages=[...])
except RateLimitError:
    # Fall back to backup provider
    response = completion(model="backup", messages=[...])
```

### Connection Issues

```bash
# Test LiteLLM health
curl http://localhost:4000/health

# Test specific provider
curl http://localhost:4000/model/info?tutor
```

## Related Documentation

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Backend Architecture](backend.md)
