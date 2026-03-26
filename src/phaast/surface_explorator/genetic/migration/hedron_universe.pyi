from typing import Literal, Optional

from phaast.structure import Atom, Base, Structure
from phaast.structure.constants import AtomicNumber
from phaast.surface_explorator.genetic.migration import Migrator
from phaast.utils import ObjectData
from phaast.vector import Vector
from phaast.surface_explorator.genetic.migration.filter_list import FilterList

HedronNumber = Literal[6,8,12,20]

HedronPositions : dict[HedronNumber, list[Vector]]

class HedronUniverse:
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    atom_population : list[Atom]
    bond_filter : FilterList
    n_vertices : HedronNumber

    def __init__(
        self,
        n_vertices : HedronNumber,
        filter_list : Optional[FilterList] = None,
    ): ...

    def get_available_positions(self, atomic_number : AtomicNumber) -> list[tuple[Vector, float]]: ...

    def get_random_available_position(self, atomic_number : AtomicNumber) -> Vector | None: ...

    def include_atom(self, pos : Vector, atom : Atom) -> None: ...

    def get_structure(self) -> Structure: ...

class HedronMigrator(Migrator):
    base : Base
    n_vertices : HedronNumber
    filter_list : FilterList

    def __init__(self, base : Base, n_vertices : HedronNumber, filter_list : FilterList): ...

    def __call__(self) -> Structure: ...

    def as_data(self) -> ObjectData: ...
