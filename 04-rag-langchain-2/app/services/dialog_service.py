from app.config.settings import Settings
from app.llm.openrouter_client import OpenRouterClient
from app.rag.context_provider import ContextProvider
from app.services.chat_history import ChatHistory


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
