"""Разбор очень коротких сообщений о расходе без LLM («100 р хлеб»)."""

import re
from datetime import datetime

from src.extraction_result import ExtractionResult
from src.transaction import Transaction

_SHORT_EXPENSE = re.compile(
    r"^\s*(\d+(?:[.,]\d+)?)\s*(?:р\.?|руб\.?|рублей|rub|₽)\s*(?:на\s+)?(.+?)\s*$",
    re.IGNORECASE | re.UNICODE,
)


def _guess_category(description: str) -> str:
    d = description.lower()
    if any(
        w in d
        for w in (
            "хлеб",
            "молоко",
            "кофе",
            "продукт",
            "магазин",
            "пятёрочка",
            "перекрёсток",
            "еда",
            "овощ",
            "фрукт",
            "мясо",
        )
    ):
        return "продукты"
    if any(w in d for w in ("такси", "uber", "яндекс", "bolt")):
        return "транспорт"
    if any(w in d for w in ("кафе", "ресторан", "обед", "ужин")):
        return "рестораны"
    return "прочее"


def try_parse_short_expense(text: str) -> ExtractionResult | None:
    """
    Если строка — сумма в рублях и короткое описание, вернуть transaction.
    Иначе None (дальше пусть решает LLM).
    """
    raw = text.strip()
    if not raw or len(raw) > 200:
        return None
    m = _SHORT_EXPENSE.match(raw)
    if not m:
        return None
    amount_str, description = m.group(1), m.group(2).strip()
    if not description:
        return None
    try:
        amount = float(amount_str.replace(",", "."))
    except ValueError:
        return None
    if amount <= 0:
        return None

    now = datetime.now().replace(microsecond=0)
    tx = Transaction(
        occurred_at=now,
        direction="expense",
        amount=amount,
        expense_type="daily",
        category=_guess_category(description),
        description=description,
    )
    return ExtractionResult(action="transaction", transaction=tx)
