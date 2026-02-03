from typing import Iterable

cimport cython

from libc.math cimport NAN
from phaast.structure.primitives cimport Atom, Structure, Molecule

cdef class Individual(Molecule):
    generations_alive : cython.uint

    descendants : list[Individual]

    def __init__(self, atoms_or_mol : Iterable[Atom], double energy = NAN):
        super().__init__(atoms_or_mol, energy)

        self.generations_alive = 0
        self.descendants : list[Individual] = []

    @property
    def is_optimized(self):
        return self.energy == self.energy


cdef class ChildIndividual(Individual):
    parent_a : Individual
    parent_b : Individual

    def __init__(self, atoms_or_mol : Iterable[Atom] | Molecule, parents : tuple[Individual, Individual]):
        super().__init__(atoms_or_mol)

        self.parent_a : Individual = parents[0]
        self.parent_b : Individual = parents[1]

    @property
    def parents(self) -> tuple[Individual, Individual]:
        return (self.parent_a, self.parent_b)

cdef class MutantIndividual(Individual):
    ancestor : Individual

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual):
        super().__init__(atoms_or_mol)

        self.ancestor : Individual = ancestor
        self.ancestor.descendants.append(self)

cdef class OptimizedIndividual(Individual):
    generations_alive : cython.uint

    descendants : list[Individual]

    ancestor : Individual

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual, energy : float):
        super().__init__(atoms_or_mol, energy)

        self.ancestor : Individual = ancestor
        self.ancestor.descendants.append(self)
