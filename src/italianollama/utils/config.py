"""Configuration utilities for ItalianOllama."""

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager.

    Loads configuration from environment variables and config files.
    """

    def __init__(self, config_dir: Path | None = None):
        """Initialize configuration.

        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = config_dir or Path(__file__).parent.parent.parent / "config"
        self._config = {}
        self._load_env()

    def _load_env(self):
        """Load configuration from environment variables."""
        # LLM Configuration
        self._config["llm"] = {
            "provider": os.getenv("AISUITE_PROVIDER", "ollama"),
            "model": os.getenv("BLABLADOR_MODEL", "alias-fast"),
            "api_key": os.getenv("BLABLADOR_API_KEY", ""),
            "api_url": os.getenv("BLABLADOR_API_URL", "http://localhost:11434"),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "4096")),
        }

        # Neo4j Configuration
        self._config["neo4j"] = {
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "user": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", ""),
            "database": os.getenv("NEO4J_DATABASE", "neo4j"),
        }

        # Ollama Configuration
        self._config["ollama"] = {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        }

        # Language Learning Configuration
        self._config["language_learning"] = {
            "default_language": os.getenv("TARGET_LANGUAGE", "italian"),
            "default_level": os.getenv("DIFFICULTY_LEVEL", "intermediate"),
        }

        # API Configuration
        self._config["api"] = {
            "host": os.getenv("API_HOST", "0.0.0.0"),
            "port": int(os.getenv("API_PORT", "8000")),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
        }

        logger.info("Configuration loaded from environment")

    def load_yaml(self, filename: str) -> dict:
        """Load YAML configuration file.

        Args:
            filename: Name of the config file

        Returns:
            Configuration dictionary
        """
        try:
            import yaml

            config_path = self.config_dir / filename
            if config_path.exists():
                with open(config_path) as f:
                    return yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not installed")
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")

        return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Supports nested keys with dot notation (e.g., "llm.provider")

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using bracket notation."""
        return self.get(key)

    def __repr__(self) -> str:
        return f"Config(provider={self.get('llm.provider')}, language={self.get('language_learning.default_language')})"


# Global config instance
config = Config()
