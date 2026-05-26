from openai import AsyncOpenAI

from app.config.settings import Settings


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
