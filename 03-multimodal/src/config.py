import os

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SYSTEM_PROMPT = """
Ты — персональный финансовый советник и бухгалтер личных финансов.
Твоя задача — из текста и фото чеков извлекать данные транзакции в строгом формате.

Если пользователь сообщает доход или расход, верни action=transaction и заполни поля:
- occurred_at: дата и время в ISO формате YYYY-MM-DDTHH:MM:SS
- direction: income или expense
- amount: число больше 0
- expense_type: daily, periodic или one_time
- category: короткая категория (продукты, рестораны, такси, образование, путешествия и т.д.)
- description: краткое понятное описание операции

Если пользователь просит отчет/баланс, верни action=report и period:
- day, week или month

Если данных недостаточно или это не финансовая запись, верни action=unknown.

Правила:
- Не выдумывай сумму и дату, если они не читаются. В таком случае action=unknown.
- Для фотографий чеков выделяй итоговую сумму покупки и нормализуй формат даты/времени.
- Ответ должен быть только структурированным JSON по заданной схеме.
""".strip()


class Settings:
    def __init__(self) -> None:
        self.telegram_bot_token: str = self._require("TELEGRAM_BOT_TOKEN")
        self.llm_api_key: str = os.getenv("LLM_API_KEY", "")
        self.llm_base_url: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        self.llm_text_model: str = os.getenv("LLM_TEXT_MODEL", "openrouter/auto")
        self.llm_vision_model: str = os.getenv("LLM_VISION_MODEL", self.llm_text_model)
        self.system_prompt: str = os.getenv("SYSTEM_PROMPT", _DEFAULT_SYSTEM_PROMPT)
        self.dialog_history_limit: int = int(os.getenv("DIALOG_HISTORY_LIMIT", "10"))
        self.llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        self.llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
        self.max_receipt_image_bytes: int = int(
            os.getenv("MAX_RECEIPT_IMAGE_BYTES", str(5 * 1024 * 1024))
        )
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self._validate()

    @staticmethod
    def _require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    def _validate(self) -> None:
        if "openrouter.ai" in self.llm_base_url and not self.llm_api_key:
            raise ValueError("Required environment variable 'LLM_API_KEY' is not set")
        if self.llm_timeout_seconds <= 0:
            raise ValueError("LLM_TIMEOUT_SECONDS must be greater than zero")
        if self.llm_max_retries < 0:
            raise ValueError("LLM_MAX_RETRIES must be zero or greater")
        if self.max_receipt_image_bytes <= 0:
            raise ValueError("MAX_RECEIPT_IMAGE_BYTES must be greater than zero")
