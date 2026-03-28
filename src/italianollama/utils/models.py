"""Model management utilities using hellmholtz.

This module provides access to Blablador models, their availability,
and token limits through the hellmholtz package.
"""

import logging
import os

logger = logging.getLogger(__name__)


def get_blablador_models() -> list[dict]:
    """Get list of available Blablador models from hellmholtz.

    Returns:
        List of model dictionaries with name, description, and token limits
    """
    try:
        from hellmholtz.providers.blablador_config import KNOWN_MODELS, BlabladorModel

        models = []
        for model in KNOWN_MODELS:
            models.append(
                {
                    "name": model.name,
                    "alias": model.alias,
                    "description": model.description,
                    "max_context_tokens": model.max_context_tokens,
                    "api_id": model.api_id,
                }
            )
        return models

    except ImportError:
        logger.warning("hellmholtz not installed, cannot get model list")
        return []


def get_model_info(model_name: str) -> dict | None:
    """Get information about a specific model.

    Args:
        model_name: Name, alias, or ID of the model

    Returns:
        Model info dict or None if not found
    """
    try:
        from hellmholtz.providers.blablador_config import BlabladorModel, get_model_by_name

        model = get_model_by_name(model_name)
        if model:
            return {
                "name": model.name,
                "alias": model.alias,
                "description": model.description,
                "max_context_tokens": model.max_context_tokens,
                "api_id": model.api_id,
            }
    except ImportError:
        logger.warning("hellmholtz not installed")

    return None


def get_token_limit(model_name: str) -> int:
    """Get the maximum context token limit for a model.

    Args:
        model_name: Name of the model

    Returns:
        Maximum context tokens
    """
    try:
        from hellmholtz.providers.blablador_config import get_token_limit

        return get_token_limit(model_name)
    except ImportError:
        # Fallback defaults
        defaults = {
            "alias-fast": 32768,
            "alias-large": 131072,
            "alias-huge": 131072,
            "alias-code": 131072,
            "llama3.2": 131072,
        }
        return defaults.get(model_name, 32768)


def get_default_model() -> str:
    """Get the default model from environment or fallbacks.

    Returns:
        Model name string
    """
    # Check environment
    model = os.getenv("BLABLADOR_MODEL") or os.getenv("OLLAMA_MODEL")
    if model:
        return model

    # Check if alias-fast is available
    info = get_model_info("alias-fast")
    if info:
        return "alias-fast"

    return "llama3.2"


def list_alias_models() -> list[dict]:
    """Get list of alias models (optimized routing models).

    Returns:
        List of alias model info
    """
    models = get_blablador_models()
    return [m for m in models if m.get("alias")]


def list_code_models() -> list[dict]:
    """Get list of models optimized for coding.

    Returns:
        List of code model info
    """
    models = get_blablador_models()
    return [m for m in models if "code" in m.get("name", "").lower()]


class ModelManager:
    """Manage model selection and availability checking."""

    def __init__(self):
        """Initialize the model manager."""
        self._monitor = None
        self._init_monitor()

    def _init_monitor(self):
        """Initialize the availability monitor."""
        try:
            from hellmholtz.monitoring import ModelAvailabilityMonitor

            api_key = os.getenv("BLABLADOR_API_KEY")
            api_base = os.getenv(
                "BLABLADOR_API_URL", "https://api.helmholtz-blablador.fz-juelich.de/v1/"
            )

            if api_key:
                self._monitor = ModelAvailabilityMonitor(api_key=api_key, api_base=api_base)
        except Exception as e:
            logger.warning(f"Could not initialize model monitor: {e}")

    def get_available_models(self) -> list[dict]:
        """Get currently available models from API.

        Returns:
            List of available model info
        """
        if not self._monitor:
            return get_blablador_models()

        try:
            api_models = self._monitor.get_api_models()
            return [{"id": m["id"], "object": m.get("object")} for m in api_models]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []

    def check_model_accessibility(self, model_name: str) -> tuple[bool, float]:
        """Test if a model is accessible.

        Args:
            model_name: Name of the model to test

        Returns:
            Tuple of (is_accessible, latency_seconds)
        """
        if not self._monitor:
            return False, 0.0

        try:
            return self._monitor.test_model_accessibility(model_name)
        except Exception as e:
            logger.error(f"Failed to test model accessibility: {e}")
            return False, 0.0

    def get_model_status(self) -> dict:
        """Get complete model status from YAML.

        Returns:
            Model status dictionary
        """
        if not self._monitor:
            return {}

        try:
            return self._monitor.load_model_status()
        except Exception as e:
            logger.error(f"Failed to load model status: {e}")
            return {}

    def update_model_status(self) -> dict:
        """Update model status from API.

        Returns:
            Updated model status
        """
        if not self._monitor:
            return {}

        try:
            return self._monitor.check_all_models_automatically()
        except Exception as e:
            logger.error(f"Failed to update model status: {e}")
            return {}

    def generate_report(self, test_accessibility: bool = True) -> str:
        """Generate availability report.

        Args:
            test_accessibility: Whether to test model accessibility

        Returns:
            Report string
        """
        if not self._monitor:
            return "Model monitor not initialized"

        try:
            analysis = self._monitor.analyze_availability(test_accessibility=test_accessibility)
            return self._monitor.generate_report(analysis, test_accessibility=test_accessibility)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return f"Error: {e}"


# Singleton instance
_model_manager: ModelManager | None = None


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
