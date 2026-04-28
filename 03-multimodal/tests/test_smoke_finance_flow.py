from datetime import datetime

import pytest

from src.chat_service import ChatService
from src.extraction_result import ExtractionResult
from src.transaction import Transaction
from src.transaction_store import TransactionStore


class FakeLLMClient:
    def __init__(self) -> None:
        self._step = 0

    async def extract_from_text(
        self, user_text: str, system_prompt: str, history: list[dict[str, str]] | None = None
    ) -> ExtractionResult:
        self._step += 1
        if self._step == 1:
            return ExtractionResult(
                action="transaction",
                transaction=Transaction(
                    occurred_at=datetime(2026, 4, 28, 10, 30),
                    direction="income",
                    amount=70000,
                    expense_type="one_time",
                    category="зарплата",
                    description="Апрельская зарплата",
                ),
            )
        if self._step == 2:
            return ExtractionResult(
                action="transaction",
                transaction=Transaction(
                    occurred_at=datetime(2026, 4, 28, 18, 0),
                    direction="expense",
                    amount=3200,
                    expense_type="daily",
                    category="продукты",
                    description="Покупка в магазине",
                ),
            )
        return ExtractionResult(action="report", period="month")

    async def extract_from_image(
        self, image_bytes: bytes, caption: str, system_prompt: str
    ) -> ExtractionResult:
        raise NotImplementedError


@pytest.mark.asyncio
async def test_smoke_income_expense_report_flow() -> None:
    service = ChatService(FakeLLMClient(), transaction_store=TransactionStore())

    first = await service.handle_text(1, "Получил зарплату")
    second = await service.handle_text(1, "Потратил на продукты")
    report = await service.handle_text(1, "Покажи отчет за месяц")

    assert "Транзакция сохранена" in first
    assert "Транзакция сохранена" in second
    assert "Отчет за месяц" in report
    assert "Доходы: 70000.00" in report
    assert "Расходы: 3200.00" in report
