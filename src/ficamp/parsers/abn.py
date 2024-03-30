from pathlib import Path
from src.ficamp.parsers.protocol import Parser
from src.ficamp.types import Tx
import xlrd


class AbnParser(Parser):
    """Parser for ABN AMRO bank statements."""

    def load(self, filename: Path):
        self.data = xlrd.open_workbook("samples/santi-txs.xls")


    def parse(self) -> list[Tx]:
        sheet = self.data.sheet_by_index(0)
        txs = []
        for i in range(1, sheet.nrows):
            date = xlrd.xldate_as_datetime(sheet.cell_value(i, 0), self.data.datemode)
            amount = sheet.cell_value(i, 1)
            currency = sheet.cell_value(i, 2)
            concept = sheet.cell_value(i, 3)
            category = sheet.cell_value(i, 4)
            metadata = {}
            tags = []
            tx = Tx(date, amount, currency, concept, category, metadata, tags)
            txs.append(tx)
        return txs