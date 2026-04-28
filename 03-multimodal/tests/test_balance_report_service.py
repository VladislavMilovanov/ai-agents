from datetime import datetime

import pytest

from src.balance_report_service import BalanceReportService
from src.transaction import Transaction


def test_build_report_contains_totals_and_categories() -> None:
    service = BalanceReportService()
    items = [
        Transaction(
            occurred_at=datetime(2026, 4, 28, 10, 30),
            direction="income",
            amount=10000,
            expense_type="one_time",
            category="зарплата",
            description="ЗП",
        ),
        Transaction(
            occurred_at=datetime(2026, 4, 28, 12, 00),
            direction="expense",
            amount=2500,
            expense_type="daily",
            category="продукты",
            description="Магазин",
        ),
    ]

    report = service.build("month", items)

    assert "Отчет за месяц" in report
    assert "Транзакций: 2" in report
    assert "Доходы: 10000.00" in report
    assert "Расходы: 2500.00" in report
    assert "- продукты: 2500.00" in report


@pytest.mark.parametrize(
    ("period", "title"),
    [
        ("day", "Отчет за день"),
        ("week", "Отчет за неделю"),
        ("month", "Отчет за месяц"),
    ],
)
def test_build_report_has_expected_period_title(period: str, title: str) -> None:
    service = BalanceReportService()
    report = service.build(period, [])

    assert title in report
