from pathlib import Path
from typing import Protocol

from ficamp.datastructures import Tx


class Parser(Protocol):
    """Main protocol to define parsers for different banks."""

    def load(self, filename: Path): ...

    def parse(self) -> list[Tx]: ...
