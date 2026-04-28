from dataclasses import dataclass
from datetime import datetime

from src.transaction import Transaction

ALLOWED_ACTIONS = {"transaction", "report", "unknown"}
ALLOWED_PERIODS = {"day", "week", "month"}


@dataclass(slots=True)
class ExtractionResult:
    action: str
    transaction: Transaction | None = None
    period: str = "month"

    @classmethod
    def from_dict(cls, payload: dict) -> "ExtractionResult":
        action = str(payload.get("action", "unknown"))
        if action not in ALLOWED_ACTIONS:
            action = "unknown"
        if action != "transaction":
            period = str(payload.get("period", "month"))
            if period not in ALLOWED_PERIODS:
                period = "month"
            return cls(action=action, period=period)

        tx_data = payload.get("transaction") or {}
        occurred_at_raw = str(tx_data.get("occurred_at", ""))
        occurred_at = datetime.fromisoformat(occurred_at_raw)
        transaction = Transaction(
            occurred_at=occurred_at,
            direction=str(tx_data.get("direction", "expense")),
            amount=float(tx_data.get("amount", 0)),
            expense_type=str(tx_data.get("expense_type", "one_time")),
            category=str(tx_data.get("category", "other")),
            description=str(tx_data.get("description", "")),
        )
        return cls(action=action, transaction=transaction)
