import pytest
from pydantic import ValidationError

from app.config.settings import Settings

_MINIMAL_ENV = {
    "TELEGRAM_BOT_TOKEN": "t",
    "OPENROUTER_API_KEY": "k",
    "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
    "LLM_MODEL": "openrouter/auto",
    "EMBEDDING_MODEL": "openai/text-embedding-3-small",
    "RETRIEVER_K": "4",
    "HISTORY_MAX_PAIRS": "10",
    "CHUNK_SIZE": "1000",
    "CHUNK_OVERLAP": "200",
    "DATA_DIR": "data",
}


def _apply_env(monkeypatch: pytest.MonkeyPatch, overrides: dict[str, str] | None = None) -> None:
    for key, value in _MINIMAL_ENV.items():
        monkeypatch.setenv(key, value)
    if overrides:
        for key, value in overrides.items():
            monkeypatch.setenv(key, value)


def test_settings_loads_with_minimal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_env(monkeypatch)
    settings = Settings()
    assert settings.retriever_k == 4
    assert settings.openrouter_api_key == "k"
    assert settings.data_dir == "data"


def test_settings_rejects_empty_openrouter_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_env(monkeypatch, {"OPENROUTER_API_KEY": ""})
    with pytest.raises(ValidationError):
        Settings()


def test_settings_rejects_bad_retriever_k(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_env(monkeypatch, {"RETRIEVER_K": "0"})
    with pytest.raises(ValidationError):
        Settings()


def test_settings_rejects_overlap_ge_chunk_size(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_env(monkeypatch, {"CHUNK_SIZE": "500", "CHUNK_OVERLAP": "500"})
    with pytest.raises(ValidationError):
        Settings()


def test_settings_rejects_non_http_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_env(monkeypatch, {"OPENROUTER_BASE_URL": "not-a-url"})
    with pytest.raises(ValidationError):
        Settings()
