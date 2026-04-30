from aiogram import Dispatcher

from src.chat_service import ChatService
from src.handlers import message as message_module
from src.handlers.index_commands import setup_index_handlers
from src.handlers.start import router as start_router
from src.index_service import IndexService


def register_handlers(
    dp: Dispatcher,
    chat_service: ChatService,
    index_service: IndexService,
) -> None:
    dp.include_router(start_router)
    dp.include_router(setup_index_handlers(index_service))
    dp.include_router(message_module.setup(chat_service))
