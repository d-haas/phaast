from enum import Enum
from typing import Literal, Iterable

from phaast.structure.constants import AtomicNumber
from phaast.utils import JsonType

class FilterMode(Enum):
    NONE = 0
    INCLUDE = 1
    EXCLUDE = 2

class FilterList(dict[tuple[AtomicNumber, AtomicNumber], Literal[True]]):
    mode: FilterMode

    def __init__(self, mode: FilterMode, bondings: Iterable[tuple[AtomicNumber, AtomicNumber]]): ...

    def is_permited(self, zi: AtomicNumber, zj: AtomicNumber) -> bool: ...

    def as_data(self) -> dict[str, JsonType]: ...
