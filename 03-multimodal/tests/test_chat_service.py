from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.chat_service import (
    FALLBACK_MESSAGE,
    UNSUPPORTED_INPUT_MESSAGE,
    ChatService,
)
from src.dialog_history import DialogHistory
from src.extraction_result import ExtractionResult
from src.llm_client import LLMClient
from src.transaction import Transaction
from src.transaction_store import TransactionStore

USER_ID = 42


@pytest.fixture
def llm_mock() -> LLMClient:
    return AsyncMock(spec=LLMClient)


@pytest.mark.asyncio
async def test_handle_text_saves_transaction(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_text.return_value = ExtractionResult(  # type: ignore[attr-defined]
        action="transaction",
        transaction=Transaction(
            occurred_at=datetime(2026, 4, 28, 10, 30),
            direction="expense",
            amount=1250.0,
            expense_type="daily",
            category="продукты",
            description="Пятерочка",
        ),
    )
    store = TransactionStore()
    service = ChatService(llm_mock, system_prompt="Ты ассистент")
    service = ChatService(llm_mock, system_prompt="Ты ассистент", transaction_store=store)

    result = await service.handle_text(USER_ID, "Купил продукты")

    assert "Транзакция сохранена" in result
    assert len(store.list_for_user(USER_ID)) == 1


@pytest.mark.asyncio
async def test_handle_text_returns_fallback_on_llm_error(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_text.side_effect = RuntimeError("API недоступен")  # type: ignore[attr-defined]
    service = ChatService(llm_mock)

    result = await service.handle_text(USER_ID, "Любой текст")

    assert result == FALLBACK_MESSAGE


@pytest.mark.asyncio
async def test_handle_text_returns_report(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_text.side_effect = [  # type: ignore[attr-defined]
        ExtractionResult(
            action="transaction",
            transaction=Transaction(
                occurred_at=datetime(2026, 4, 28, 10, 30),
                direction="income",
                amount=50000.0,
                expense_type="one_time",
                category="зарплата",
                description="ЗП",
            ),
        ),
        ExtractionResult(
            action="transaction",
            transaction=Transaction(
                occurred_at=datetime(2026, 4, 28, 12, 0),
                direction="expense",
                amount=2000.0,
                expense_type="daily",
                category="продукты",
                description="Магазин",
            ),
        ),
        ExtractionResult(action="report", period="month"),
    ]
    service = ChatService(llm_mock, transaction_store=TransactionStore())

    await service.handle_text(USER_ID, "Получил зарплату")
    await service.handle_text(USER_ID, "Купил продукты")
    report = await service.handle_text(USER_ID, "Покажи отчет за месяц")

    assert "Отчет за месяц" in report
    assert "Транзакций: 2" in report
    assert "Доходы: 50000.00" in report
    assert "Расходы: 2000.00" in report
    assert "Категории расходов" in report


@pytest.mark.asyncio
async def test_handle_text_unknown_action(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_text.return_value = ExtractionResult(action="unknown")  # type: ignore[attr-defined]
    service = ChatService(llm_mock)

    result = await service.handle_text(USER_ID, "Привет")

    assert result == UNSUPPORTED_INPUT_MESSAGE


@pytest.mark.asyncio
async def test_handle_text_accumulates_history(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_text.return_value = ExtractionResult(action="unknown")  # type: ignore[attr-defined]
    history = DialogHistory(limit=10)
    service = ChatService(llm_mock, history=history)

    await service.handle_text(USER_ID, "Первый вопрос")
    await service.handle_text(USER_ID, "Второй вопрос")

    saved = history.get(USER_ID)
    assert len(saved) == 4
    assert saved[0] == {"role": "user", "content": "Первый вопрос"}
    assert saved[1] == {"role": "assistant", "content": UNSUPPORTED_INPUT_MESSAGE}
    assert saved[2] == {"role": "user", "content": "Второй вопрос"}

    second_call_history = llm_mock.extract_from_text.call_args_list[1].kwargs["history"]  # type: ignore[attr-defined]
    assert len(second_call_history) == 2


@pytest.mark.asyncio
async def test_handle_image_returns_fallback_on_error(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_image.side_effect = RuntimeError("VLM down")  # type: ignore[attr-defined]
    service = ChatService(llm_mock)

    result = await service.handle_image(USER_ID, b"img")

    assert result == FALLBACK_MESSAGE


@pytest.mark.asyncio
async def test_handle_image_saves_transaction(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_image.return_value = ExtractionResult(  # type: ignore[attr-defined]
        action="transaction",
        transaction=Transaction(
            occurred_at=datetime(2026, 4, 28, 19, 10),
            direction="expense",
            amount=890.0,
            expense_type="daily",
            category="кафе",
            description="Чек из кофейни",
        ),
    )
    store = TransactionStore()
    service = ChatService(llm_mock, transaction_store=store)

    result = await service.handle_image(USER_ID, b"fake-jpeg-bytes", caption="чек")

    assert "Транзакция сохранена" in result
    assert len(store.list_for_user(USER_ID)) == 1


@pytest.mark.asyncio
async def test_handle_image_returns_validation_message_on_value_error(
    llm_mock: LLMClient,
) -> None:
    llm_mock.extract_from_image.side_effect = ValueError("too large")  # type: ignore[attr-defined]
    service = ChatService(llm_mock)

    result = await service.handle_image(USER_ID, b"img")

    assert "Не удалось обработать изображение" in result


@pytest.mark.asyncio
async def test_handle_text_uses_context_for_clarification(llm_mock: LLMClient) -> None:
    llm_mock.extract_from_text.side_effect = [  # type: ignore[attr-defined]
        ExtractionResult(action="unknown"),
        ExtractionResult(
            action="transaction",
            transaction=Transaction(
                occurred_at=datetime(2026, 4, 28, 20, 15),
                direction="expense",
                amount=450.0,
                expense_type="daily",
                category="кафе",
                description="Кофе и десерт",
            ),
        ),
    ]
    history = DialogHistory(limit=10)
    store = TransactionStore()
    service = ChatService(llm_mock, history=history, transaction_store=store)

    first = await service.handle_text(USER_ID, "Купил кофе")
    second = await service.handle_text(USER_ID, "Это было в кафе")

    assert first == UNSUPPORTED_INPUT_MESSAGE
    assert "Транзакция сохранена" in second
    assert len(store.list_for_user(USER_ID)) == 1
    second_call_history = llm_mock.extract_from_text.call_args_list[1].kwargs["history"]  # type: ignore[attr-defined]
    assert len(second_call_history) == 2
