from unittest.mock import AsyncMock

import pytest

from src.chat_service import FALLBACK_MESSAGE, ChatService
from src.dialog_history import DialogHistory
from src.llm_client import LLMClient

USER_ID = 42


@pytest.fixture
def llm_mock() -> LLMClient:
    return AsyncMock(spec=LLMClient)


@pytest.mark.asyncio
async def test_handle_returns_llm_answer(llm_mock: LLMClient) -> None:
    llm_mock.ask.return_value = "Ответ от модели"  # type: ignore[attr-defined]
    service = ChatService(llm_mock, system_prompt="Ты ассистент")

    result = await service.handle(USER_ID, "Привет")

    assert result == "Ответ от модели"
    llm_mock.ask.assert_awaited_once_with(  # type: ignore[attr-defined]
        "Привет", system_prompt="Ты ассистент", history=[]
    )


@pytest.mark.asyncio
async def test_handle_returns_fallback_on_llm_error(llm_mock: LLMClient) -> None:
    llm_mock.ask.side_effect = RuntimeError("API недоступен")  # type: ignore[attr-defined]
    service = ChatService(llm_mock)

    result = await service.handle(USER_ID, "Любой текст")

    assert result == FALLBACK_MESSAGE


@pytest.mark.asyncio
async def test_handle_accumulates_history(llm_mock: LLMClient) -> None:
    llm_mock.ask.return_value = "Ответ"  # type: ignore[attr-defined]
    history = DialogHistory(limit=10)
    service = ChatService(llm_mock, history=history)

    await service.handle(USER_ID, "Первый вопрос")
    await service.handle(USER_ID, "Второй вопрос")

    saved = history.get(USER_ID)
    assert len(saved) == 4
    assert saved[0] == {"role": "user", "content": "Первый вопрос"}
    assert saved[1] == {"role": "assistant", "content": "Ответ"}
    assert saved[2] == {"role": "user", "content": "Второй вопрос"}

    second_call_history = llm_mock.ask.call_args_list[1].kwargs["history"]  # type: ignore[attr-defined]
    assert len(second_call_history) == 2
