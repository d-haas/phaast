from phaast.structure.primitives cimport Structure

cdef double get_rand() nogil

cdef unsigned long get_randint(int a, int b) nogil

cdef double get_rand_uniform(double a, double b) nogil

cdef class Mutator:
    pass

cdef class DisplacementMutator(Mutator):
    cdef unsigned int num
    cdef double min_displacement
    cdef double max_displacement

    cdef Structure ccall(self, Structure structure)

cdef class PermuteMutator(Mutator):
    cdef int num : int

    cdef Structure ccall(self, Structure structure)

cdef class TwistMutator(Mutator):
    cdef double min_angle
    cdef double max_angle

    cdef Structure ccall(self, Structure structure)
