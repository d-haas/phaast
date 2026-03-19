from typing import Iterable

cimport cython

from libc.math cimport NAN
from phaast.structure.primitives cimport Atom, Structure, Molecule

cdef class Individual(Molecule):
    generations_alive : cython.uint
    descendants : list[cython.uint]
    id : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom], id : cython.uint, double energy = NAN):
        super().__init__(atoms_or_mol, energy)

        self.generations_alive = 0
        self.descendants : list[Individual] = []
        self.id = id

    @property
    def is_optimized(self):
        return self.energy == self.energy

    def add_descendant(self, ind : Individual):
        self.descendants.append(ind.id)

    def get_descendants(self):
        return self.descendants

    def get_id(self):
        return self.id

    def as_data(self):
        return super().as_data() | {
            "generations_alive" : self.generations_alive,
            "id"                : self.id,
            "descendants"       : self.descendants,
        }


cdef class ChildIndividual(Individual):

    parent_a : cython.uint
    parent_b : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom] | Molecule, parents : tuple[Individual, Individual], id : cython.uint):
        super().__init__(atoms_or_mol, id)

        self.parent_a = parents[0].id
        self.parent_b = parents[1].id

        parents[0].add_descendant(self)
        parents[1].add_descendant(self)

    @property
    def parents(self) -> tuple[Individual, Individual]:
        return (self.parent_a, self.parent_b)

    def as_data(self):
        return super().as_data() | {
            "type"     : "child",
            "parent_a" : self.parent_a,
            "parent_b" : self.parent_b,
        }

cdef class MutantIndividual(Individual):

    ancestor : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual, id : cython.uint):
        super().__init__(atoms_or_mol, id)

        self.ancestor = ancestor.id
        ancestor.add_descendant(self)

    def as_data(self):
        return super().as_data() | {
            "type"     : "mutant",
            "ancestor" : self.ancestor,
        }

cdef class OptimizedIndividual(Individual):

    ancestor : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : Individual, id : cython.uint, energy : float):
        super().__init__(atoms_or_mol, id, energy)

        self.ancestor = ancestor.id
        ancestor.add_descendant(self)

    def as_data(self):
        return super().as_data() | {
            "type"     : "optimized",
            "ancestor" : self.ancestor,
        }
