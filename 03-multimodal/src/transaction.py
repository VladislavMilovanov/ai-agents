from dataclasses import dataclass
from datetime import datetime

ALLOWED_DIRECTIONS = {"income", "expense"}
ALLOWED_EXPENSE_TYPES = {"daily", "periodic", "one_time"}


@dataclass(slots=True)
class Transaction:
    occurred_at: datetime
    direction: str
    amount: float
    expense_type: str
    category: str
    description: str

    def __post_init__(self) -> None:
        if self.direction not in ALLOWED_DIRECTIONS:
            raise ValueError(f"Unsupported direction: {self.direction}")
        if self.expense_type not in ALLOWED_EXPENSE_TYPES:
            raise ValueError(f"Unsupported expense_type: {self.expense_type}")
        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if not self.category.strip():
            raise ValueError("Category must not be empty")
        if not self.description.strip():
            raise ValueError("Description must not be empty")
