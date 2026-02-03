from __future__ import annotations
from math import nan
from typing import Iterable

from phaast.structure import Atom, Structure, Molecule

class Individual(Structure):
    generations_alive : int

    descendants : list[Individual]

    def __init__(self, atoms_or_mol : Iterable[Atom], energy : float = nan): ...


class ChildIndividual(Individual):
    parents : tuple[Individual, Individual]

    def __init__(self, atoms_or_mol : Iterable[Atom] | Molecule, parents : tuple[Individual, Individual]): ...

class MutantIndividual(Individual):
    ancestor : Individual

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual): ...

class OptimizedIndividual(Individual, Molecule):
    ancestor : Individual

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual, energy : float): ...
