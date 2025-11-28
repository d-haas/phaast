# cython: freethreading_compatible = True

import cython

import random
from typing import Literal, Optional


from phaast.structure import Atom, Base, Structure
from phaast.structure.constants import AtomicNumber, AtomicRadi
from phaast.surface_explorator.genetic.migration.filter_list import *
from phaast.surface_explorator.genetic.migration import Migrator

from phaast.vec import Vector
from phaast.computer import Computer

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

    def check_available_position(self, new_atom : Atom) -> cython.int:

        if self.atom_population:
            for atom, _ in self.atom_population:
                if new_atom.is_touching(atom, bonding_tolerance=-0.005): #dist_squared < radius_sum_squared:
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
                    new_atom = Atom(atomic_number, new_position)
                    if self.check_available_position(new_atom):
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

class HedronMigrator(Migrator):
    base : Base
    n_vertices : HedronNumber
    filter_list : FilterList
    computer : Computer
    rng : random.Random

    def __init__(self, base : Base, n_vertices : HedronNumber, filter_list : FilterList, rng : None | random.Random):
        self.base = base

        assert n_vertices in (4,6,8,12,20), "Number of vertices is not valid, must be in (4,6,8,12,20)"

        self.n_vertices = n_vertices

        self.filter_list = filter_list

        if isinstance(rng, random.Random):
            self.rng = rng
        else:
            self.rng = random.Random()

    def __call__(
        self,
    ) -> Structure:


        atoms = [Atom(element.z) for element in self.base.elements]
        self.rng.shuffle(atoms)

        universe = HedronUniverse(
            n_vertices = self.n_vertices,
            filter_list = self.filter_list,
        )

        while atoms:
            atom = atoms.pop(0)
            random_available_position = universe.get_random_available_position(atom.z, self.rng)
            if random_available_position is not None:
                random_available_position, hedron_scale = random_available_position
                universe.include_atom(random_available_position, atom, hedron_scale)
            else:
                atoms.append(atom)
                
        return Structure([element[0] for element in universe.atom_population])
