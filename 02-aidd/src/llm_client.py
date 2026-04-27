import logging

from openai import AsyncOpenAI

from src.config import Settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self._model = settings.llm_model
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )

    async def ask(self, user_text: str, system_prompt: str = "") -> str:
        logger.debug("LLM request: %s", user_text[:100])
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_text})
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        answer = response.choices[0].message.content or ""
        logger.debug("LLM response: %s", answer[:100])
        return answer
