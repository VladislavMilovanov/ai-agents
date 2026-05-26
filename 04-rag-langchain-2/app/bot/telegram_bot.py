import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message

from app.config.settings import Settings
from app.handlers.message_handler import MessageHandler

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, settings: Settings, message_handler: MessageHandler) -> None:
        self._bot = Bot(token=settings.telegram_bot_token)
        self._dispatcher = Dispatcher()
        self._message_handler = message_handler

        private_router = Router()
        private_router.message.filter(F.chat.type == "private")
        message_handler.register(private_router)
        self._dispatcher.include_router(private_router)

        self._dispatcher.message.register(self._log_non_private_message, ~F.chat.type == "private")

    async def start(self) -> None:
        logger.info("Starting Telegram long polling")
        await self._dispatcher.start_polling(self._bot)

    @staticmethod
    async def _log_non_private_message(message: Message) -> None:
        logger.debug(
            "Ignored non-private message chat_id=%s type=%s",
            message.chat.id,
            message.chat.type,
        )
