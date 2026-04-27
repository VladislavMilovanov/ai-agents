from aiogram import Router
from aiogram.types import Message

from src.chat_service import ChatService

router = Router()


def setup(chat_service: ChatService) -> Router:
    @router.message()
    async def handle_message(message: Message) -> None:
        if not message.text:
            return
        answer = await chat_service.handle(message.text)
        await message.answer(answer)

    return router
