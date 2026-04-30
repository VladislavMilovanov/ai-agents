import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.index_service import IndexService

logger = logging.getLogger(__name__)

INDEX_FAIL_MESSAGE = "Не удалось обновить индекс. Попробуйте позже."
STATUS_EMPTY_MESSAGE = (
    "Индекс пуст (0 чанков). Положите файлы в папку data/ или посмотрите логи при старте."
)


def setup_index_handlers(index_service: IndexService) -> Router:
    router = Router()

    @router.message(Command("index"))
    async def cmd_index(message: Message) -> None:
        try:
            n = await index_service.rebuild()
            await message.answer(f"Индекс обновлён. Чанков: {n}")
        except Exception:
            logger.exception("Manual reindex failed")
            await message.answer(INDEX_FAIL_MESSAGE)

    @router.message(Command("index_status"))
    async def cmd_index_status(message: Message) -> None:
        n = index_service.chunk_count()
        if n == 0:
            await message.answer(STATUS_EMPTY_MESSAGE)
        else:
            await message.answer(f"Чанков в индексе: {n}")

    return router
