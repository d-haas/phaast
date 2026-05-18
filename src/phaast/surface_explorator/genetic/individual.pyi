from __future__ import annotations
from math import nan
from typing import Iterable

from phaast.structure import Atom, Structure, Molecule
from phaast.structure.primitives import MoleculeData

dummy_individual : Individual

class IndividualData(MoleculeData):
    id : int
    descendants : list[int]
    type        : str

class ChildIndividualData(IndividualData):
    parent_a : int
    parent_b : int

class MutantIndividualData(IndividualData):
    ancestor : int

class OptimizedIndividualData(IndividualData):
    ancestor : int

class Individual(Structure):
    id : int
    descendants : list[int]
    energy      : float

    def __init__(self, atoms_or_mol : Iterable[Atom], id : int, energy : float = nan): ...

    def get_descendants(self) -> list[int]: ...

    def add_descendant(self, ind_id : int) -> None: ...

    def as_data(self) -> IndividualData: ...

    @classmethod
    def from_data(cls, data : IndividualData) -> Individual: ... # type: ignore[override]

class ChildIndividual(Individual):
    parents : tuple[int, int]

    def __init__(self, atoms_or_mol : Iterable[Atom] | Molecule, parents : tuple[int, int], id : int): ...

    def as_data(self) -> ChildIndividualData: ...

class MutantIndividual(Individual):
    ancestor : int

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : int, id : int): ...

    def as_data(self) -> MutantIndividualData: ...

class OptimizedIndividual(Individual, Molecule):
    ancestor : int

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : int, id : int, energy : float): ...

    def as_data(self) -> OptimizedIndividualData: ...
