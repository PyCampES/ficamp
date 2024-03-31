from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


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
class Tx(SQLModel, table=True):
    """Represents a transaction extracted from a bank"""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime
    amount: Decimal
    currency: Currency
    concept: str
    category: None | str
    tx_metadata: dict[str, str] = Field(sa_column=Column(JSON))
    tags: list[str] = Field(sa_column=Column(JSON))
