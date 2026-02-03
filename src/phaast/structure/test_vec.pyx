from phaast.vector cimport Vector

cpdef abanana():
    cdef Vector a = Vector()
    a.x = 3.0
    print(a)
