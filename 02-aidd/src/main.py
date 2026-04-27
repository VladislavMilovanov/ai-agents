import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.config import Settings
from src.handlers import register_handlers
from src.logger import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings()
    setup_logging(settings.log_level)

    logger.info("Starting bot")

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
