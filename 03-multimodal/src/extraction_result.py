from dataclasses import dataclass
from datetime import datetime, timezone

from src.transaction import Transaction

ALLOWED_ACTIONS = {"transaction", "report", "unknown"}
ALLOWED_PERIODS = {"day", "week", "month"}


def _parse_occurred_at(raw: str) -> datetime:
    s = raw.strip()
    if not s:
        return datetime.now().replace(microsecond=0)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        try:
            dt = datetime.strptime(s, "%Y-%m-%d")
            return dt.replace(hour=12, minute=0, second=0, microsecond=0)
        except ValueError:
            return datetime.now().replace(microsecond=0)
    if "T" not in s and " " in s:
        s = s.replace(" ", "T", 1)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
        except ValueError:
            return datetime.now().replace(microsecond=0)
        return dt.replace(hour=12, minute=0, second=0, microsecond=0)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.replace(microsecond=0)


def _normalize_direction(raw: str) -> str:
    key = raw.strip().lower()
    mapping = {
        "income": "income",
        "expense": "expense",
        "доход": "income",
        "расход": "expense",
        "приход": "income",
    }
    if key in mapping:
        return mapping[key]
    low = raw.lower()
    if "доход" in raw or "income" in low or "приход" in raw:
        return "income"
    return "expense"


def _normalize_expense_type(raw: str) -> str:
    key = raw.strip().lower().replace(" ", "_").replace("-", "_")
    mapping = {
        "daily": "daily",
        "periodic": "periodic",
        "one_time": "one_time",
        "onetime": "one_time",
        "разовый": "one_time",
        "разовая": "one_time",
        "подписка": "periodic",
        "ежемесячный": "periodic",
        "ежемесячная": "periodic",
        "регулярный": "periodic",
        "регулярная": "periodic",
    }
    if key in mapping:
        return mapping[key]
    low = raw.lower()
    if "подпис" in low or "period" in low or "ежемеся" in low:
        return "periodic"
    if "разов" in low or "one" in low:
        return "one_time"
    return "daily"


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
        if not isinstance(tx_data, dict):
            return cls(action="unknown")

        try:
            occurred_at = _parse_occurred_at(str(tx_data.get("occurred_at", "")))
            direction = _normalize_direction(str(tx_data.get("direction", "expense")))
            amount = float(tx_data.get("amount", 0))
            expense_type = _normalize_expense_type(str(tx_data.get("expense_type", "daily")))
            category = str(tx_data.get("category", "other")).strip() or "прочее"
            description = str(tx_data.get("description", "")).strip()
            transaction = Transaction(
                occurred_at=occurred_at,
                direction=direction,
                amount=amount,
                expense_type=expense_type,
                category=category,
                description=description,
            )
        except (ValueError, TypeError):
            return cls(action="unknown")

        return cls(action=action, transaction=transaction)
