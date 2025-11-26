from enum import Enum
from typing import Literal, Iterable

from phaast.structure.constants import AtomicNumber

class FilterMode(Enum):
    NONE = 0
    INCLUDE = 1
    EXCLUDE = 2

class FilterList(dict[tuple[AtomicNumber, AtomicNumber], Literal[True]]):
    mode: FilterMode

    #@check_types
    def __init__(
        self,
        mode: FilterMode,
        bondings: Iterable[tuple[AtomicNumber, AtomicNumber]],
    ):
        self.mode = mode

        super().__init__()
        for i, j in bondings:
            self[(i, j)] = True
            self[(j, i)] = True

    def is_permited(self, zi: AtomicNumber, zj: AtomicNumber):
        match self.mode:
            case FilterMode.INCLUDE:
                return (zi, zj) in self
            case FilterMode.EXCLUDE:
                return (zi, zj) not in self
            case FilterMode.NONE:
                return True
