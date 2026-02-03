from phaast.structure.primitives cimport Atom, Structure, Molecule

cdef class Individual(Molecule):
    cdef public unsigned int generations_alive
    cdef public list descendants

cdef class ChildIndividual(Individual):
    cdef public parent_a
    cdef public parent_b

cdef class MutantIndividual(Individual):
    cdef public Individual ancestor

cdef class OptimizedIndividual(Individual):
    cdef public unsigned int generations_alive
    cdef public list descendants
    cdef public Individual ancestor

