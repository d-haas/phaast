cpdef Vector create_vector(double x = *, double y = *, double z = *)

cdef struct Vec:
    double x
    double y
    double z

cdef class Vector:
    cdef public double x, y, z

    cdef Vector add(self, Vector other)
    cdef Vector sub(self, Vector other)
    cdef double dot(self, Vector other)
    cdef Vector mul(self, double other)
    cdef Vector div(self, double other)
    cdef Vector neg(self)

    cpdef Vector cross(Vector self, Vector other)

    cpdef void rotate_x(Vector self, double ang)
    cpdef Vector rotated_x(Vector self, double ang)
    cpdef void rotate_y(Vector self, double ang)
    cpdef Vector rotated_y(Vector self, double ang)
    cpdef void rotate_z(Vector self, double ang)
    cpdef Vector rotated_z(Vector self, double ang)

    cdef double cmod_sqr(self)
    cdef double cmod(self)

    cpdef void normalize(self)
    cpdef Vector normalized(self)

    cpdef Vector copy(self)
