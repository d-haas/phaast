from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
    from phaast.structure import Molecule

from phaast.structure.comparator.c_comparators import energy_difference, grigoryan_springborg, bonding_length

class ComparisonAlgorithm(Protocol):
    def __call__(self, mol1 : Molecule, mol2 : Molecule) -> bool:...

class ComparisonSequence(ComparisonAlgorithm):
    __slots__ = ("algorithms",)

    def __init__(self, *algorithms : ComparisonAlgorithm):
        self.algorithms = algorithms

    def __call__(self, mol1 : Molecule, mol2 : Molecule) -> bool:
        for algorithm in self.algorithms:
            if algorithm(mol1, mol2):
                return True

        return False

class EnergyDifference(ComparisonAlgorithm):
    __slots__ = ("tolerance",)

    def __init__(self, tolerance : float = 1e-4):
        self.tolerance = tolerance

    def __call__(self, mol1 : Molecule, mol2 : Molecule) -> bool:
        return energy_difference(mol1, mol2, self.tolerance)

class GrigoryanSpringborg(ComparisonAlgorithm):
    __slots__ = ("tolerance",)

    tolerance : float

    def __init__(self, tolerance : float):
        self.tolerance = tolerance

    def __call__(self, mol1 : Molecule, mol2 : Molecule) -> bool:
        return grigoryan_springborg(mol1, mol2, self.tolerance)

class BondingLength(ComparisonAlgorithm):
    __slots__ = ("tolerance", "bonding_tolerance",)

    tolerance : float
    bonding_tolerance : float

    def __init__(self, tolerance : float, bonding_tolerance : float = 0.25):
        self.tolerance = tolerance
        self.bonding_tolerance = bonding_tolerance

    def __call__(self, mol1 : Molecule, mol2 : Molecule) -> bool:
        return bonding_length(mol1, mol2, self.tolerance, self.bonding_tolerance)
