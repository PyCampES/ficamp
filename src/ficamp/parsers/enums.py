from enum import StrEnum

from ficamp.parsers.abn import AbnParser
from ficamp.parsers.bbva import AccountBBVAParser, CreditCardBBVAParser
from ficamp.parsers.bsabadell import AccountBSabadellParser, CreditCardBSabadellParser
from ficamp.parsers.caixabank import CaixaBankParser


class BankParser(StrEnum):
    ABN = "abn"
    BBVA_ACCOUNT = "bbva-account"
    BBVA_CREDIT = "bbva-credit"
    BSABADELL_ACCOUNT = "bsabadell-account"
    BSABADELL_CREDIT = "bsabadell-credit"
    CAIXABANK = "caixabank"

    def get_parser(self):
        if self == BankParser.ABN:
            return AbnParser()
        if self == BankParser.BBVA_ACCOUNT:
            return AccountBBVAParser()
        if self == BankParser.BBVA_CREDIT:
            return CreditCardBBVAParser()
        if self == BankParser.BSABADELL_ACCOUNT:
            return AccountBSabadellParser()
        if self == BankParser.BSABADELL_CREDIT:
            return CreditCardBSabadellParser()
        if self == BankParser.CAIXABANK:
            return CaixaBankParser()
