import logging
from typing import TYPE_CHECKING

from langchain_core.messages import BaseMessage

from src.dialog_history import DialogHistory
from src.llm_client import LLMClient

if TYPE_CHECKING:
    from src.rag_chain import RagChain

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Извини, сейчас не могу ответить. Попробуй чуть позже."


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str = "",
        history: DialogHistory | None = None,
        rag_chain: "RagChain | None" = None,
    ) -> None:
        self._llm = llm_client
        self._system_prompt = system_prompt
        self._history = history
        self._rag = rag_chain

    async def handle(self, user_id: int, user_text: str) -> str:
        past: list[BaseMessage] = self._history.get_messages(user_id) if self._history else []
        try:
            if self._rag is not None and self._rag.is_ready():
                answer = await self._rag.answer(user_text, past, self._system_prompt)
            else:
                answer = await self._llm.ask(
                    user_text,
                    system_prompt=self._system_prompt,
                    history=past,
                )
        except Exception:
            logger.exception("LLM/RAG request failed")
            return FALLBACK_MESSAGE

        if self._history:
            self._history.add_user(user_id, user_text)
            self._history.add_assistant(user_id, answer)

        return answer
