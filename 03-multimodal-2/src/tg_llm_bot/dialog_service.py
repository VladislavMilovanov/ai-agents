from collections import defaultdict

from tg_llm_bot.llm_client import LlmClient


class DialogService:
    def __init__(
        self,
        system_prompt: str,
        llm: LlmClient,
        max_messages: int,
    ) -> None:
        self._system_prompt = system_prompt
        self._llm = llm
        self._max_messages = max_messages
        self._histories: dict[int, list[dict[str, str]]] = defaultdict(list)

    def _trim(self, history: list[dict[str, str]]) -> None:
        while len(history) > self._max_messages:
            history.pop(0)
            if history:
                history.pop(0)

    async def reply(self, chat_id: int, user_text: str) -> str:
        history = self._histories[chat_id]
        history.append({"role": "user", "content": user_text})
        self._trim(history)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self._system_prompt},
            *history,
        ]
        answer = await self._llm.complete(messages)
        history.append({"role": "assistant", "content": answer})
        self._trim(history)
        return answer
