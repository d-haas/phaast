# cython: freethreading_compatible = True

import random
from typing import Optional
from structure import Atom
from structure.constants import AtomicNumber, AtomicRadi
import cython
from structure.creator.filter_list import *

from vec import Vector

GOLDEN_RATIO = (1 + 5**.5)/2

HedronNumber = Literal[4,6,8,12,20]
HedronPositions : dict[HedronNumber, list[Vector]] = {}
HedronPositions[4] = [
    Vector( 1, 1, 1).normalized(),
    Vector(-1,-1, 1).normalized(),
    Vector(-1, 1,-1).normalized(),
    Vector( 1,-1,-1).normalized(),
]
HedronPositions[6] = [
    Vector(-1, 0, 0),
    Vector( 1, 0, 0),
    Vector( 0,-1, 0),
    Vector( 0, 1, 0),
    Vector( 0, 0,-1),
    Vector( 0, 0, 1),
]
HedronPositions[8] = [
    Vector(-1,-1,-1).normalized(),
    Vector( 1,-1,-1).normalized(),
    Vector(-1, 1,-1).normalized(),
    Vector( 1, 1,-1).normalized(),
    Vector(-1,-1, 1).normalized(),
    Vector( 1,-1, 1).normalized(),
    Vector(-1, 1, 1).normalized(),
    Vector( 1, 1, 1).normalized(),
]

HedronPositions[12] = []

HedronPositions[20] = HedronPositions[8] + [
    Vector( GOLDEN_RATIO, 1/GOLDEN_RATIO, 0).normalized(),
    Vector( GOLDEN_RATIO,-1/GOLDEN_RATIO, 0).normalized(),
    Vector(-GOLDEN_RATIO, 1/GOLDEN_RATIO, 0).normalized(),
    Vector(-GOLDEN_RATIO,-1/GOLDEN_RATIO, 0).normalized(),

    Vector( 0, GOLDEN_RATIO, 1/GOLDEN_RATIO).normalized(),
    Vector( 0, GOLDEN_RATIO,-1/GOLDEN_RATIO).normalized(),
    Vector( 0,-GOLDEN_RATIO, 1/GOLDEN_RATIO).normalized(),
    Vector( 0,-GOLDEN_RATIO,-1/GOLDEN_RATIO).normalized(),

    Vector( 1/GOLDEN_RATIO, 0, GOLDEN_RATIO).normalized(),
    Vector( 1/GOLDEN_RATIO, 0,-GOLDEN_RATIO).normalized(),
    Vector(-1/GOLDEN_RATIO, 0, GOLDEN_RATIO).normalized(),
    Vector(-1/GOLDEN_RATIO, 0,-GOLDEN_RATIO).normalized(),
]

class HedronUniverse:
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    atom_population : list[tuple[Atom, float]]
    bond_filter : FilterList
    n_vertices : HedronNumber

    def __init__(
        self,
        n_vertices : HedronNumber,
        filter_list : Optional[FilterList] = None,
    ):
        self.n_vertices = n_vertices
        self.atom_population = []
        self.bond_filter = filter_list if filter_list else FilterList(FilterMode.NONE, ())

    def check_available_position(self, pos : Vector, atomic_number : AtomicNumber) -> cython.int:
        atomic_radius : cython.double = AtomicRadi[atomic_number]

        if self.atom_population:
            for atom, _ in self.atom_population:
                dist_squared : cython.double = (atom.pos - pos).mod_sqr
                radius_sum : cython.double = AtomicRadi[atom.z] + atomic_radius
                radius_sum_squared : cython.double = (radius_sum)**2 - 0.005 #Added margin for error
                if dist_squared < radius_sum_squared:
                    # Atom would be "inside the delimited field of bonding"
                    return False

            return True

        else:
            return True


    def get_available_positions(self, atomic_number : AtomicNumber) -> list[tuple[Vector, float]]:
        positions : list[tuple[Vector, float]] = []

        for atom, hedron_scale in self.atom_population:
            if self.bond_filter.is_permited(atomic_number, atom.z):
                radius : cython.double = AtomicRadi[atomic_number] + atom.radius
                for point in HedronPositions[self.n_vertices]:
                    new_position = atom.pos + point*radius*hedron_scale
                    if self.check_available_position(new_position, atomic_number):
                        positions.append(
                            (
                                new_position,
                                -hedron_scale,
                            ),
                        )

        return positions

    def get_random_available_position(self, atomic_number : AtomicNumber, rand_gen : None | random.Random = None) -> tuple[Vector, float] | None:
        rng = rand_gen if rand_gen else random.Random()
        if self.atom_population:
            positions = self.get_available_positions(atomic_number)
            if positions:
                return rng.choice(positions)
            else:
                return None
        else:
            return Vector(), 1.0

    def include_atom(self, pos : Vector, atom : Atom, hedron_scale : float):
        # Caching radius for faster access
        atom.pos = pos
        self.atom_population.append(
            (
                atom,
                hedron_scale,
            )
        )
