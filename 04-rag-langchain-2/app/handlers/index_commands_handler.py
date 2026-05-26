import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.rag.index_service import IndexService

logger = logging.getLogger(__name__)

INDEX_FAIL_MESSAGE = "Не удалось обновить индекс. Попробуйте позже."
STATUS_EMPTY_MESSAGE = (
    "Индекс пуст (0 чанков). Положите файлы в папку data/ или посмотрите логи при старте."
)


class IndexCommandsHandler:
    def __init__(self, index_service: IndexService) -> None:
        self._index_service = index_service

    def register(self, router: Router) -> None:
        router.message.register(self.handle_index, Command("index"))
        router.message.register(self.handle_index_status, Command("index_status"))

    async def handle_index(self, message: Message) -> None:
        logger.info("Incoming /index chat_id=%s", message.chat.id)
        try:
            chunk_count = await self._index_service.rebuild()
            await message.answer(f"Индекс обновлён. Чанков: {chunk_count}")
        except Exception:
            logger.exception("Manual reindex failed chat_id=%s", message.chat.id)
            await message.answer(INDEX_FAIL_MESSAGE)

    async def handle_index_status(self, message: Message) -> None:
        chunk_count = self._index_service.chunk_count()
        logger.info("Incoming /index_status chat_id=%s chunks=%s", message.chat.id, chunk_count)
        if chunk_count == 0:
            await message.answer(STATUS_EMPTY_MESSAGE)
        else:
            await message.answer(f"Чанков в индексе: {chunk_count}")
