"""Configuration management for the Sofia Chainlit frontend.

Uses Pydantic Settings for env var validation and typing.
All settings can be overridden via environment variables or a .env file.
"""

import logging
from typing import Literal

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Frontend settings loaded from environment variables.

    Attributes are matched case-insensitively against environment variables,
    so ``BACKEND_URL=http://api:8000`` sets :attr:`backend_url`.
    """

    # ============ Backend Connection ============
    backend_url: str = "http://localhost:8000"
    """Base URL of the FastAPI backend (no trailing slash)."""

    backend_timeout: float = 30.0
    """HTTP request timeout in seconds for non-streaming calls."""

    # ============ Student / Session ============
    default_student_id: str = "demo"
    """Fallback student ID when none is supplied via the session environment."""

    # ============ Chainlit / UI ============
    app_name: str = "Sofia – Italian Tutor"
    """Display name shown in the Chainlit UI."""

    # ============ Logging ============
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """Logging level for the frontend process."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# ---------------------------------------------------------------------------
# Module-level singleton – created lazily on first access
# ---------------------------------------------------------------------------

_settings: Settings | None = None


def get_settings() -> Settings:
    """Return (or lazily create) the global :class:`Settings` instance."""
    global _settings
    if _settings is None:
        _settings = Settings()

        logger = logging.getLogger(__name__)
        logger.info(
            "Frontend settings loaded: backend_url=%s log_level=%s",
            _settings.backend_url,
            _settings.log_level,
        )

    return _settings
