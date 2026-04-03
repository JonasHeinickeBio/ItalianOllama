"""Configuration management for Sofia Chainlit frontend.

Settings are loaded from environment variables with validation via Pydantic.
All settings can be overridden via .env file or environment variables.
"""

import logging
from typing import Literal

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Frontend configuration with environment variable support.

    Attributes:
        backend_url: Base URL of the FastAPI backend (no trailing slash)
        backend_timeout: HTTP request timeout in seconds
        default_student_id: Fallback student ID for anonymous sessions
        app_name: Display name in Chainlit UI
        chat_placeholder: Placeholder text for chat input
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        neo4j_uri: Neo4j database URI
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
        neo4j_database: Neo4j database name (optional)
    """

    # ============ Backend Connection ============
    backend_url: str = Field(
        default="http://localhost:8000",
        description="Base URL of FastAPI backend excluding trailing slash",
    )

    backend_timeout: float = Field(
        default=120.0,
        description="HTTP request timeout in seconds (non-streaming)",
    )

    # ============ Student / Session ============
    default_student_id: str = Field(
        default="demo",
        description="Fallback student ID when none provided in session",
    )

    # ============ Chainlit / UI ============
    app_name: str = Field(
        default="Sofia – Italian Tutor",
        description="Application display name",
    )

    chat_placeholder: str = Field(
        default="Scrivi un messaggio... (Write a message...)",
        description="Placeholder text for chat input",
    )

    # ============ Neo4j Configuration ============
    neo4j_uri: str = Field(
        default="neo4j://localhost:7687",
        description="Neo4j database URI (e.g., neo4j://localhost:7687)",
    )

    neo4j_user: str = Field(
        default="neo4j",
        description="Neo4j username",
    )

    neo4j_password: str = Field(
        default="password",
        description="Neo4j password",
    )

    neo4j_database: str = Field(
        default="neo4j",
        description="Neo4j database name",
    )

    # ============ Logging ============
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Lazy singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the settings singleton.

    Returns:
        Settings: Global settings instance

    Note:
        Settings are cached after first access. To reset, set _settings = None.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        logging.basicConfig(level=_settings.log_level)
    return _settings
