from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class Currency(StrEnum):
    EUR = "EUR"
    USD = "USD"


@dataclass
class Concept:
    """This class represent a potential match or the raw concept.

    The parser may try to generate the `best_concept_match` from the raw concept.
    If the `best_concept_match` is not useful for the categorizer, it can choose
    to use the raw concept instead.
    """

    best_concept_match: str
    raw: str


@dataclass
class Tx:
    """Represents a transaction extracted from a bank"""

    date: datetime
    amount: Decimal
    currency: Currency
    concept: str | Concept
    category: None | str
    metadata: dict[str, str]
    tags: list[str]
