from aiogram import Dispatcher

from src.chat_service import ChatService
from src.handlers import message as message_module
from src.handlers.start import router as start_router


def register_handlers(dp: Dispatcher, chat_service: ChatService) -> None:
    dp.include_router(start_router)
    dp.include_router(message_module.setup(chat_service))
