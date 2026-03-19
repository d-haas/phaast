from __future__ import annotations
from math import nan
from typing import Iterable, Literal

from phaast.structure import Atom, Structure, Molecule
from phaast.structure.primitives import MoleculeData

class IndividualData(MoleculeData):
    generations_alive : int
    id : int
    descendants : list[int]

class Individual(Structure):
    generations_alive : int
    id : int
    descendants : list[int]

    def __init__(self, atoms_or_mol : Iterable[Atom], id : int, energy : float = nan): ...

    def get_descendants(self) -> list[Individual]: ...

    def as_data(self) -> IndividualData: ...

class ChildIndividualData(IndividualData):
    type : Literal["child"]
    parent_a : int
    parent_b : int

class ChildIndividual(Individual):
    parents : tuple[int, int]

    def __init__(self, atoms_or_mol : Iterable[Atom] | Molecule, parents : tuple[Individual, Individual], id : int): ...

    def as_data(self) -> ChildIndividualData: ...

class MutantIndividualData(IndividualData):
    type     : Literal["mutant"]
    ancestor : int

class MutantIndividual(Individual):
    ancestor : int

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual, id : int): ...

    def as_data(self) -> MutantIndividualData: ...

class OptimizedIndividualData(IndividualData):
    type     : Literal["optimized"]
    ancestor : int

class OptimizedIndividual(Individual, Molecule):
    ancestor : int

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual, id : int, energy : float): ...

    def as_data(self) -> OptimizedIndividualData: ...
