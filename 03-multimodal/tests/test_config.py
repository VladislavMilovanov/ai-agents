import pytest

from src.config import Settings


def test_settings_reads_values_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    monkeypatch.setenv("LLM_TEXT_MODEL", "openrouter/test-model")
    monkeypatch.setenv("LLM_VISION_MODEL", "openrouter/test-vision")
    monkeypatch.setenv("SYSTEM_PROMPT", "test prompt")
    monkeypatch.setenv("DIALOG_HISTORY_LIMIT", "7")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "12")
    monkeypatch.setenv("LLM_MAX_RETRIES", "1")
    monkeypatch.setenv("MAX_RECEIPT_IMAGE_BYTES", "1024")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.telegram_bot_token == "test-token"
    assert settings.llm_api_key == "test-key"
    assert settings.llm_base_url == "https://openrouter.ai/api/v1"
    assert settings.llm_text_model == "openrouter/test-model"
    assert settings.llm_vision_model == "openrouter/test-vision"
    assert settings.system_prompt == "test prompt"
    assert settings.dialog_history_limit == 7
    assert settings.llm_timeout_seconds == 12.0
    assert settings.llm_max_retries == 1
    assert settings.max_receipt_image_bytes == 1024
    assert settings.log_level == "DEBUG"


def test_settings_fails_fast_without_required_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")

    with pytest.raises(ValueError, match="LLM_API_KEY"):
        Settings()
