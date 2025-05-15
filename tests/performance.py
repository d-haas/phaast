import vec
import time
import cython
from typing import Any, Iterator, Union, overload

class Vector:
    __slots__ = ("x", "y", "z")

    def __init__(self, *args : float):
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

    def __getitem__(self, key : int) -> float:
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

    def __setitem__(self, key : int, value : float) -> None:
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

    def __iter__(self) -> Iterator[float]:
        """
        Iter over vector
        """
        return iter(
            (
                self.x,
                self.y,
                self.z,
            ),
        )

    def __add__(self, other : 'Vector') -> 'Vector':
        """
        Vector addition
        """
        return self.__class__(
            self.x+other.x,
            self.y+other.y,
            self.z+other.z,
        )
    def __iadd__(self, other : 'Vector') -> 'Vector':
        """
        In-place vector addition
        """
        self.x+= other.x
        self.y+= other.y
        self.z+= other.z
        return self

    def __sub__(self, other : 'Vector') -> 'Vector':
        """
        Vector subtraction
        """
        return self.__class__(
            self.x-other.x,
            self.y-other.y,
            self.z-other.z,
        )
    def __isub__(self, other : 'Vector') -> 'Vector':
        """
        In-place vector subtraction
        """
        self.x-= other.x
        self.y-= other.y
        self.z-= other.z
        return self

    @overload
    def __mul__(self, other : 'Vector') -> float:...
    @overload
    def __mul__(self, other : float) -> 'Vector':...
    def __mul__(self, other : Union['Vector',float]) -> Union[float, 'Vector']:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        if isinstance(other, Vector):
            return self.x*other.x + self.y*other.y + self.z*other.z
        elif isinstance(other, float):
            return self.__class__(
                other*self.x,
                other*self.y,
                other*self.z,
            )
        else:
            raise TypeError(
                f"Multiplication only accepts a Vector or float, not {type(other)}."
            )

    @overload
    def __rmul__(self, other : float) -> 'Vector':...
    @overload
    def __rmul__(self, other : 'Vector') -> 'Vector':...
    def __rmul__(self, other : Union['Vector', float]) -> Union[float, 'Vector']:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        if isinstance(other, Vector):
            return self.x*other.x + self.y*other.y + self.z*other.z
        elif isinstance(other, float):
            return self.__class__(
                other*self.x,
                other*self.y,
                other*self.z,
            )
        else:
            raise TypeError(
                f"Multiplication only accepts a Vector or float, not {type(other)}."
            )

    def __imul__(self, other : float) -> 'Vector':
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
                f"In-place multiplication only accepts float, not {type(other)}."
            )


    def __truediv__(self, other : float) -> 'Vector':
        """
        Division by scalar
        """
        return self.__class__(
            self.x/other,
            self.y/other,
            self.z/other,
        )
    def __itruediv__(self, other : float) -> 'Vector':
        """
        In-place division by scalar
        """
        self.x/= other
        self.y/= other
        self.z/= other
        return self

    def __neg__(self) -> 'Vector':
        return self.__class__(
            -self.x,
            -self.y,
            -self.z,
        )

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
    def cross(self, other : 'Vector') -> 'Vector':
        """
        Vectorial product
        """
        return self.__class__(
            self.y*other.z-self.z*other.y,
            self.z*other.x-self.x*other.z,
            self.x*other.y-self.y*other.x,
        )

    @property
    def mod_sqr(self) -> float:
        """
        Get square or vector module
        """
        return self.x*self.x + self.y*self.y + self.z*self.z

    @property
    def mod(self) -> float:
        """
        Get vector module
        """
        return self.mod_sqr**.5

    def __abs__(self) -> float:
        return self.mod

    @cython.ccall
    def copy(self) -> 'Vector':
        return self.__class__(
            self.x,
            self.y,
            self.z,
        )

def run():
    VECTOR_VALUE = 1.2

    start_var = time.monotonic_ns()
    a = Vector(VECTOR_VALUE)
    end_var = time.monotonic_ns()
    start_sum = time.monotonic_ns()
    for _ in range(100000):
        a+= a
    end_sum = time.monotonic_ns()
    print(f"Pure python variable creation time was {(end_var-start_var)/1e3} µs")
    print(f"Pure python sum time was {(end_sum-start_sum)/1e3} µs")

    start_var_c = time.monotonic_ns()
    a = vec.Vector(VECTOR_VALUE)
    end_var_c = time.monotonic_ns()
    start_sum_c = time.monotonic_ns()
    for _ in range(100000):
        a+= a
    end_sum_c = time.monotonic_ns()
    print(f"Cython variable creation time was {(end_var_c-start_var_c)/1e3} µs")
    print(f"Cython sum time was {(end_sum_c-start_sum_c)/1e3} µs")

    print(f"Cython is {round((end_sum-start_sum)/(end_sum_c-start_sum_c), 2)} times faster than pure python.")
