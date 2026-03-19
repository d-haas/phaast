from phaast.structure.primitives cimport Structure

cdef class Crossover:
    pass

cdef class PlaneMating:
    cdef Structure ccall(self, Structure struct1, Structure struct2)
