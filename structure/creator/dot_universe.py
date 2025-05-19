# cython: freethreading_compatible = True

import random
from math import ceil
from typing import Optional
from structure import Atom
from structure.constants import *
import cython
from structure.creator import FilterList, FilterMode

from typecheck import check_types
from vec import Vector

@cython.cclass
class Limit:
    min = cython.declare(cython.int, visibility="public")
    max = cython.declare(cython.int, visibility="public")
    def __init__(self, min : int, max : int):
        self.min = min
        self.max = max

@cython.cclass
class DotUniverse:
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    dot_distance : cython.double
    atom_population : list[Atom]
    limits : tuple[Limit, Limit, Limit]
    max_radius: cython.double
    bond_filter : FilterList

    @check_types
    def __init__(
        self,
        dot_distance : float,
        max_radius : float = 2.60,
        filter_list : Optional[FilterList] = None,
    ):
        self.dot_distance = dot_distance
        self.atom_population : list[Atom] = []
        self.limits = (
            Limit(0, 0),
            Limit(0, 0),
            Limit(0, 0),
        )
        self.max_radius = max_radius
        self.bond_filter = filter_list if filter_list else FilterList(FilterMode.NONE, ())

    @cython.ccall
    def check_available_position(self, cell_pos : tuple[int, int, int], atomic_number : AtomicNumber) -> cython.int:
        pos_vec = Vector(*cell_pos) * self.dot_distance
        result : cython.int = False
        atomic_radius : cython.double = AtomicRadi[atomic_number]

        if self.atom_population:
            for atom in self.atom_population:
                dist_squared : cython.double = (atom.pos - pos_vec).mod_sqr
                radius_sum : cython.double = AtomicRadi[atom.z] + atomic_radius
                radius_sum_squared : cython.double = (radius_sum)**2
                if dist_squared < (radius_sum + self.dot_distance*1.001)**2:
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

    @cython.ccall
    def get_available_positions(self, atomic_number : AtomicNumber) -> list[tuple[int, int, int]]:
        positions : list[
            tuple[cython.int, cython.int, cython.int]
        ] = []
        i : cython.int
        j : cython.int
        k : cython.int
        _ : tuple[range, range, range] = (
            range(self.limits[0].min, self.limits[0].max+1),
            range(self.limits[1].min, self.limits[1].max+1),
            range(self.limits[2].min, self.limits[2].max+1),
        )

        for i in range(self.limits[0].min, self.limits[0].max+1):
            for j in range(self.limits[1].min, self.limits[1].max+1):
                for k in range(self.limits[2].min, self.limits[2].max+1):
                    if self.check_available_position((i, j, k), atomic_number):
                        positions.append(
                            (i, j, k),
                        )

        return positions

    @cython.ccall
    def get_random_available_position(self, atomic_number : AtomicNumber, rand_gen : None | random.Random = None) -> tuple[int, int, int]:
        rng = rand_gen if rand_gen else random.Random()

        if self.atom_population:
            positions = self.get_available_positions(atomic_number)
            return rng.choice(positions)

        else:
            return (0,0,0)




    @cython.ccall
    def include_atom(self, cell_pos : tuple[int, int, int], atom : Atom):
        # Caching radius for faster access
        radius = AtomicRadi[atom.z]

        atom.pos = Vector(*cell_pos) * self.dot_distance

        for coord in range(3):
            min_coord = cell_pos[coord]-ceil((self.max_radius+radius)/self.dot_distance)
            max_coord = cell_pos[coord]+ceil((self.max_radius+radius)/self.dot_distance)
            if min_coord < self.limits[coord].min:
                self.limits[coord].min = min_coord
            if max_coord < self.limits[coord].max:
                self.limits[coord].max = max_coord

        self.atom_population.append(atom)

