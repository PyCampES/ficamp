"""ABN AMRO is a Dutch Bank

Even though, ABN operates in more countries, we are only covering the NL branch with xls files.
"""

from decimal import Decimal
import re
from datetime import datetime
from pathlib import Path

import xlrd  # type: ignore
from ficamp.parsers.protocols import Parser
from ficamp.datastructures import Currency, Tx

TRANSACTIONDATE_REGEX = r"(\d{4})(\d{2})(\d{2})"
transactiondate_re = re.compile(TRANSACTIONDATE_REGEX)


def transactiondate_parser(value: str) -> datetime:
    """Parses an ABN string date into a datetime."""
    out = transactiondate_re.match(value)
    if out is None:
        raise ValueError("No proper datetime format")
    year, month, day = out.groups()
    return datetime(int(year), int(month), int(day))


def amount_parser(value: str) -> Decimal:
    """Parses a string into a Decimal."""
    v = value.replace(",", ".")
    return Decimal(v)


class ConceptParser:
    """Parse ABN concepts.

    Concept samples:

    ```
    BEA, Betaalpas                   Hortus Botanicus,PAS172         NR:1W5P01, 30.12.23/17:48        AMSTERDAM
    BEA, Betaalpas                   Gamma Compact,PAS172            NR:7V0GM0, 15.01.24/18:15        AMSTERDAM
    ```

    """

    TRTP_REGEX = r"/(NAME|REMI|CSID)/([^/]+)"
    trtp_re = re.compile(TRTP_REGEX)

    SEPA_REGEX = r"(?m)^[SEPA Overboeking](\w+):\s+(.*)"
    sepa_re = re.compile(SEPA_REGEX)

    def parse_trtp(self, concept: str) -> str:
        """TRTP is a very ugly ugly thing.

        It's a string with a lot of fields separated by slashes.
        """
        matches = self.trtp_re.findall(concept)
        if not matches:
            raise ValueError("[TRTP] No matches found")
        out = "|".join([f"{key}:{value}" for key, value in matches])
        return out

    def parse_sepa(self, concept: str) -> str:
        # matches = self.sepa_re.findall(concept)
        # fields = {}
        # print(matches)
        # for match in matches:
        #     # match is a tuple, we're interested in the second and third elements
        #     key, val = match[1:3]
        #     if key and val:  # Ensure both key and value are not empty
        #         fields[key.strip()] = val.strip()
        # print(fields)
        # payee = fields.get("Naam", "") + (
        #     " " + fields.get("IBAN", "") if fields.get("IBAN") else ""
        # )
        # memo = fields.get("Omschrijving", "")

        match = re.search(r"(?m)^SEPA Overboeking(.*)", concept)
        if not match:
            raise ValueError("[SEPA] No matches found")

        # Split the remaining text into key-value pairs
        pairs = re.findall(r"(?m)^(\w+):\s+(.*)", match.group(1))
        print(pairs)
        # Convert the list of pairs to a dictionary
        # return dict(pairs)
        out = "|".join([f"{key}:{value}" for key, value in pairs])
        return out


class AbnParser(Parser):
    """Parser for ABN AMRO bank statements.

    ABN uses the old `.xls` excel version, and we require xlrd
    to properly parse those kind of files
    """

    def load(self, filename: Path):
        self.book = xlrd.open_workbook(filename)

    def parse(self) -> list[Tx]:
        """ABN XLS parser.

        Columns by index in file:
            0. accountNumber
            1. mutationcode -> currency
            2. transactiondate -> date
            3. valuedate
            4. startsaldo
            5. endsaldo
            6. amount -> Decimal
            7. description -> str
        """
        book = self.book
        sheet = book.sheet_by_index(0)

        txs = []
        for i in range(1, sheet.nrows):
            currency = sheet.cell_value(i, 1)
            date = sheet.cell_value(i, 0)
            amount = sheet.cell_value(i, 6)
            concept = sheet.cell_value(i, 3)
            category = sheet.cell_value(i, 4)

            tx = self.build_transaction(date, amount, currency, concept, category)
            txs.append(tx)
        return txs

    @staticmethod
    def build_transaction(
        date: str,
        amount: str,
        currency: str,
        concept: str,
        category: str,
    ) -> Tx:
        _date = transactiondate_parser(date)
        _amount = amount_parser(amount)
        _currency = Currency(currency)
        return Tx(
            date=_date,
            amount=_amount,
            currency=_currency,
            concept=concept,
            category=category,
            metadata={},
            tags=[],
        )
