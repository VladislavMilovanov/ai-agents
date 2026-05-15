import asyncio
import logging
import sys

from tg_llm_bot.dialog_service import DialogService
from tg_llm_bot.llm_client import LlmClient
from tg_llm_bot.settings import Settings
from tg_llm_bot.telegram_bot import TelegramBotApp


def setup_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
        force=True,
    )
    for noisy in ("httpx", "httpcore", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


async def main(settings: Settings) -> None:
    setup_logging(settings.log_level)
    logger.info(
        "tg_llm_bot starting log_level=%s llm_model=%s",
        settings.log_level,
        settings.llm_model,
    )
    llm = LlmClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        model=settings.llm_model,
    )
    dialogs = DialogService(
        system_prompt=settings.system_prompt,
        llm=llm,
        max_messages=settings.dialog_max_messages,
    )
    app = TelegramBotApp(bot_token=settings.telegram_bot_token, dialogs=dialogs)
    await app.run_polling()


def run_main() -> None:
    try:
        settings = Settings.from_env()
    except ValueError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        raise SystemExit(1) from None

    asyncio.run(main(settings))


if __name__ == "__main__":
    run_main()
