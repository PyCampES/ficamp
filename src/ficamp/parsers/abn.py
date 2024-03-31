"""ABN AMRO is a Dutch Bank

Even though, ABN operates in more countries, we are only covering the NL branch with xls files.
"""

import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import xlrd  # type: ignore

from ficamp.datastructures import Currency, Tx
from ficamp.parsers.protocols import Parser

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
    SEPA Overboeking                 IBAN: XXXXX        BIC: ABNANL2A                    Naam: ABN AMRO INZAKE GELDMAAT  Omschrijving: Storting 12-01-24  15:36 uur, Pas 172              Geldautomaat 812936              1053EK Amsterdam                Kenmerk: 401215363553
    ```

    """

    TRTP_REGEX = r"/(NAME|REMI|CSID)/([^/]+)"
    trtp_re = re.compile(TRTP_REGEX)

    SEPA_REGEX = r"Naam:\s(.*)\s{2,}Omschrijving:\s(.*)"
    sepa_re = re.compile(SEPA_REGEX)

    BEA_REGEX = r"(\s{2,})(.+?),PAS\d+\s+\S+\s+\S+\s+(\w+)"
    bea_re = re.compile(BEA_REGEX)

    def parse(self, concept: str) -> str:
        parsers = {
            "DEPOSIT INV": self.parse_deposit_inv,
            "BEA": self.parse_bea_gea,
            "GEA": self.parse_bea_gea,
            "/TRTP": self.parse_trtp,
            "ABN": self.parse_abn,
            "SEPA": self.parse_sepa,
            "KOOP": self.parse_abn,
        }
        for key, parser in parsers.items():
            if concept.startswith(key):
                # print(f"Using {parser}")
                try:
                    return parser(concept)
                except ValueError:
                    continue

        return "UNKNOWN"

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
        matches = self.sepa_re.search(concept)
        if not matches:
            raise ValueError("[SEPA] No matches found")
        out = "|".join(["SEPA"] + list(matches.groups()))
        return out

    def parse_bea_gea(self, concept: str) -> str:
        match = self.bea_re.search(concept)
        if not match:
            raise ValueError("[BEA/GEA] No matches found")
        return f"{match.group(2)}|{match.group(3)}"

    def parse_deposit_inv(self, concept: str) -> str:
        return "Investments ABN|" + concept

    def parse_abn(self, concept: str) -> str:
        return "ABN AMRO|" + concept


class AbnParser(Parser):
    """Parser for ABN AMRO bank statements.

    ABN uses the old `.xls` excel version, and we require xlrd
    to properly parse those kind of files
    """

    def __init__(self):
        self.concept_parser = ConceptParser()

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
            date = str(sheet.cell_value(i, 2))
            amount = str(sheet.cell_value(i, 6))
            concept = sheet.cell_value(i, 7)
            print("currency", currency)
            print("date", date)
            print("amount", amount)
            print("concept", concept)
            tx = self.build_transaction(date, amount, currency, concept)
            txs.append(tx)
        return txs

    def build_transaction(
        self,
        date: str,
        amount: str,
        currency: str,
        concept: str,
    ) -> Tx:
        _date = transactiondate_parser(date)
        _amount = amount_parser(amount)
        _currency = Currency(currency)

        _concept = self.concept_parser.parse(concept)

        return Tx(
            date=_date,
            amount=_amount,
            currency=_currency,
            concept=_concept,
            category=None,
            tx_metadata={},
            tags=[],
        )
