# cython: freethreading_compatible = True
from __future__ import annotations
from typing import Any, Iterator, Union
import cython, struct

if cython.compiled:
    from cython.cimports.libc.math import sqrt, sin, cos # type: ignore
else:
    from math import sqrt, sin, cos

@cython.ccall
def create_vector(
    x : cython.double = 0.0,
    y : cython.double = 0.0,
    z : cython.double = 0.0,
) -> Vector:
    return Vector(x, y, z)


@cython.auto_pickle(True)
@cython.cclass
class Vector:
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

    @cython.cfunc
    def add(self, other : Vector) -> Vector:
        result : Vector = Vector(
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

    @cython.cfunc
    def sub(self, other : Vector) -> Vector:
        result : Vector = Vector(
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

    @cython.cfunc
    def dot(self, other : Vector) -> cython.double:
        return self.x*other.x + self.y*other.y + self.z*other.z

    @cython.cfunc
    def mul(self, other : cython.double) -> Vector:
        result : Vector = Vector(other * self.x, other * self.y, other * self.z)
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

    @cython.cfunc
    def div(self, other : cython.double) -> Vector:
        result : Vector = Vector(self.x/other, self.y/other, self.z/other)
        return result

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

    @cython.cfunc
    def neg(self) -> Vector:
        result : Vector = self.mul(-1)
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

    @cython.ccall
    def cross(self, other : Vector) -> Vector:
        """
        Vectorial product
        """
        return Vector(
            self.y*other.z-self.z*other.y,
            self.z*other.x-self.x*other.z,
            self.x*other.y-self.y*other.x,
        )

    @cython.ccall
    @cython.returns(cython.void)
    def rotate_x(self, ang : cython.double):
        cython.declare(
            ty = cython.double,
            tz = cython.double,
            s_ang = cython.double,
            c_ang = cython.double,
        )
        ty = self.y
        tz = self.z
        s_ang = sin(ang)
        c_ang = cos(ang)
        self.y = ty*c_ang - tz*s_ang
        self.z = ty*s_ang + tz*c_ang

    @cython.ccall
    def rotated_x(self, ang : cython.double) -> Vector:
        cython.declare(
            ty = cython.double,
            tz = cython.double,
            s_ang = cython.double,
            c_ang = cython.double,
        )
        ty = self.y
        tz = self.z
        s_ang = sin(ang)
        c_ang = cos(ang)
        return Vector(
            self.x,
            ty*c_ang - tz*s_ang,
            ty*s_ang + tz*c_ang,
        )

    @cython.ccall
    @cython.returns(cython.void)
    def rotate_y(self, ang : cython.double):
        cython.declare(
            tz = cython.double,
            tx = cython.double,
            s_ang = cython.double,
            c_ang = cython.double,
        )
        tz = self.z
        tx = self.x
        s_ang = sin(ang)
        c_ang = cos(ang)
        self.z = tz*c_ang - tx*s_ang
        self.x = tz*s_ang + tx*c_ang

    @cython.ccall
    def rotated_y(self, ang : cython.double) -> Vector:
        cython.declare(
            tz = cython.double,
            tx = cython.double,
            s_ang = cython.double,
            c_ang = cython.double,
        )
        tz = self.z
        tx = self.x
        s_ang = sin(ang)
        c_ang = cos(ang)
        return Vector(
            tz*s_ang + tx*c_ang,
            self.y,
            tz*c_ang - tx*s_ang,
        )

    @cython.ccall
    @cython.returns(cython.void)
    def rotate_z(self, ang : cython.double):
        cython.declare(
            tx = cython.double,
            ty = cython.double,
            s_ang = cython.double,
            c_ang = cython.double,
        )
        tx = self.x
        ty = self.y
        s_ang = sin(ang)
        c_ang = cos(ang)
        self.x = tx*c_ang - ty*s_ang
        self.y = tx*s_ang + ty*c_ang

    @cython.ccall
    def rotated_z(self, ang : cython.double) -> Vector:
        cython.declare(
            tx = cython.double,
            ty = cython.double,
            s_ang = cython.double,
            c_ang = cython.double,
        )
        tx = self.x
        ty = self.y
        s_ang = sin(ang)
        c_ang = cos(ang)
        return Vector(
            tx*c_ang - ty*s_ang,
            tx*s_ang + ty*c_ang,
            self.z,
        )

    @cython.cfunc
    def cmod_sqr(self) -> cython.double:
        return self.dot(self)

    @property
    def mod_sqr(self) -> cython.double:
        """
        Get square or vector module
        """
        return self.cmod_sqr()

    @cython.cfunc
    def cmod(self) -> cython.double:
        return sqrt(self.cmod_sqr())

    @property
    def mod(self) -> cython.double:
        """
        Get vector module
        a
        """
        return self.cmod()

    @cython.ccall
    @cython.returns(cython.void)
    def normalize(self):
        """
        Normalize vector in-place
        """
        mod : cython.double = self.cmod()
        self.x/= mod
        self.y/= mod
        self.z/= mod

    @cython.ccall
    def normalized(self) -> Vector:
        """
        Return normalized vector
        """
        return self.copy()/self.cmod()

    def __abs__(self) -> cython.double:
        return self.cmod()

    @cython.ccall
    def copy(self) -> Vector:
        return Vector(
            self.x,
            self.y,
            self.z,
        )

    def as_bytes(self) -> bytes:
        return struct.pack(
            b"ddd",
            self.x,
            self.y,
            self.z,
        )

    @classmethod
    def from_bytes(cls, data : bytes) -> Vector:
        return Vector(*struct.unpack_from(b"ddd", data))

    def as_data(self) -> tuple:
        return (self.x, self.y, self.z)

    @classmethod
    def from_data(cls, data : tuple | list) -> Vector:
        return Vector(*data)

    def __reduce__(self):
        return (create_vector, (self.x, self.y, self.z))
