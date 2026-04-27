from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def handle_message(message: Message) -> None:
    await message.answer(f"Получил твоё сообщение: «{message.text}»")
