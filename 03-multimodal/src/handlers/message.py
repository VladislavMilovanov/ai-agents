from io import BytesIO

from aiogram import Router
from aiogram.types import Message

from src.chat_service import ChatService

router = Router()

UNSUPPORTED_INPUT_MESSAGE = "Пришли текстовое сообщение, и я отвечу."


def setup(chat_service: ChatService) -> Router:
    @router.message()
    async def handle_message(message: Message) -> None:
        user_id = message.from_user.id if message.from_user else 0
        if message.photo:
            photo = message.photo[-1]
            file = await message.bot.get_file(photo.file_id)
            image_buffer = BytesIO()
            await message.bot.download(file, destination=image_buffer)
            answer = await chat_service.handle_image(
                user_id=user_id,
                image_bytes=image_buffer.getvalue(),
                caption=message.caption or "",
            )
            await message.answer(answer)
            return

        if message.text and message.text.strip():
            answer = await chat_service.handle_text(user_id, message.text.strip())
            await message.answer(answer)
            return

        await message.answer(UNSUPPORTED_INPUT_MESSAGE)

    return router
