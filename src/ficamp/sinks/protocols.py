from enum import Enum
from typing import Protocol

from ficamp.datastructures import Tx


class BaseSinkException(Exception):
    """Base exception for all sink exceptions.

    If your sink function is going to raise an exception, it should inherit from this class.
    """

    pass


class SinkProtocol(Protocol):
    def write(self, transations: list[Tx]): ...
