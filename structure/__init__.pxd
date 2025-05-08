from vec cimport Vector

cdef class Atom:
    cdef public unsigned int z
    cdef public Vector pos

    @staticmethod
    cdef Atom create(unsigned int atomic_number, Vector pos)

    cpdef Atom copy(self)
