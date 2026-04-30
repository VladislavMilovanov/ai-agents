import asyncio
import base64
import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI

from src.config import Settings
from src.extraction_result import ExtractionResult

logger = logging.getLogger(__name__)

_FINANCE_JSON_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "finance_event",
        "schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["transaction", "report", "unknown"],
                },
                "period": {
                    "type": "string",
                    "enum": ["day", "week", "month"],
                },
                "transaction": {
                    "type": "object",
                    "properties": {
                        "occurred_at": {"type": "string"},
                        "direction": {
                            "type": "string",
                            "enum": ["income", "expense"],
                        },
                        "amount": {"type": "number"},
                        "expense_type": {
                            "type": "string",
                            "enum": ["daily", "periodic", "one_time"],
                        },
                        "category": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": [
                        "occurred_at",
                        "direction",
                        "amount",
                        "expense_type",
                        "category",
                        "description",
                    ],
                },
            },
            "required": ["action"],
        },
    },
}


def _is_ollama_openai_base(base_url: str) -> bool:
    return ":11434" in base_url.lower()


def _message_text_for_json(message: Any) -> str:
    """Текст ответа для разбора JSON (Ollama/Qwen может класть рассуждения в reasoning)."""
    content = (getattr(message, "content", None) or "").strip()
    if content:
        return content
    extra = getattr(message, "model_extra", None) or {}
    reasoning = getattr(message, "reasoning", None) or extra.get("reasoning") or ""
    if not isinstance(reasoning, str) or not reasoning.strip():
        return ""
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", reasoning):
        try:
            obj, end = decoder.raw_decode(reasoning, match.start())
            if isinstance(obj, dict) and "action" in obj:
                return reasoning[match.start() : end].strip()
        except json.JSONDecodeError:
            continue
    return ""


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self._text_model = settings.llm_text_model
        self._vision_model = settings.llm_vision_model
        self._timeout_seconds = settings.llm_timeout_seconds
        self._max_retries = settings.llm_max_retries
        self._max_receipt_image_bytes = settings.max_receipt_image_bytes
        self._client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self._ollama_mode = _is_ollama_openai_base(settings.llm_base_url)

    async def extract_from_text(
        self,
        user_text: str,
        system_prompt: str,
        history: list[dict[str, str]] | None = None,
    ) -> ExtractionResult:
        logger.debug("LLM text extraction request: %s", user_text[:100])
        messages: list[dict[str, str]] = []
        messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_text})
        parsed = await self._request_structured(
            model=self._text_model,
            messages=messages,
        )
        return ExtractionResult.from_dict(parsed)

    async def extract_from_image(
        self,
        image_bytes: bytes,
        caption: str,
        system_prompt: str,
    ) -> ExtractionResult:
        logger.debug("LLM image extraction request. caption=%s", caption[:100])
        if len(image_bytes) > self._max_receipt_image_bytes:
            raise ValueError("Receipt image is too large")
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": caption or "Извлеки транзакцию из чека"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            },
        ]
        parsed = await self._request_structured(
            model=self._vision_model,
            messages=messages,
        )
        return ExtractionResult.from_dict(parsed)

    async def _request_structured(self, model: str, messages: list[dict]) -> dict:
        response = None
        for attempt in range(self._max_retries + 1):
            try:
                kwargs: dict[str, Any] = {"model": model, "messages": messages}
                if self._ollama_mode:
                    # Ollama: json_schema часто подвисает; Qwen3 — отключить thinking.
                    kwargs["max_tokens"] = 2048
                    kwargs["extra_body"] = {"think": False}
                else:
                    kwargs["response_format"] = _FINANCE_JSON_SCHEMA

                response = await asyncio.wait_for(
                    self._client.chat.completions.create(**kwargs),
                    timeout=self._timeout_seconds,
                )
                break
            except Exception:
                if attempt >= self._max_retries:
                    raise
                await asyncio.sleep(0.3 * (attempt + 1))

        if response is None:
            raise RuntimeError("LLM response is empty")
        choices = getattr(response, "choices", None) or []
        if not choices or choices[0] is None:
            raise RuntimeError("LLM response has no choices")
        message = choices[0].message
        if message is None:
            raise RuntimeError("LLM response has no message")
        content = _message_text_for_json(message) or "{}"
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = (
                cleaned.removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON, snippet=%r", cleaned[:240])
            return {"action": "unknown"}
        if not isinstance(parsed, dict):
            raise ValueError("Structured payload must be an object")
        return parsed
