from phaast.vector cimport Vector
from phaast.utils.c_random cimport *

cpdef abanana():
    cdef Vector a = Vector()
    a.x = 3.0
    print(a)
