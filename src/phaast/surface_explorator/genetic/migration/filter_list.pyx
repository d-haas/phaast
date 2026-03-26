from typing import Literal, Iterable

from phaast.structure.constants import AtomicNumber

cpdef enum FilterMode:
    NONE = 0
    INCLUDE = 1
    EXCLUDE = 2

filter_mode_to_str = {
    FilterMode.NONE : "None",
    FilterMode.INCLUDE : "Include",
    FilterMode.EXCLUDE : "Exclude",
}

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
        for pair in bondings:
            self[(pair[0], pair[1])] = True
            self[(pair[1], pair[0])] = True

    def is_permited(self, zi: AtomicNumber, zj: AtomicNumber) -> bool:
        if self.mode == FilterMode.INCLUDE:
            return (zi, zj) in self
        elif self.mode == FilterMode.EXCLUDE:
            return (zi, zj) not in self
        elif self.mode == FilterMode.NONE:
            return True

    def as_data(self) -> dict:
        return {
            "mode"     : filter_mode_to_str[self.mode],
            "bondings" : list(self.keys()),
            "import_path"   : "phaast.surface_explorator.genetic.migration.filter_list.FilterList",
            "args"     : (int(self.mode), list(self.keys())),
            "kwargs"   : {},
        }
