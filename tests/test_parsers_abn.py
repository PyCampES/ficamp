from datetime import datetime
from decimal import Decimal

import pytest
from ficamp.parsers.abn import (
    ConceptParser,
    amount_parser,
    transactiondate_parser,
)


@pytest.mark.parametrize(
    "input, expected",
    [
        ["20210101", datetime(2021, 1, 1)],
        ["20231231", datetime(2023, 12, 31)],
        ["20240101", datetime(2024, 1, 1)],
        ["20240102", datetime(2024, 1, 2)],
        ["20240103", datetime(2024, 1, 3)],
        ["20240104", datetime(2024, 1, 4)],
        ["20240105", datetime(2024, 1, 5)],
        ["19950620", datetime(1995, 6, 20)],
    ],
)
def test_transactiondate_parser_ok(input: str, expected: datetime):
    d = transactiondate_parser(input)
    assert d == expected


@pytest.mark.parametrize("inputs", ["2021-01-01", "holis", "202523434"])
def test_transactiondate_parser_raises(inputs: str):
    with pytest.raises(ValueError):
        transactiondate_parser("2021-01-01")


@pytest.mark.parametrize(
    "input, expected",
    [
        ["-40,50", Decimal("-40.50")],
        ["-1,5", Decimal("-1.5")],
    ],
)
def test_amount_parser_ok(input: str, expected: Decimal):
    out = amount_parser(input)
    assert out == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            "/TRTP/SEPA OVERBOEKING/IBAN/XXXXXX/BIC/ABNANL2A/NAME/R DE JONG/EREF/NOTPROVIDED",
            "NAME:R DE JONG",
        ],
    ],
)
def test_parse_trtp_ok(input: str, expected: str):
    out = ConceptParser().parse_trtp(input)
    assert out == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            "SEPA Overboeking                 IBAN: XXXXX        BIC: ABNANL2A                    Naam: ABN AMRO INZAKE GELDMAAT  Omschrijving: Storting 12-01-24  15:36 uur, Pas 172              Geldautomaat 812936              1053EK Amsterdam                Kenmerk: 401215363553",
            "R DE JONG",
        ],
    ],
)
def test_parse_sepa_ok(input: str, expected: str):
    out = ConceptParser().parse_sepa(input)
    {
        "IBAN": "XXXXX",
        "BIC": "ABNANL2A",
        "Naam": "ABN AMRO INZAKE GELDMAAT",
        "Omschrijving": "Storting 12-01-24 1536 uur, Pas 172 Geldautomaat 812936              1053EK Amsterdam",
        "Kenmerk": "401215363553",
    }
    assert out == expected
