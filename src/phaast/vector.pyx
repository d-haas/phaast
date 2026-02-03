# cython: freethreading_compatible = True
from typing import Any, Iterator, Union, overload

cimport cython
from libc.math cimport sqrt, sin, cos

cpdef Vector create_vector(double x = 0, double y = 0, double z = 0):
    return Vector(x, y, z)

cdef struct BaseVector:
    double x
    double y
    double z

@cython.auto_pickle(True)
cdef class Vector:
    x : cython.double
    y : cython.double
    z : cython.double

    def __init__(self, *args : cython.double):
        args_size = len(args)
        if   args_size == 0:
            self.x, self.y, self.z = 0, 0, 0
        elif args_size == 1:
            self.x, self.y, self.z = args*3
        elif args_size == 3:
            self.x, self.y, self.z = args
        else:
            raise ValueError(
                f"There should be 0, 1 or 3 arguments, not {len(args)}",
            )

    def __getitem__(self, key : cython.uint) -> cython.double:
        """
        Get item function, in case its needed
        to index by attribute number
        """
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise KeyError(
                f"{key} is out of vector bounds"
            )

    def __setitem__(self, key : cython.uint, value : cython.double) -> None:
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise KeyError(
                f"{key} is out of vector bounds"
            )

    def __iter__(self) -> Iterator[cython.double]:
        """
        Iter over vector
        """
        yield self.x
        yield self.y
        yield self.z

    cdef Vector add(self, Vector other):
        cdef Vector result = Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )
        return result
    def __add__(self, other : Vector) -> Vector:
        """
        Vector addition
        """
        return self.add(other)
    def __iadd__(self, other : Vector) -> Vector:
        """
        In-place vector addition
        """
        self.x+= other.x
        self.y+= other.y
        self.z+= other.z
        return self

    cdef Vector sub(self, Vector other):
        cdef Vector result = Vector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )
        return result
    def __sub__(self, other : Vector) -> Vector:
        """
        Vector subtraction
        """
        return self.sub(other)
    def __isub__(self, other : Vector) -> Vector:
        """
        In-place vector subtraction
        """
        self.x-= other.x
        self.y-= other.y
        self.z-= other.z
        return self

    cdef double dot(self, Vector other):
        return self.x*other.x + self.y*other.y + self.z*other.z
    cdef Vector mul(self, double other):
        cdef Vector result = Vector(other * self.x, other * self.y, other * self.z)
        return result

    def __mul__(self, other : Union[Vector,cython.double]) -> Union[cython.double, Vector]:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        if isinstance(other, Vector):
            return self.dot(other)
        elif isinstance(other, float):
            return self.mul(other)
        else:
            raise TypeError(
                f"Multiplication only accepts a Vector or cython.double, not {type(other)}."
            )

    def __rmul__(self, other : Union[Vector, cython.double]) -> Union[cython.double, Vector]:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        if isinstance(other, Vector):
            return self.dot(other)
        elif isinstance(other, float):
            return self.mul(other)
        else:
            raise TypeError(
                f"Multiplication only accepts a Vector or cython.double, not {type(other)}."
            )

    def __imul__(self, other : cython.double) -> Vector:
        """
        In-place multiplication by scalar
        """
        if isinstance(other, float):
            self.x*= other
            self.y*= other
            self.z*= other
            return self
        else:
            raise TypeError(
                f"In-place multiplication only accepts cython.double, not {type(other)}."
            )

    cdef Vector div(self, double other):
        cdef Vector result = Vector(self.x/other, self.y/other, self.z/other)
    def __truediv__(self, other : cython.double) -> Vector:
        """
        Division by scalar
        """
        return self.div(other)
    def __itruediv__(self, other : cython.double) -> Vector:
        """
        In-place division by scalar
        """
        self.x/= other
        self.y/= other
        self.z/= other
        return self

    cdef Vector neg(self):
        cdef Vector result = self.mul(-1)
        return result
    def __neg__(self) -> Vector:
        return self.neg()

    def __eq__(self, other : Any) -> bool:
        if isinstance(other, Vector):
            return self.mod == other.mod
        else:
            return False

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    cpdef Vector cross(Vector self, Vector other):
        """
        Vectorial product
        """
        return Vector(
            self.y*other.z-self.z*other.y,
            self.z*other.x-self.x*other.z,
            self.x*other.y-self.y*other.x,
        )

    cpdef void rotate_x(Vector self, double ang):
        cdef double ty = self.y
        cdef double tz = self.z
        cdef double s_ang = sin(ang)
        cdef double c_ang = cos(ang)
        self.y = ty*c_ang - tz*s_ang
        self.z = ty*s_ang + tz*c_ang

    cpdef Vector rotated_x(Vector self, double ang):
        cdef double ty = self.y
        cdef double tz = self.z
        cdef double s_ang = sin(ang)
        cdef double c_ang = cos(ang)
        return Vector(
            self.x,
            ty*c_ang - tz*s_ang,
            ty*s_ang + tz*c_ang,
        )

    cpdef void rotate_y(Vector self, double ang):
        cdef double tz = self.z
        cdef double tx = self.x
        cdef double s_ang = sin(ang)
        cdef double c_ang = cos(ang)
        self.z = tz*c_ang - tx*s_ang
        self.x = tz*s_ang + tx*c_ang

    cpdef Vector rotated_y(Vector self, double ang):
        cdef double tz = self.z
        cdef double tx = self.x
        cdef double s_ang = sin(ang)
        cdef double c_ang = cos(ang)
        return Vector(
            tz*s_ang + tx*c_ang,
            self.y,
            tz*c_ang - tx*s_ang,
        )

    cpdef void rotate_z(Vector self, double ang):
        cdef double tx = self.x
        cdef double ty = self.y
        cdef double s_ang = sin(ang)
        cdef double c_ang = cos(ang)
        self.x = tx*c_ang - ty*s_ang
        self.y = tx*s_ang + ty*c_ang

    cpdef Vector rotated_z(Vector self, double ang):
        cdef double tx = self.x
        cdef double ty = self.y
        cdef double s_ang = sin(ang)
        cdef double c_ang = cos(ang)
        return Vector(
            tx*c_ang - ty*s_ang,
            tx*s_ang + ty*c_ang,
            self.z,
        )

    cdef double cmod_sqr(self):
        return self.dot(self)
    @property
    def mod_sqr(self) -> cython.double:
        """
        Get square or vector module
        """
        return self.cmod_sqr()

    cdef double cmod(self):
        return sqrt(self.cmod_sqr())
    @property
    def mod(self) -> cython.double:
        """
        Get vector module
        """
        return self.cmod()

    cpdef void normalize(self):
        """
        Normalize vector in-place
        """
        mod = self.cmod()
        self.x/= mod
        self.y/= mod
        self.z/= mod

    cpdef Vector normalized(self):
        """
        Return normalized vector
        """
        return self.copy()/self.cmod()

    def __abs__(self) -> cython.double:
        return self.cmod()

    cpdef Vector copy(self):
        return Vector(
            self.x,
            self.y,
            self.z,
        )

    def __reduce__(self):
        return (create_vector, (self.x, self.y, self.z))
