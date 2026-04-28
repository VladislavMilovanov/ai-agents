from src.transaction import Transaction


class BalanceReportService:
    def build(self, period: str, items: list[Transaction]) -> str:
        period_title = {
            "day": "день",
            "week": "неделю",
            "month": "месяц",
        }.get(period, "период")
        income = sum(tx.amount for tx in items if tx.direction == "income")
        expense = sum(tx.amount for tx in items if tx.direction == "expense")
        balance = income - expense

        categories: dict[str, float] = {}
        for tx in items:
            if tx.direction != "expense":
                continue
            categories[tx.category] = categories.get(tx.category, 0.0) + tx.amount

        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        category_lines = (
            "\n".join(f"- {name}: {amount:.2f}" for name, amount in top_categories[:5])
            if top_categories
            else "- Нет расходов в выбранном периоде"
        )

        return (
            f"Отчет за {period_title}:\n"
            f"- Транзакций: {len(items)}\n"
            f"- Доходы: {income:.2f}\n"
            f"- Расходы: {expense:.2f}\n"
            f"- Баланс: {balance:.2f}\n"
            "Категории расходов:\n"
            f"{category_lines}"
        )
