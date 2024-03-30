from pathlib import Path
from types import Tx
from typing import Protocol


class Parser(Protocol):
    """Main protocol to define parsers for different banks."""

    def load(self, filename: Path): ...

    def parse(self) -> list[Tx]: ...
