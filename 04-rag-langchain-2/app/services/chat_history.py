from collections import deque

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ChatHistory:
    def __init__(self, max_pairs: int) -> None:
        self._max_messages = max_pairs * 2
        self._storage: dict[int, deque[BaseMessage]] = {}

    def add_user(self, chat_id: int, content: str) -> None:
        self._append(chat_id, HumanMessage(content=content))

    def add_assistant(self, chat_id: int, content: str) -> None:
        self._append(chat_id, AIMessage(content=content))

    def get_messages(self, chat_id: int) -> list[BaseMessage]:
        return list(self._storage.get(chat_id, []))

    def _append(self, chat_id: int, message: BaseMessage) -> None:
        if chat_id not in self._storage:
            self._storage[chat_id] = deque(maxlen=self._max_messages)
        self._storage[chat_id].append(message)
