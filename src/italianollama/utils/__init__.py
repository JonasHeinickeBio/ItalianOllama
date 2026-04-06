"""Utility modules for ItalianOllama."""

from .deepl import (
    DeepLClient,
    format_translation_for_vocabulary,
    get_deepl_client,
)
from .openrouter import (
    OpenRouterAPI,
    add_free_models_to_config,
    discover_free_models,
    format_model_for_litellm,
    update_litellm_config,
)

__all__ = [
    "DeepLClient",
    "format_translation_for_vocabulary",
    "get_deepl_client",
    "OpenRouterAPI",
    "add_free_models_to_config",
    "discover_free_models",
    "format_model_for_litellm",
    "update_litellm_config",
]
