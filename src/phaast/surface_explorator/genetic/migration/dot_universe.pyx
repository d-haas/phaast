# cython: freethreading_compatible = True

import cython
import random
from math import ceil
from typing import Optional

from cython.parallel import prange

from phaast.utils.c_random cimport get_rand, get_randint, get_rand_uniform
from phaast.vector cimport Vector
from phaast.structure.primitives cimport Atom, Structure
from phaast.structure import Base
from phaast.structure.constants import *
from phaast.surface_explorator.genetic.migration import Migrator
from phaast.surface_explorator.genetic.migration.filter_list import *

from phaast.utils.typecheck import check_types


cdef class Limit:
    min : cython.int
    max : cython.int
    def __init__(self, _min : int, _max : int):
        self.min = _min
        self.max = _max

cdef class DotUniverse:
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    dot_distance : cython.double
    atom_population : list[Atom]
    limits : Limit[:]
    max_radius: cython.double
    bond_filter : FilterList

    @check_types
    def __init__(
        self,
        dot_distance : cython.double,
        max_radius : cython.double = 2.60,
        filter_list : Optional[FilterList] = None,
    ):
        self.dot_distance = dot_distance
        self.atom_population : list[Atom] = []

        cdef Limit[:] temp_limits = cvarray(shape=(3,), itemsize = sizeof(Limit*), format="O")

        cdef int i
        cdef Limit limit_ptr
        for i in range(3):
            limit_ptr = Limit(0, 0)
            temp_limits[i] = limit_ptr

        self.limits = temp_limits

        self.max_radius = max_radius
        self.bond_filter = filter_list if filter_list else FilterList(FilterMode.NONE, ())

    cdef bool check_available_position(self, int cell_i, int cell_j, int cell_k, unsigned int atomic_number):
        cdef Vector pos_vec = Vector(*cell_pos) * self.dot_distance
        cdef bool result = False
        cdef double atomic_radius = AtomicRadi[atomic_number]
        cdef double dist_squared
        cdef double radius_sum
        cdef double radius_sum_squared

        if self.atom_population:
            for atom in self.atom_population:
                dist_squared = (atom.pos - pos_vec).mod_sqr
                radius_sum = AtomicRadi[atom.z] + atomic_radius
                radius_sum_squared = (radius_sum)**2
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

    cpdef list get_available_positions(self, unsigned int atomic_number):# -> list[tuple[int, int, int]]:
        positions : list[
            tuple[cython.int, cython.int, cython.int]
        ] = []
        cdef int i, j, k
        cdef int i_min, i_max, j_min, j_max, k_min, k_max
        i_min, i_max = self.limits[0].min, self.limits[0].max+1
        j_min, j_max = self.limits[1].min, self.limits[1].max+1
        k_min, k_max = self.limits[2].min, self.limits[2].max+1

        for i in range(i_min, i_max):
            for j in range(j_min, j_max):
                for k in range(k_min, k_max):
                    if self.check_available_position(i, j, k, atomic_number):
                        positions.append(
                            (i, j, k),
                        )

        return positions

    cpdef tuple get_random_available_position(self, unsigned int atomic_number):
        if self.atom_population:
            positions = self.get_available_positions(atomic_number)
            return positions[get_randint(0, len(positions)-1)]

        else:
            return (0,0,0)




    def include_atom(self, cell_pos : tuple[int, int, int], Atom atom):
        # Caching radius for faster access
        radius = atom.radius

        atom.pos = Vector(cell_i, cell_j, cell_k) * self.dot_distance

        for coord in range(3):
            min_coord = cell_pos[coord]-ceil((self.max_radius+radius)/self.dot_distance)
            max_coord = cell_pos[coord]+ceil((self.max_radius+radius)/self.dot_distance)
            if min_coord < self.limits[coord].min:
                self.limits[coord].min = min_coord
            if max_coord < self.limits[coord].max:
                self.limits[coord].max = max_coord

        self.atom_population.append(atom)


class MeshMigrator(Migrator):
    base : Base
    cell_size : float
    filter_list : FilterList

    def __init__(self, base : Base, cell_size : float, filter_list : FilterList):
        self.base = base

        self.cell_size = cell_size

        self.filter_list = filter_list

    def __call__(self) -> Structure:
        """
        Generate a random structure with atoms in the base
        Use seed as parameter for future reproducibility
        (same seed with the same base will result in the same structure)
        """

        # Create list of atoms based on stoichiometry
        atoms = [Atom(element.z) for element in self.base.elements]
        # Randomly shuffle it
        self.rng.shuffle(atoms)

        # Create dot universe
        universe = DotUniverse(
            self.cell_size,
            max((atom.radius for atom in atoms)),
            self.filter_list,
        )

        while atoms:
            # Get first atom and remove it from the list
            atom = atoms.pop(0)

            # Get random position to put the atom
            random_available_position = universe.get_random_available_position(atom.z)
            
            # Put it in the universe if there are positions available
            if random_available_position:
                universe.include_atom(random_available_position, atom)
            # Else, put it in the end of the list
            else:
                atoms.append(atom)
                
        # Return structure of atoms in the universe
        return Structure(atoms)
