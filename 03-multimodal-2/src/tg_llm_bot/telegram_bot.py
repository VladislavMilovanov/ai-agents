import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.types.error_event import ErrorEvent

from tg_llm_bot.dialog_service import DialogService

logger = logging.getLogger(__name__)


class TelegramBotApp:
    def __init__(self, bot_token: str, dialogs: DialogService) -> None:
        self._bot = Bot(token=bot_token)
        self._dp = Dispatcher()
        self._dialogs = dialogs
        router = Router()
        router.message.register(self._on_start, CommandStart())
        router.message.register(self._on_message, ~Command())
        self._dp.include_router(router)
        self._dp.errors.register(self._on_dispatch_error)

    async def _on_dispatch_error(self, event: ErrorEvent) -> None:
        update_id = getattr(event.update, "update_id", None)
        logger.error(
            "Unhandled error while handling update_id=%s",
            update_id,
            exc_info=event.exception,
        )

    async def _on_start(self, message: Message) -> None:
        await message.answer(
            "Я отвечаю как технический специалист по состоянию оборудования "
            "(вибродиагностика, нормы, документация — из ваших сообщений).\n\n"
            "Вставляйте в текст выдержки из ГОСТ/регламентов и фактические "
            "замеры; без них задам уточнения. Не подставляю числа «с потолка»."
        )

    async def _on_message(self, message: Message) -> None:
        if message.text is None:
            await message.answer("Пока поддерживаю только текст.")
            return
        try:
            reply_text = await self._dialogs.reply(message.chat.id, message.text)
        except Exception:
            logger.exception("LLM or dialog failed chat_id=%s", message.chat.id)
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
            return
        await message.answer(reply_text)

    async def run_polling(self) -> None:
        logger.info("Telegram long polling started")
        await self._dp.start_polling(self._bot)
