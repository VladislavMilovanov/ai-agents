from aiogram import Dispatcher

from src.handlers.message import router as message_router
from src.handlers.start import router as start_router


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(message_router)
