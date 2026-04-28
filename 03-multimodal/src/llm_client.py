import asyncio
import base64
import json
import logging

from openai import AsyncOpenAI

from src.config import Settings
from src.extraction_result import ExtractionResult

logger = logging.getLogger(__name__)


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
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(
                        model=model,
                        messages=messages,
                        response_format={
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
                        },
                    ),
                    timeout=self._timeout_seconds,
                )
                break
            except Exception:
                if attempt >= self._max_retries:
                    raise
                await asyncio.sleep(0.3 * (attempt + 1))

        if response is None:
            raise RuntimeError("LLM response is empty")
        content = response.choices[0].message.content or "{}"
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = (
                cleaned.removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise ValueError("Structured payload must be an object")
        return parsed
