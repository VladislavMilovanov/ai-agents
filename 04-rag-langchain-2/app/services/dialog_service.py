import logging

from app.config.settings import Settings
from app.rag.rag_chain import RagChain
from app.services.chat_history import ChatHistory

logger = logging.getLogger(__name__)

INDEX_NOT_READY_MESSAGE = (
    "База документов ещё не готова. Подождите завершения индексации или отправьте /index."
)


class DialogService:
    def __init__(
        self,
        settings: Settings,
        chat_history: ChatHistory,
        rag_chain: RagChain,
    ) -> None:
        self._settings = settings
        self._chat_history = chat_history
        self._rag_chain = rag_chain

    async def reply(self, chat_id: int, user_text: str) -> str:
        if not self._rag_chain.is_ready():
            logger.warning("RAG index not ready chat_id=%s", chat_id)
            return INDEX_NOT_READY_MESSAGE

        history = self._chat_history.get_messages(chat_id)
        logger.info(
            "Dialog RAG request chat_id=%s history_messages=%s",
            chat_id,
            len(history),
        )
        answer = await self._rag_chain.answer(
            user_text,
            history,
            self._settings.system_prompt,
        )
        self._chat_history.add_user(chat_id, user_text)
        self._chat_history.add_assistant(chat_id, answer)
        return answer
