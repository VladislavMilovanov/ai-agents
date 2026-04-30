import os

from dotenv import load_dotenv

load_dotenv()


def _env_first(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    return default


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

Короткие фразы вроде «100 р хлеб», «500 р кофе», «1000₽ такси» — это расход (expense):
сумма из числа, описание из текста после суммы, occurred_at — текущие дата и время,
если пользователь не указал дату явно.

Если пользователь просит отчет/баланс, верни action=report и period:
- day, week или month

Если данных недостаточно или это не финансовая запись, верни action=unknown.

Правила:
- Не выдумывай сумму и дату, если они не читаются. В таком случае action=unknown.
- Для фотографий чеков выделяй итоговую сумму покупки и нормализуй формат даты/времени.
- Ответ должен быть только структурированным JSON по заданной схеме.
- Для приветствий и сообщений без суммы/операции (например «привет») верни action=unknown.
- Поле direction только латиницей: income или expense.
- Поле expense_type: daily, periodic или one_time.
- Дата occurred_at в ISO: YYYY-MM-DDTHH:MM:SS (локальное время, без часового пояса).
""".strip()


class Settings:
    def __init__(self) -> None:
        self.telegram_bot_token: str = self._require("TELEGRAM_BOT_TOKEN")
        self.llm_api_key: str = _env_first("LLM_API_KEY", "OPENROUTER_API_KEY")
        self.llm_base_url: str = _env_first(
            "LLM_BASE_URL",
            "OPENROUTER_BASE_URL",
            default="https://openrouter.ai/api/v1",
        )
        self.llm_text_model: str = _env_first(
            "LLM_TEXT_MODEL", "LLM_MODEL", default="openrouter/auto"
        )
        self.llm_vision_model: str = _env_first("LLM_VISION_MODEL") or self.llm_text_model
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
            raise ValueError(
                "Set LLM_API_KEY or OPENROUTER_API_KEY when LLM_BASE_URL points to OpenRouter"
            )
        if self.llm_timeout_seconds <= 0:
            raise ValueError("LLM_TIMEOUT_SECONDS must be greater than zero")
        if self.llm_max_retries < 0:
            raise ValueError("LLM_MAX_RETRIES must be zero or greater")
        if self.max_receipt_image_bytes <= 0:
            raise ValueError("MAX_RECEIPT_IMAGE_BYTES must be greater than zero")
