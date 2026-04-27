from aiogram import Router
from aiogram.types import Message

from src.chat_service import ChatService

router = Router()

UNSUPPORTED_INPUT_MESSAGE = "Пришли текстовое сообщение, и я отвечу."


def setup(chat_service: ChatService) -> Router:
    @router.message()
    async def handle_message(message: Message) -> None:
        if not message.text or not message.text.strip():
            await message.answer(UNSUPPORTED_INPUT_MESSAGE)
            return
        answer = await chat_service.handle(message.text.strip())
        await message.answer(answer)

    return router
