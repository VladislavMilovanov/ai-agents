import logging
import sys

from langchain_openai import OpenAIEmbeddings
from pydantic import ValidationError

from app.bot.telegram_bot import TelegramBot
from app.config.logging_setup import setup_logging
from app.config.settings import Settings
from app.handlers.index_commands_handler import IndexCommandsHandler
from app.handlers.message_handler import MessageHandler
from app.rag.index_service import IndexService
from app.rag.rag_chain import RagChain
from app.services.chat_history import ChatHistory
from app.services.dialog_service import DialogService

_ENV_FIELD_NAMES: dict[str, str] = {
    "telegram_bot_token": "TELEGRAM_BOT_TOKEN",
    "openrouter_api_key": "OPENROUTER_API_KEY",
    "openrouter_base_url": "OPENROUTER_BASE_URL",
    "llm_model": "LLM_MODEL",
    "embedding_model": "EMBEDDING_MODEL",
    "system_prompt": "SYSTEM_PROMPT",
    "retriever_k": "RETRIEVER_K",
    "data_dir": "DATA_DIR",
    "chunk_size": "CHUNK_SIZE",
    "chunk_overlap": "CHUNK_OVERLAP",
    "history_max_pairs": "HISTORY_MAX_PAIRS",
    "llm_timeout_sec": "LLM_TIMEOUT_SEC",
    "log_level": "LOG_LEVEL",
    "openrouter_http_referer": "OPENROUTER_HTTP_REFERER",
    "openrouter_x_title": "OPENROUTER_X_TITLE",
}


def _load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        for error in exc.errors():
            field = error.get("loc", ("",))[0]
            env_name = _ENV_FIELD_NAMES.get(str(field), str(field).upper())
            message = error.get("msg", "некорректное значение")
            print(f"Ошибка конфигурации: {env_name} — {message}", file=sys.stderr)
        sys.exit(1)


async def main() -> None:
    settings = _load_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
    )
    index_service = IndexService(settings, embeddings)
    try:
        chunk_total = await index_service.rebuild()
        logger.info("Startup indexing finished, chunks=%s", chunk_total)
    except Exception:
        logger.exception("Startup indexing failed; bot starts with empty index")
        index_service.set_empty_store()

    rag_chain = RagChain(settings, index_service)
    logger.info("RAG chain ready=%s chunks=%s", rag_chain.is_ready(), index_service.chunk_count())

    chat_history = ChatHistory(max_pairs=settings.history_max_pairs)
    dialog_service = DialogService(settings, chat_history, rag_chain)
    message_handler = MessageHandler(dialog_service)
    index_commands_handler = IndexCommandsHandler(index_service)
    telegram_bot = TelegramBot(settings, message_handler, index_commands_handler)

    logger.info("Application started")
    await telegram_bot.start()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
