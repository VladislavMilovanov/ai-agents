from datetime import datetime

from src.extraction_result import ExtractionResult


def test_from_dict_builds_transaction() -> None:
    payload = {
        "action": "transaction",
        "transaction": {
            "occurred_at": "2026-04-28T10:30:00",
            "direction": "expense",
            "amount": 1500,
            "expense_type": "daily",
            "category": "продукты",
            "description": "Покупка",
        },
    }

    result = ExtractionResult.from_dict(payload)

    assert result.action == "transaction"
    assert result.transaction is not None
    assert result.transaction.occurred_at == datetime(2026, 4, 28, 10, 30)


def test_from_dict_normalizes_invalid_action_and_period() -> None:
    payload = {"action": "other", "period": "year"}

    result = ExtractionResult.from_dict(payload)

    assert result.action == "unknown"
    assert result.period == "month"


def test_from_dict_invalid_transaction_becomes_unknown() -> None:
    payload = {
        "action": "transaction",
        "transaction": {
            "occurred_at": "2026-04-28T10:30:00",
            "direction": "expense",
            "amount": 0,
            "expense_type": "daily",
            "category": "продукты",
            "description": "Покупка",
        },
    }

    result = ExtractionResult.from_dict(payload)

    assert result.action == "unknown"
    assert result.transaction is None


def test_from_dict_accepts_russian_direction() -> None:
    payload = {
        "action": "transaction",
        "transaction": {
            "occurred_at": "2026-04-28T10:30:00",
            "direction": "расход",
            "amount": 100,
            "expense_type": "daily",
            "category": "продукты",
            "description": "хлеб",
        },
    }

    result = ExtractionResult.from_dict(payload)

    assert result.action == "transaction"
    assert result.transaction is not None
    assert result.transaction.direction == "expense"
