import logging

from src.llm_client import LLMClient

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Извини, сейчас не могу ответить. Попробуй чуть позже."


class ChatService:
    def __init__(self, llm_client: LLMClient, system_prompt: str = "") -> None:
        self._llm = llm_client
        self._system_prompt = system_prompt

    async def handle(self, user_text: str) -> str:
        try:
            return await self._llm.ask(user_text, system_prompt=self._system_prompt)
        except Exception:
            logger.exception("LLM request failed")
            return FALLBACK_MESSAGE
