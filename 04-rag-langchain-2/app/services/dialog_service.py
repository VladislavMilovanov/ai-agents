import logging

from app.config.settings import Settings
from app.llm.openrouter_client import OpenRouterClient
from app.models.chat_message import ChatMessage
from app.rag.context_provider import ContextProvider
from app.services.chat_history import ChatHistory

logger = logging.getLogger(__name__)


class DialogService:
    def __init__(
        self,
        settings: Settings,
        chat_history: ChatHistory,
        openrouter_client: OpenRouterClient,
        context_provider: ContextProvider,
    ) -> None:
        self._settings = settings
        self._chat_history = chat_history
        self._openrouter_client = openrouter_client
        self._context_provider = context_provider

    async def reply(self, chat_id: int, user_text: str) -> str:
        self._chat_history.add(chat_id, ChatMessage(role="user", content=user_text))

        messages: list[dict[str, str]] = [
            {"role": "system", "content": self._settings.system_prompt},
        ]
        messages.extend(
            message.to_api_dict() for message in self._chat_history.get_messages(chat_id)
        )
        messages = self._context_provider.enrich(messages)

        logger.info("Dialog request chat_id=%s messages=%s", chat_id, len(messages))
        answer = await self._openrouter_client.complete(messages)
        self._chat_history.add(chat_id, ChatMessage(role="assistant", content=answer))
        return answer
