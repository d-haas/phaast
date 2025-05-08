import cython
from typing import Any, Iterator, Union, overload

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
    def __mul__(self, other : 'Vector') -> cython.double:...
    @overload
    def __mul__(self, other : cython.double) -> 'Vector':...
    def __mul__(self, other : Union['Vector',cython.double]) -> Union[cython.double, 'Vector']:
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
                f"Multiplication only accepts a Vector or cython.double, not {type(other)}."
            )

    @overload
    def __rmul__(self, other : cython.double) -> 'Vector':...
    @overload
    def __rmul__(self, other : 'Vector') -> 'Vector':...
    def __rmul__(self, other : Union['Vector', cython.double]) -> Union[cython.double, 'Vector']:
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
                f"Multiplication only accepts a Vector or cython.double, not {type(other)}."
            )

    def __imul__(self, other : cython.double) -> 'Vector':
        """
        In-place multiplication by scalar
        """
        if isinstance(other, cython.double):
            self.x*= other
            self.y*= other
            self.z*= other
            return self
        else:
            raise TypeError(
                f"In-place multiplication only accepts cython.double, not {type(other)}."
            )


    def __truediv__(self, other : cython.double) -> 'Vector':
        """
        Division by scalar
        """
        return self.__class__(
            self.x/other,
            self.y/other,
            self.z/other,
        )
    def __itruediv__(self, other : cython.double) -> 'Vector':
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

    def __repr__(self) -> cython.basestring:
        return f"Vector({self.x}, {self.y}, {self.z})"

    def __str__(self) -> cython.basestring:
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
    def squared_mod(self) -> cython.double:
        """
        Get square or vector module
        """
        return self.x*self.x + self.y*self.y + self.z*self.z

    @property
    def mod(self) -> cython.double:
        """
        Get vector module
        """
        return self.squared_mod**.5

    def normalize(self) -> None:
        """
        Normalize vector in-place
        """
        mod = self.mod
        self.x/= mod
        self.y/= mod
        self.z/= mod

    def normalized(self) -> 'Vector':
        """
        Return normalized vector
        """
        return self.copy()/self.mod

    def __abs__(self) -> cython.double:
        return self.mod

    @cython.ccall
    def copy(self) -> 'Vector':
        return self.__class__(
            self.x,
            self.y,
            self.z,
        )
