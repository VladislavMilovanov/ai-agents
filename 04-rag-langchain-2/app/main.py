import logging
import sys

from pydantic import ValidationError

from app.bot.telegram_bot import TelegramBot
from app.config.logging_setup import setup_logging
from app.config.settings import Settings
from app.handlers.message_handler import MessageHandler
from app.llm.openrouter_client import OpenRouterClient
from app.rag.context_provider import ContextProvider
from app.services.chat_history import ChatHistory
from app.services.dialog_service import DialogService

_ENV_FIELD_NAMES: dict[str, str] = {
    "telegram_bot_token": "TELEGRAM_BOT_TOKEN",
    "openrouter_api_key": "OPENROUTER_API_KEY",
    "openrouter_base_url": "OPENROUTER_BASE_URL",
    "llm_model": "LLM_MODEL",
    "system_prompt": "SYSTEM_PROMPT",
    "history_max_pairs": "HISTORY_MAX_PAIRS",
    "llm_timeout_sec": "LLM_TIMEOUT_SEC",
    "log_level": "LOG_LEVEL",
    "openrouter_http_referer": "OPENROUTER_HTTP_REFERER",
    "openrouter_x_title": "OPENROUTER_X_TITLE",
}


def _load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        for error in exc.errors():
            field = error.get("loc", ("",))[0]
            env_name = _ENV_FIELD_NAMES.get(str(field), str(field).upper())
            message = error.get("msg", "некорректное значение")
            print(f"Ошибка конфигурации: {env_name} — {message}", file=sys.stderr)
        sys.exit(1)


async def main() -> None:
    settings = _load_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    chat_history = ChatHistory(max_pairs=settings.history_max_pairs)
    openrouter_client = OpenRouterClient(settings)
    context_provider = ContextProvider()
    dialog_service = DialogService(
        settings,
        chat_history,
        openrouter_client,
        context_provider,
    )
    message_handler = MessageHandler(dialog_service)
    telegram_bot = TelegramBot(settings, message_handler)

    logger.info("Application started")
    await telegram_bot.start()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
