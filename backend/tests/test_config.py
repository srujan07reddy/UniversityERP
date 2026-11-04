import os
from app.core.config import Settings, get_settings


def test_settings_defaults():
    """Verify default configuration attributes and types."""
    settings = Settings()
    assert settings.PROJECT_NAME == "Jeppiaar University ERP"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
    assert len(settings.BACKEND_CORS_ORIGINS) > 0


def test_cors_origins_validator_string():
    """Verify assembling CORS origins from a comma-separated string."""
    cors_str = "http://localhost:3000, https://erp.jeppiaar.ac.in, http://localhost:5173"
    result = Settings.assemble_cors_origins(cors_str)
    assert result == [
        "http://localhost:3000",
        "https://erp.jeppiaar.ac.in",
        "http://localhost:5173",
    ]


def test_cors_origins_validator_list():
    """Verify preserving CORS origins when provided as a list."""
    cors_list = ["http://localhost:3000", "https://erp.jeppiaar.ac.in"]
    result = Settings.assemble_cors_origins(cors_list)
    assert result == cors_list


def test_cors_origins_validator_invalid_or_empty():
    """Verify assembling CORS origins returns empty list for unexpected types."""
    assert Settings.assemble_cors_origins(123) == []  # type: ignore


def test_get_settings_caching():
    """Verify that get_settings is cached (LRU)."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_settings_environment_override(monkeypatch):
    """Verify environment variable overrides take precedence."""
    monkeypatch.setenv("PROJECT_NAME", "Overridden ERP")
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("DEBUG", "False")

    custom_settings = Settings()
    assert custom_settings.PROJECT_NAME == "Overridden ERP"
    assert custom_settings.ENVIRONMENT == "staging"
    assert custom_settings.DEBUG is False

