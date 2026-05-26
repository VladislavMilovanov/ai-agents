import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.services.dialog_service import DialogService

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = (
    "Привет! Я LLM-ассистент в Telegram. Напишите мне текстовым сообщением — помогу с вопросами."
)
NON_TEXT_MESSAGE = "Сейчас я понимаю только текстовые сообщения"
EMPTY_TEXT_MESSAGE = "Напишите ваш вопрос текстом"
LLM_ERROR_MESSAGE = "Не удалось получить ответ, попробуйте позже"


class MessageHandler:
    def __init__(self, dialog_service: DialogService) -> None:
        self._dialog_service = dialog_service

    def register(self, router: Router) -> None:
        router.message.register(self.handle_start, CommandStart())
        router.message.register(self.handle_text, F.text)
        router.message.register(self.handle_non_text)

    async def handle_start(self, message: Message) -> None:
        logger.info("Incoming /start chat_id=%s", message.chat.id)
        await message.answer(WELCOME_MESSAGE)

    async def handle_text(self, message: Message) -> None:
        text = message.text or ""
        logger.info("Incoming message chat_id=%s length=%s", message.chat.id, len(text))

        if not text.strip():
            await message.answer(EMPTY_TEXT_MESSAGE)
            return

        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        try:
            reply = await self._dialog_service.reply(message.chat.id, text.strip())
        except Exception:
            logger.exception("Failed to get LLM reply chat_id=%s", message.chat.id)
            await message.answer(LLM_ERROR_MESSAGE)
            return

        await message.answer(reply)

    async def handle_non_text(self, message: Message) -> None:
        logger.debug(
            "Non-text message chat_id=%s content_type=%s",
            message.chat.id,
            message.content_type,
        )
        await message.answer(NON_TEXT_MESSAGE)
