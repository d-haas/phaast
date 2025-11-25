from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from phaast.structure import Molecule

import bisect
import itertools
from enum import Enum
from phaast.vec import Vector
from phaast.structure.constants import AtomicNumber

class ComparisonAlgorithm(Enum):
    GRIGORYAN_SPRINGBORN = 1
    HAAS_OLIVEIRA = 2

def grigoryan_springborn(struct1 : Molecule, struct2 : Molecule, **_) -> float:
    """
    Compare different structures using the
    Grigoryan-Springborn algorithm
    DOI: 10.1140/epjd/e2005-00141-6
    Equation (1)
    """
    atoms_num : int = len(struct1) # Number of atoms in structure

    #Check if number of atoms is the same in both structures
    assert struct1.is_equal_to(struct2), "Both structure should have the same number of atoms"

    """
    Sum distances between atoms of each structure and
    store it in a ordered list for each structure for
    each combination of two elements

    Thanks Amanda
    """
    self_dists : dict[tuple[AtomicNumber, AtomicNumber], list[float]] = {}
    for atom_i, atom_j in itertools.combinations(struct1, 2):
        dict_key = (atom_i.z, atom_j.z) if atom_j.z>atom_i.z else (atom_j.z, atom_i.z)
        if not dict_key in self_dists:
            self_dists[dict_key] = []
        diff : Vector = atom_i.pos - atom_j.pos
        bisect.insort(
            self_dists[dict_key],
            diff.mod_sqr,
        )
    other_dists : dict[tuple[AtomicNumber, AtomicNumber], list[float]] = {}
    for atom_i, atom_j in itertools.combinations(struct2, 2):
        dict_key = (atom_i.z, atom_j.z) if atom_j.z>atom_i.z else (atom_j.z, atom_i.z)
        if not dict_key in other_dists:
            other_dists[dict_key] = []
        diff = atom_i.pos - atom_j.pos
        bisect.insort(
            other_dists[dict_key],
            diff.mod_sqr,
        )

    # Get difference between each distance in each molecule (squared)
    sum_distances_squared_diff : float = 0
    for dict_key in self_dists:
        sum_distances_squared_diff+= sum([
            (i - j)**2
            for i, j
            in zip(self_dists[dict_key], other_dists[dict_key])
        ])

    # Calculate final value of Grigoryan-Springborn algorithm
    q : float = ( ( 2/(atoms_num*(atoms_num-1)) ) * sum_distances_squared_diff )**.5
    s : float = 1 / ( 1 + q )

    return s

def haas_oliveira(mol1 : Molecule, mol2 : Molecule, **kwargs) -> float:
    bonding_tolarance : float = kwargs["bonding_tolerance"] if "bonding_tolerance" in kwargs else 0.0

    mol1_bondings = mol1.get_bondings_lenghts(bonding_tolarance)
    mol2_bondings = mol2.get_bondings_lenghts(bonding_tolarance)

    # Compare if both molecules have the same types of bondings
    if mol1_bondings.keys() != mol2_bondings.keys(): return 0
    # At this point both molecules share the same bonding types

    for bonding in mol1_bondings:
        if len(mol1_bondings[bonding]) != len(mol2_bondings[bonding]):
            return 0
    # At this point both molecules have the same number of bondings per type

    # Compare difference between distances for each bonding type and add to a general variable
    square_distances_difference_sum : float = 0
    for bonding in mol1_bondings:
        square_distances_difference_sum+= sum(
            [
                abs(i-j) for i, j
                in zip(
                    sorted(mol1_bondings[bonding]),
                    sorted(mol2_bondings[bonding]),
                )
            ]
        )

    # Use said variable (with positive value) to obtain a number between 1 and 0
    return 1 / (1 + square_distances_difference_sum)

comparison_functions_dict : dict[ComparisonAlgorithm, Callable[[Molecule, Molecule], float]] = {
    ComparisonAlgorithm.GRIGORYAN_SPRINGBORN : grigoryan_springborn,
    ComparisonAlgorithm.HAAS_OLIVEIRA : haas_oliveira,
}
