"""Configuration management for Italian Tutor API.

Uses Pydantic Settings for env var validation and typing.
"""

import logging
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API settings from environment variables.

    All required settings will raise validation error at startup if missing.
    """

    # ============ Neo4j Configuration ============
    neo4j_uri: str = "bolt://localhost:7687"
    """Neo4j connection URI. Supports bolt:// (local) or neo4j+s:// (Aura cloud)"""

    neo4j_user: str = "neo4j"
    """Neo4j username"""

    neo4j_password: str = "password"
    """Neo4j password"""

    neo4j_database: str = "neo4j"
    """Neo4j database name"""

    # ============ LiteLLM Configuration ============
    litellm_base_url: str = "http://litellm:4000"
    """LiteLLM server URL"""

    litellm_api_key: str = "dummy"
    """LiteLLM API key"""

    litellm_model: str = "tutor"
    """LiteLLM model name"""

    litellm_timeout: int = 120
    """LiteLLM request timeout in seconds"""

    # ============ Blablador Direct API (Alternative) ============
    blablador_api_url: str | None = None
    """Blablador API URL (if using direct, not LiteLLM)"""

    blablador_api_key: str | None = None
    """Blablador API key"""

    blablador_model: str = "alias-fast"
    """Blablador model name"""

    # ============ Authentication & Security ============
    auth_secret: str = "dev-secret-key-do-not-use-in-production"
    """Secret key for JWT signing. Generate with: openssl rand -hex 32"""

    jwt_algorithm: str = "HS256"
    """JWT signing algorithm"""

    jwt_expiration_hours: int = 4
    """JWT token expiration time in hours"""

    # ============ CORS Configuration ============
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",
    ]
    """Allowed origin domains for CORS. Set to ['*'] for development only"""

    cors_credentials: bool = True
    """Allow credentials in CORS requests"""

    # ============ Logging ============
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """Logging level"""

    log_format: Literal["json", "text"] = "text"
    """Log output format"""

    # ============ Runtime Configuration ============
    use_aura: bool = False
    """Whether using Neo4j Aura (cloud) instead of local"""

    sentry_dsn: str | None = None
    """Sentry error tracking DSN (optional)"""

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore unknown env vars
        # Allow both snake_case and UPPER_CASE env vars


# Global settings instance (lazy loaded)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create global settings instance.

    Settings are loaded from environment variables and .env file.
    Raises ValidationError if required variables are missing.
    """
    global _settings
    if _settings is None:
        _settings = Settings()

        # Log loaded configuration (without secrets)
        logger = logging.getLogger(__name__)
        logger.info(
            f"Settings loaded: neo4j_uri={_settings.neo4j_uri}, "
            f"litellm_url={_settings.litellm_base_url}, "
            f"log_level={_settings.log_level}"
        )

    return _settings


# Convenience accessors
def get_log_level() -> int:
    """Get logging level as int."""
    return getattr(logging, get_settings().log_level)
