import pytest

from src.config import Settings

_MINIMAL_ENV = {
    "TELEGRAM_BOT_TOKEN": "t",
    "OPENROUTER_API_KEY": "k",
    "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
    "LLM_MODEL": "openrouter/auto",
    "EMBEDDING_MODEL": "openai/text-embedding-3-small",
    "DIALOG_HISTORY_LIMIT": "10",
    "CHUNK_SIZE": "1000",
    "CHUNK_OVERLAP": "200",
    "RETRIEVER_K": "4",
    "LOG_LEVEL": "INFO",
    "DATA_DIR": "data",
}


def test_settings_loads_with_minimal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, val in _MINIMAL_ENV.items():
        monkeypatch.setenv(key, val)
    s = Settings()
    assert s.retriever_k == 4
    assert s.openrouter_api_key == "k"


def test_settings_rejects_empty_openrouter_key(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, val in _MINIMAL_ENV.items():
        monkeypatch.setenv(key, val)
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        Settings()


def test_settings_rejects_bad_retriever_k(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, val in _MINIMAL_ENV.items():
        monkeypatch.setenv(key, val)
    monkeypatch.setenv("RETRIEVER_K", "0")
    with pytest.raises(ValueError, match="RETRIEVER_K"):
        Settings()


def test_settings_rejects_overlap_ge_chunk_size(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, val in _MINIMAL_ENV.items():
        monkeypatch.setenv(key, val)
    monkeypatch.setenv("CHUNK_SIZE", "500")
    monkeypatch.setenv("CHUNK_OVERLAP", "500")
    with pytest.raises(ValueError, match="CHUNK_OVERLAP"):
        Settings()


def test_settings_rejects_non_http_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, val in _MINIMAL_ENV.items():
        monkeypatch.setenv(key, val)
    monkeypatch.setenv("OPENROUTER_BASE_URL", "not-a-url")
    with pytest.raises(ValueError, match="OPENROUTER_BASE_URL"):
        Settings()
