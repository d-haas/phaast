cdef class Vector:
    cdef public double x, y, z

    @staticmethod
    cdef Vector create(double x, double y, double z)
    
    cpdef Vector cross(self, Vector other)
    
    cdef Vector cmul(self, double other)

    cpdef double get_mod_sqr(self)
    cpdef double get_mod(self)
    
    cpdef void normalize(self)
    cpdef Vector normalized(self)
    
    cpdef Vector copy(self)
