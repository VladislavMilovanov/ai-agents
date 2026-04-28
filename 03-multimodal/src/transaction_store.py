from datetime import datetime, timedelta

from src.transaction import Transaction


class TransactionStore:
    def __init__(self) -> None:
        self._store: dict[int, list[Transaction]] = {}

    def add(self, user_id: int, transaction: Transaction) -> None:
        self._store.setdefault(user_id, []).append(transaction)

    def list_for_user(self, user_id: int) -> list[Transaction]:
        return list(self._store.get(user_id, []))

    def list_by_period(
        self, user_id: int, period: str, now: datetime | None = None
    ) -> list[Transaction]:
        now_dt = now or datetime.now()
        if period == "day":
            start = now_dt - timedelta(days=1)
        elif period == "week":
            start = now_dt - timedelta(days=7)
        else:
            start = now_dt - timedelta(days=30)
        return [tx for tx in self.list_for_user(user_id) if tx.occurred_at >= start]
