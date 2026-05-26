from app.models.chat_message import ChatMessage


class ChatHistory:
    def __init__(self, max_pairs: int) -> None:
        self._max_pairs = max_pairs
        self._storage: dict[int, list[ChatMessage]] = {}
