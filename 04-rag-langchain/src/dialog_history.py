from collections import deque

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class DialogHistory:
    """Per-user буфер последних реплик в формате LangChain (только Human / AI)."""

    def __init__(self, limit: int = 10) -> None:
        self._limit = limit
        self._store: dict[int, deque[BaseMessage]] = {}

    def add_user(self, user_id: int, content: str) -> None:
        self._append(user_id, HumanMessage(content=content))

    def add_assistant(self, user_id: int, content: str) -> None:
        self._append(user_id, AIMessage(content=content))

    def _append(self, user_id: int, message: BaseMessage) -> None:
        if user_id not in self._store:
            self._store[user_id] = deque(maxlen=self._limit)
        self._store[user_id].append(message)

    def get_messages(self, user_id: int) -> list[BaseMessage]:
        return list(self._store.get(user_id, []))
