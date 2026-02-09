from phaast.structure.primitives cimport Structure

cdef class Mutator:
    pass

cdef class DisplacementMutator(Mutator):
    cdef unsigned int num
    cdef double min_displacement
    cdef double max_displacement

    cdef Structure ccall(self, Structure structure)

cdef class PermuteMutator(Mutator):
    cdef int num

    cdef Structure ccall(self, Structure structure)

cdef class TwistMutator(Mutator):
    cdef double min_angle
    cdef double max_angle

    cdef Structure ccall(self, Structure structure)
