from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Tx:
    """Represents a transaction extracted from a bank"""

    date: datetime
    amount: Decimal
    currency: str
    concept: str
    category: None | str
    metadata: dict[str, str]
    tags: list[str]
