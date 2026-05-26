import logging

from openai import AsyncOpenAI

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    def __init__(self, settings: Settings) -> None:
        default_headers: dict[str, str] = {}
        if settings.openrouter_http_referer:
            default_headers["HTTP-Referer"] = settings.openrouter_http_referer
        if settings.openrouter_x_title:
            default_headers["X-Title"] = settings.openrouter_x_title

        self._settings = settings
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            timeout=settings.llm_timeout_sec,
            default_headers=default_headers or None,
        )

    async def complete(self, messages: list[dict[str, str]]) -> str:
        logger.info(
            "LLM request model=%s messages=%s",
            self._settings.llm_model,
            len(messages),
        )
        response = await self._client.chat.completions.create(
            model=self._settings.llm_model,
            messages=messages,
        )
        if not response.choices:
            raise ValueError("LLM returned no choices")

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty content")

        logger.info("LLM response length=%s", len(content))
        return content
