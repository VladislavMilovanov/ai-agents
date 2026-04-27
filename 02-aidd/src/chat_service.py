import logging

from src.dialog_history import DialogHistory
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Извини, сейчас не могу ответить. Попробуй чуть позже."


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str = "",
        history: DialogHistory | None = None,
    ) -> None:
        self._llm = llm_client
        self._system_prompt = system_prompt
        self._history = history

    async def handle(self, user_id: int, user_text: str) -> str:
        past = self._history.get(user_id) if self._history else []
        try:
            answer = await self._llm.ask(
                user_text,
                system_prompt=self._system_prompt,
                history=past,
            )
        except Exception:
            logger.exception("LLM request failed")
            return FALLBACK_MESSAGE

        if self._history:
            self._history.add(user_id, "user", user_text)
            self._history.add(user_id, "assistant", answer)

        return answer
