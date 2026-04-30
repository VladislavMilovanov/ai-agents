import asyncio
import logging

from aiogram import Bot, Dispatcher
from langchain_openai import OpenAIEmbeddings

from src.chat_service import ChatService
from src.config import Settings
from src.dialog_history import DialogHistory
from src.handlers import register_handlers
from src.index_service import IndexService
from src.llm_client import LLMClient
from src.logger import setup_logging
from src.rag_chain import RagChain

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings()
    setup_logging(settings.log_level)

    logger.info("Starting bot")

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
    )
    index_service = IndexService(settings, embeddings)
    try:
        chunk_total = await index_service.rebuild()
        logger.info("Startup indexing finished, chunks: %s", chunk_total)
    except Exception:
        logger.exception("Startup indexing failed; bot starts with empty index")
        index_service.set_empty_store()

    llm_client = LLMClient(settings)
    rag_chain = RagChain(settings, index_service)
    dialog_history = DialogHistory(limit=settings.dialog_history_limit)
    chat_service = ChatService(
        llm_client,
        system_prompt=settings.system_prompt,
        history=dialog_history,
        rag_chain=rag_chain,
    )

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    register_handlers(dp, chat_service, index_service)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
