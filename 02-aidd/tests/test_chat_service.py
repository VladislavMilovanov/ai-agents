from unittest.mock import AsyncMock

import pytest

from src.chat_service import FALLBACK_MESSAGE, ChatService
from src.llm_client import LLMClient


@pytest.fixture
def llm_mock() -> LLMClient:
    mock = AsyncMock(spec=LLMClient)
    return mock


@pytest.mark.asyncio
async def test_handle_returns_llm_answer(llm_mock: LLMClient) -> None:
    llm_mock.ask.return_value = "Ответ от модели"  # type: ignore[attr-defined]
    service = ChatService(llm_mock, system_prompt="Ты ассистент")

    result = await service.handle("Привет")

    assert result == "Ответ от модели"
    llm_mock.ask.assert_awaited_once_with("Привет", system_prompt="Ты ассистент")  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_handle_returns_fallback_on_llm_error(llm_mock: LLMClient) -> None:
    llm_mock.ask.side_effect = RuntimeError("API недоступен")  # type: ignore[attr-defined]
    service = ChatService(llm_mock)

    result = await service.handle("Любой текст")

    assert result == FALLBACK_MESSAGE
