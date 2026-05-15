import os
from dataclasses import dataclass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise ValueError(f"Missing required environment variable: {name}")
    return value.strip()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openrouter_api_key: str
    openrouter_base_url: str
    llm_model: str
    system_prompt: str
    log_level: str
    dialog_max_messages: int

    @staticmethod
    def from_env() -> "Settings":
        raw_max = os.environ.get("DIALOG_MAX_MESSAGES", "20").strip()
        try:
            dialog_max = int(raw_max)
        except ValueError as exc:
            raise ValueError("DIALOG_MAX_MESSAGES must be an integer") from exc
        if dialog_max < 2:
            dialog_max = 2

        return Settings(
            telegram_bot_token=_require("TELEGRAM_BOT_TOKEN"),
            openrouter_api_key=_require("OPENROUTER_API_KEY"),
            openrouter_base_url=os.environ.get(
                "OPENROUTER_BASE_URL",
                "https://openrouter.ai/api/v1",
            ).strip(),
            llm_model=os.environ.get("LLM_MODEL", "openai/gpt-4o-mini").strip(),
            system_prompt=os.environ.get(
                "SYSTEM_PROMPT",
                "You are a helpful assistant.",
            ).strip(),
            log_level=os.environ.get("LOG_LEVEL", "INFO").strip(),
            dialog_max_messages=dialog_max,
        )
