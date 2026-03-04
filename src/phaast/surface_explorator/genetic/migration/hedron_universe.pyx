# cython: freethreading_compatible = True

import cython

import random
from typing import Literal, Optional

from phaast.utils.c_random cimport get_rand, get_randint, get_rand_uniform
from phaast.vector cimport Vector
from phaast.structure.primitives cimport Atom, Structure

from phaast.structure import Base
from phaast.structure.constants import AtomicNumber, AtomicRadi
#from phaast.surface_explorator.genetic.migration.filter_list cimport FilterMode
from phaast.surface_explorator.genetic.migration.filter_list import FilterMode, FilterList
from phaast.surface_explorator.genetic.migration import Migrator

from phaast.computer import Computer

GOLDEN_RATIO = (1 + 5**.5)/2

HedronNumber = Literal[6,8,12,20] #4 was removed

HedronPositions : dict[HedronNumber, list[Vector]] = {}
#HedronPositions[4] = [
#    Vector( 1, 1, 1).normalized(),
#    Vector(-1,-1, 1).normalized(),
#    Vector(-1, 1,-1).normalized(),
#    Vector( 1,-1,-1).normalized(),
#]

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

HedronPositions[12] = [
    Vector(0, 1, GOLDEN_RATIO).normalized(),
    Vector(0, 1,-GOLDEN_RATIO).normalized(),
    Vector(0,-1, GOLDEN_RATIO).normalized(),
    Vector(0,-1,-GOLDEN_RATIO).normalized(),

    Vector( 1, GOLDEN_RATIO, 0).normalized(),
    Vector( 1,-GOLDEN_RATIO, 0).normalized(),
    Vector(-1, GOLDEN_RATIO, 0).normalized(),
    Vector(-1,-GOLDEN_RATIO, 0).normalized(),

    Vector( GOLDEN_RATIO, 0, 1).normalized(),
    Vector( GOLDEN_RATIO, 0,-1).normalized(),
    Vector(-GOLDEN_RATIO, 0, 1).normalized(),
    Vector(-GOLDEN_RATIO, 0,-1).normalized(),
]

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

cdef class HedronUniverse:
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    atom_population : list[Atom]
    bond_filter : FilterList
    n_vertices : cython.int # HedronNumber

    def __init__(
        self,
        n_vertices : HedronNumber,
        filter_list : Optional[FilterList] = None,
    ):
        self.n_vertices = n_vertices
        self.atom_population = []
        self.bond_filter = filter_list if filter_list else FilterList(FilterMode.NONE, ())

    cdef bool check_available_position(self, Atom new_atom):

        if self.atom_population:
            for atom in self.atom_population:
                if new_atom.is_touching(atom, bonding_tolerance=-0.005): #dist_squared < radius_sum_squared:
                    # Atom would be "inside the delimited field of bonding"
                    return False

            return True

        else:
            return True


    cpdef list get_available_positions(self, unsigned int atomic_number): # -> list[tuple[Vector, float]]:
        cdef list positions = [] # : list[Vector]

        cdef double radius
        cdef Vector new_position
        cdef Atom new_atom

        for atom in self.atom_population:
            if self.bond_filter.is_permited(atomic_number, atom.z):
                radius : cython.double = AtomicRadi[atomic_number] + atom.radius
                for point in HedronPositions[self.n_vertices]:
                    new_position = atom.pos + point*radius
                    new_atom = Atom(atomic_number, new_position)
                    if self.check_available_position(new_atom):
                        positions.append(
                            new_position,
                        )

        return positions

    def get_random_available_position(self, atomic_number : AtomicNumber) -> Vector | None:
        if self.atom_population:
            positions = self.get_available_positions(atomic_number)
            if positions:
                return positions[get_randint(0, len(positions)-1)]
            else:
                return None
        else:
            return Vector(0, 0, 0)

    def include_atom(self, Vector pos, Atom atom):
        # Caching radius for faster access
        atom.pos = pos
        self.atom_population.append(
            atom,
        )

    cpdef Structure get_structure(self):
        return Structure([atom for atom in self.atom_population])

class HedronMigrator(Migrator):
    base : Base
    n_vertices : HedronNumber
    filter_list : FilterList

    def __init__(self, base : Base, n_vertices : HedronNumber, filter_list : FilterList):
        self.base = base

        assert n_vertices in (4,6,8,12,20), "Number of vertices is not valid, must be in (4,6,8,12,20)"

        self.n_vertices = n_vertices

        self.filter_list = filter_list

    def __call__(
        self,
    ) -> Structure:


        atoms = [Atom(element.z) for element in self.base.elements]
        random.shuffle(atoms)

        universe = HedronUniverse(
            n_vertices = self.n_vertices,
            filter_list = self.filter_list,
        )

        while atoms:
            atom = atoms.pop(0)
            random_available_position = universe.get_random_available_position(atom.z)
            if random_available_position is not None:
                universe.include_atom(random_available_position, atom)
            else:
                atoms.append(atom)
                
        return Structure([atom for atom in universe.atom_population])
