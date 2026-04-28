from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Привет! Я финансовый бот.\n"
        "Можешь прислать текст о доходе/расходе, фото чека "
        "или запросить отчет за день/неделю/месяц."
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Я персональный финансовый ассистент.\n"
        "Что я умею:\n"
        "- сохранить доход или расход из текста;\n"
        "- извлечь транзакцию из фото чека;\n"
        "- собрать отчет за день, неделю или месяц."
    )
