# cython: freethreading_compatible = True

cimport cython

cdef class Vector:
    cdef public double x, y, z
