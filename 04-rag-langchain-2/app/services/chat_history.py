from app.models.chat_message import ChatMessage


class ChatHistory:
    def __init__(self, max_pairs: int) -> None:
        self._max_pairs = max_pairs
        self._storage: dict[int, list[ChatMessage]] = {}

    def add(self, chat_id: int, message: ChatMessage) -> None:
        if chat_id not in self._storage:
            self._storage[chat_id] = []
        self._storage[chat_id].append(message)
        self._trim(chat_id)

    def get_messages(self, chat_id: int) -> list[ChatMessage]:
        return list(self._storage.get(chat_id, []))

    def _trim(self, chat_id: int) -> None:
        messages = self._storage.get(chat_id, [])
        max_messages = self._max_pairs * 2
        if len(messages) <= max_messages:
            return
        self._storage[chat_id] = messages[-max_messages:]
