import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.telegram_bot_token: str = self._require("TELEGRAM_BOT_TOKEN")
        self.openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_base_url: str = os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.llm_model: str = os.getenv("LLM_MODEL", "openrouter/auto")
        self.system_prompt: str = os.getenv(
            "SYSTEM_PROMPT", "Ты полезный ассистент. Отвечай чётко и по делу."
        )
        self.dialog_history_limit: int = int(os.getenv("DIALOG_HISTORY_LIMIT", "10"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def _require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
