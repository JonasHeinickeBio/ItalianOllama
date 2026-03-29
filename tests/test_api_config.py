"""Tests for italianollama.api.config module."""
import logging

import pytest

import italianollama.api.config as config_module
from italianollama.api.config import Settings, get_log_level, get_settings


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch):
    """Reset global _settings before each test."""
    monkeypatch.setattr(config_module, "_settings", None)
    yield
    monkeypatch.setattr(config_module, "_settings", None)


def test_settings_defaults():
    s = Settings()
    assert s.neo4j_uri == "bolt://localhost:7687"
    assert s.neo4j_user == "neo4j"
    assert s.neo4j_password == "password"
    assert s.neo4j_database == "neo4j"
    assert s.litellm_base_url == "http://litellm:4000"
    assert s.litellm_api_key == "dummy"
    assert s.litellm_model == "tutor"
    assert s.litellm_timeout == 120
    assert s.blablador_api_url is None
    assert s.blablador_api_key is None
    assert s.blablador_model == "alias-fast"
    assert s.auth_secret == "dev-secret-key-do-not-use-in-production"
    assert s.jwt_algorithm == "HS256"
    assert s.jwt_expiration_hours == 4
    assert "http://localhost:3000" in s.cors_origins
    assert s.cors_credentials is True
    assert s.log_level == "INFO"
    assert s.log_format == "text"
    assert s.use_aura is False
    assert s.sentry_dsn is None


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("NEO4J_URI", "bolt://testhost:7687")
    monkeypatch.setenv("NEO4J_USER", "testuser")
    monkeypatch.setenv("LITELLM_MODEL", "gpt-4")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    s = Settings()
    assert s.neo4j_uri == "bolt://testhost:7687"
    assert s.neo4j_user == "testuser"
    assert s.litellm_model == "gpt-4"
    assert s.log_level == "DEBUG"


def test_get_settings_singleton():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_get_settings_creates_settings():
    assert config_module._settings is None
    s = get_settings()
    assert s is not None
    assert isinstance(s, Settings)
    assert config_module._settings is s


def test_get_settings_logs(caplog):
    with caplog.at_level(logging.INFO, logger="italianollama.api.config"):
        get_settings()
    assert any("Settings loaded" in r.message for r in caplog.records)


def test_get_log_level_info():
    level = get_log_level()
    assert level == logging.INFO


def test_get_log_level_debug(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setattr(config_module, "_settings", None)
    level = get_log_level()
    assert level == logging.DEBUG


def test_get_log_level_warning(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setattr(config_module, "_settings", None)
    level = get_log_level()
    assert level == logging.WARNING


def test_settings_cors_origins():
    s = Settings()
    assert isinstance(s.cors_origins, list)
    assert len(s.cors_origins) >= 1


def test_settings_optional_fields():
    s = Settings()
    assert s.blablador_api_url is None
    assert s.blablador_api_key is None
    assert s.sentry_dsn is None


def test_settings_with_blablador(monkeypatch):
    monkeypatch.setenv("BLABLADOR_API_URL", "http://blablador:8080")
    monkeypatch.setenv("BLABLADOR_API_KEY", "secret")
    s = Settings()
    assert s.blablador_api_url == "http://blablador:8080"
    assert s.blablador_api_key == "secret"


def test_settings_extra_ignored(monkeypatch):
    monkeypatch.setenv("UNKNOWN_SETTING", "value")
    s = Settings()
    assert s is not None
