import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.services.dialog_service import DialogService

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = (
    "Привет! Я LLM-ассистент в Telegram. Напишите мне текстовым сообщением — помогу с вопросами."
)


class MessageHandler:
    def __init__(self, dialog_service: DialogService) -> None:
        self._dialog_service = dialog_service

    def register(self, router: Router) -> None:
        router.message.register(self.handle_start, CommandStart())

    async def handle_start(self, message: Message) -> None:
        logger.info("Incoming /start chat_id=%s", message.chat.id)
        await message.answer(WELCOME_MESSAGE)
