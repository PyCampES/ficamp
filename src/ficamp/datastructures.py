from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class Currency(StrEnum):
    EUR = "EUR"
    USD = "USD"


@dataclass
class Tx:
    """Represents a transaction extracted from a bank"""

    date: datetime
    amount: Decimal
    currency: Currency
    concept: str
    category: None | str
    metadata: dict[str, str]
    tags: list[str]
