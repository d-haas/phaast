# cython: freethreading_compatible = True

import random
from typing import Optional
from structure import Atom
from structure.constants import AtomicNumber, AtomicRadi
import cython
from structure.creator.filter_list import *

from utils.typecheck import check_types
from vec import Vector

HedronNumber = Literal[4,6,8,12,20]
HedronPositions : dict[HedronNumber, list[Vector]] = {
    4  : [
        Vector( 1, 1, 1).normalized(),
        Vector(-1,-1, 1).normalized(),
        Vector(-1, 1,-1).normalized(),
        Vector( 1,-1,-1).normalized(),
    ],
    6  : [
        Vector(-1, 0, 0),
        Vector( 1, 0, 0),
        Vector( 0,-1, 0),
        Vector( 0, 1, 0),
        Vector( 0, 0,-1),
        Vector( 0, 0, 1),
    ],
    8  : [
        Vector(-1,-1,-1).normalized(),
        Vector( 1,-1,-1).normalized(),
        Vector(-1, 1,-1).normalized(),
        Vector( 1, 1,-1).normalized(),
        Vector(-1,-1, 1).normalized(),
        Vector( 1,-1, 1).normalized(),
        Vector(-1, 1, 1).normalized(),
        Vector( 1, 1, 1).normalized(),
    ],
    # For now lets just use 4, 6 and 8 vertices polyhedra
    12 : [],
    20 : [],
}

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
    ):
        self.n_vertices = n_vertices
        self.atom_population : list[Atom] = []
        self.bond_filter = filter_list if filter_list else FilterList(FilterMode.NONE, ())

    def check_available_position(self, pos : Vector, atomic_number : AtomicNumber) -> cython.int:
        result : cython.int = False
        atomic_radius : cython.double = AtomicRadi[atomic_number]

        if self.atom_population:
            for atom in self.atom_population:
                dist_squared : cython.double = (atom.pos - pos).mod_sqr
                radius_sum : cython.double = AtomicRadi[atom.z] + atomic_radius
                radius_sum_squared : cython.double = (radius_sum)**2 - 0.05 #Added margin for error
                if dist_squared < radius_sum_squared:
                    # Atom would be "inside the delimited field of bonding"
                    return False
                # If atomic bonding is permitted
                elif self.bond_filter.is_permited(atomic_number, atom.z):
                    # Atom is in "ideal distance for bonding"
                    result = True
        else:
            return True

        return result

    def get_available_positions(self, atomic_number : AtomicNumber) -> list[Vector]:
        positions : list[Vector] = []

        for atom in self.atom_population:
            radius : cython.double = AtomicRadi[atomic_number] + atom.radius
            for point in HedronPositions[self.n_vertices]:
                new_position = atom.pos + point*radius
                if self.check_available_position(new_position, atomic_number):
                    positions.append(new_position)

        return positions

    def get_random_available_position(self, atomic_number : AtomicNumber, rand_gen : None | random.Random = None) -> Vector | None:
        rng = rand_gen if rand_gen else random.Random()
        if self.atom_population:
            positions = self.get_available_positions(atomic_number)
            if positions:
                return rng.choice(positions)
            else:
                return None
        else:
            return Vector()

    def include_atom(self, pos : Vector, atom : Atom):
        # Caching radius for faster access
        atom.pos = pos
        self.atom_population.append(atom)
