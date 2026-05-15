import logging

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LlmClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete(self, messages: list[dict[str, str]]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        if not response.choices:
            logger.warning("LLM returned no choices")
            return ""
        choice = response.choices[0].message
        content = choice.content
        return content if content else ""
