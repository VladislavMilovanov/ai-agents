from collections import deque


class DialogHistory:
    def __init__(self, limit: int = 10) -> None:
        self._limit = limit
        self._store: dict[int, deque[dict[str, str]]] = {}

    def add(self, user_id: int, role: str, content: str) -> None:
        if user_id not in self._store:
            self._store[user_id] = deque(maxlen=self._limit)
        self._store[user_id].append({"role": role, "content": content})

    def get(self, user_id: int) -> list[dict[str, str]]:
        return list(self._store.get(user_id, []))
