"""OpenRouter API utilities for free model discovery and configuration.

Best practices implemented:
- Use os.environ/ prefix for secrets in config (Lazy evaluation)
- Add rpm and tpm for proper load balancing
- Include proper error handling and timeout management
- Follow LiteLLM naming conventions
- Support environment-specific routing
"""

import os
from typing import Optional

import httpx


class OpenRouterAPI:
    """Interface to OpenRouter API for model discovery and configuration."""

    BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RPM = 60
    DEFAULT_TPM = 100000

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenRouter API client.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.client: Optional[httpx.AsyncClient] = None
        self._base_url = self.BASE_URL

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", ""),
                    "X-Title": os.getenv("OPENROUTER_X_TITLE", "ItalianOllama"),
                },
                timeout=self.DEFAULT_TIMEOUT,
            )
        return self.client

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def get_models(self, free_only: bool = False) -> list[dict]:
        """Get list of available models from OpenRouter.

        Args:
            free_only: If True, return only free models

        Returns:
            List of model information dictionaries
        """
        client = await self._get_client()
        response = await client.get("/models")
        response.raise_for_status()

        models = response.json().get("data", [])

        if free_only:
            models = [
                model for model in models if self._is_free_model(model)
            ]

        return models

    def _is_free_model(self, model: dict) -> bool:
        """Check if a model is free (price per token is zero or very low).

        Best practice: Check both prompt and completion pricing are exactly $0
        """
        pricing = model.get("pricing", {})

        try:
            prompt_price = float(pricing.get("prompt", "0"))
            completion_price = float(pricing.get("completion", "0"))

            return prompt_price == 0 and completion_price == 0
        except (ValueError, TypeError):
            return False

    async def get_free_models(self) -> list[dict]:
        """Get only free models from OpenRouter.

        Returns:
            List of free model information dictionaries
        """
        return await self.get_models(free_only=True)

    async def get_model_pricing(self, model_id: str) -> dict:
        """Get detailed pricing information for a specific model.

        Args:
            model_id: OpenRouter model ID (e.g., 'openai/gpt-3.5-turbo')

        Returns:
            Dictionary with pricing information
        """
        client = await self._get_client()
        response = await client.get(f"/models/{model_id}")
        response.raise_for_status()

        return response.json().get("data", {})


def format_model_for_litellm(model: dict) -> dict:
    """Format an OpenRouter model for LiteLLM configuration.

    Best practices implemented:
    - Use rpm AND tpm for proper load balancing
    - Format model names consistently
    - Use lazy environment variable evaluation

    Args:
        model: OpenRouter model information

    Returns:
        LiteLLM-compatible model configuration
    """
    model_id = model["id"]
    model_name = model.get("name", model_id)

    return {
        "model_name": f"openrouter-{model_id.replace('/', '-')}",
        "litellm_params": {
            "model": f"openrouter/{model_id}",
            "api_key": "os.environ/OPENROUTER_API_KEY",
            "rpm": OpenRouterAPI.DEFAULT_RPM,
            "tpm": OpenRouterAPI.DEFAULT_TPM,
            "timeout": 120,
        },
        "model_info": {
            "id": model_id,
            "provider": model_id.split("/")[0] if "/" in model_id else "unknown",
        },
    }


def update_litellm_config(
    models: list[dict],
    config_path: str = "backend/litellm/litellm_config.yaml",
) -> None:
    """Update LiteLLM config with new models.

    Best practices implemented:
    - Preserve existing configuration structure
    - Avoid duplicate models
    - Maintain proper YAML formatting

    Args:
        models: List of model configurations to add
        config_path: Path to LiteLLM config file
    """
    import yaml

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    existing_models = config.get("model_list", [])

    for new_model in models:
        model_name = new_model["model_name"]
        if not any(m["model_name"] == model_name for m in existing_models):
            existing_models.append(new_model)

    config["model_list"] = existing_models

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


async def discover_free_models() -> list[dict]:
    """Discover and return free models from OpenRouter.

    Best practices implemented:
    - Check for API key before making requests
    - Properly close HTTP client after use

    Returns:
        List of free model information dictionaries
    """
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    api = OpenRouterAPI(api_key)

    try:
        free_models = await api.get_free_models()
        return free_models
    finally:
        await api.close()


async def add_free_models_to_config(
    config_path: str = "backend/litellm/litellm_config.yaml",
) -> list[str]:
    """Discover free models from OpenRouter and add them to LiteLLM config.

    Best practices implemented:
    - Validate API key availability
    - Format models correctly for LiteLLM
    - Update config safely

    Args:
        config_path: Path to LiteLLM config file

    Returns:
        List of model names that were added
    """
    free_models = await discover_free_models()

    if not free_models:
        return []

    model_configs = [format_model_for_litellm(model) for model in free_models]

    update_litellm_config(model_configs, config_path)

    return [m["model_name"] for m in model_configs]
