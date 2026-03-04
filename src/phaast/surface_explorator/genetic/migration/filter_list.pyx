from typing import Literal, Iterable

from phaast.structure.constants import AtomicNumber

cpdef enum FilterMode:
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

    def is_permited(self, zi: AtomicNumber, zj: AtomicNumber) -> bool:
        if self.mode == FilterMode.INCLUDE:
            return (zi, zj) in self
        elif self.mode == FilterMode.EXCLUDE:
            return (zi, zj) not in self
        elif self.mode == FilterMode.NONE:
            return True
