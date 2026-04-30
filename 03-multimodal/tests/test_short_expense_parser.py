import pytest

from src.short_expense_parser import try_parse_short_expense


@pytest.mark.parametrize(
    "text,amount,desc_snip,category",
    [
        ("100 р хлеб", 100.0, "хлеб", "продукты"),
        ("100р хлеб", 100.0, "хлеб", "продукты"),
        ("12,50 р кофе", 12.5, "кофе", "продукты"),
        ("99 руб такси до дома", 99.0, "такси до дома", "транспорт"),
        ("50 ₽ на обед", 50.0, "обед", "рестораны"),
    ],
)
def test_parse_short_expense_ok(
    text: str, amount: float, desc_snip: str, category: str
) -> None:
    r = try_parse_short_expense(text)
    assert r is not None
    assert r.action == "transaction"
    assert r.transaction is not None
    assert r.transaction.amount == amount
    assert r.transaction.direction == "expense"
    assert desc_snip in r.transaction.description
    assert r.transaction.category == category


def test_parse_short_expense_rejects_empty_description() -> None:
    assert try_parse_short_expense("100 р ") is None
    assert try_parse_short_expense("100 р") is None


def test_parse_short_expense_rejects_non_matching() -> None:
    assert try_parse_short_expense("потратил 100 р на хлеб") is None
    assert try_parse_short_expense("") is None
