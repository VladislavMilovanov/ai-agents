from datetime import datetime, timedelta

from src.transaction import Transaction
from src.transaction_store import TransactionStore


def _tx(hours_ago: int, amount: float) -> Transaction:
    return Transaction(
        occurred_at=datetime.now() - timedelta(hours=hours_ago),
        direction="expense",
        amount=amount,
        expense_type="daily",
        category="продукты",
        description="Покупка",
    )


def test_list_by_period_filters_items() -> None:
    store = TransactionStore()
    user_id = 1
    store.add(user_id, _tx(hours_ago=2, amount=100))
    store.add(user_id, _tx(hours_ago=72, amount=200))

    day_items = store.list_by_period(user_id, period="day")
    month_items = store.list_by_period(user_id, period="month")

    assert len(day_items) == 1
    assert len(month_items) == 2
