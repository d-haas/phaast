from phaast.structure.primitives cimport Atom, Structure, Molecule

cdef class Individual(Molecule):
    cdef public unsigned int generations_alive
    cdef public list descendants
    cdef public unsigned int id

cdef class ChildIndividual(Individual):
    cdef public unsigned int parent_a
    cdef public unsigned int parent_b

cdef class MutantIndividual(Individual):
    cdef public unsigned int ancestor

cdef class OptimizedIndividual(Individual):
    cdef public unsigned int ancestor

