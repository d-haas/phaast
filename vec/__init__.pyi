import cython

from typing import Any, Iterator, Union, overload

class Vector:
    x : cython.double
    y : cython.double
    z : cython.double

    @overload
    def __init__(self, x : float, y : float, z : float):...
    @overload
    def __init__(self, xyz : float):...
    @overload
    def __init__(self):...
    def __init__(self, *args : float):...

    def __getitem__(self, key : cython.uint) -> cython.double:
        """
        Get item function, in case its needed
        to index by attribute number
        """
        pass

    def __setitem__(self, key : cython.uint, value : cython.double) -> None:...

    def __iter__(self) -> Iterator[cython.double]:
        """
        Iter over vector
        """
        pass

    def __add__(self, other : 'Vector') -> 'Vector':
        """
        Vector addition
        """
        pass

    def __iadd__(self, other : 'Vector') -> 'Vector':
        """
        In-place vector addition
        """
        pass

    def __sub__(self, other : 'Vector') -> 'Vector':
        """
        Vector subtraction
        """
        pass

    def __isub__(self, other : 'Vector') -> 'Vector':
        """
        In-place vector subtraction
        """
        pass

    @overload
    def __mul__(self, other : 'Vector') -> cython.double:...
    @overload
    def __mul__(self, other : cython.double) -> 'Vector':...
    def __mul__(self, other : Union['Vector',cython.double]) -> Union[cython.double, 'Vector']:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        pass

    @overload
    def __rmul__(self, other : cython.double) -> 'Vector':...
    @overload
    def __rmul__(self, other : 'Vector') -> 'Vector':...
    def __rmul__(self, other : Union['Vector', cython.double]) -> Union[cython.double, 'Vector']:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        pass

    def __imul__(self, other : cython.double) -> 'Vector':
        """
        In-place multiplication by scalar
        """
        pass

    def __truediv__(self, other : cython.double) -> 'Vector':
        """
        Division by scalar
        """
        pass

    def __itruediv__(self, other : cython.double) -> 'Vector':
        """
        In-place division by scalar
        """
        pass

    def __neg__(self) -> 'Vector':
        """
        Return same vector with opposite values
        """
        pass

    def __eq__(self, other : Any) -> bool:
        """
        Compare vectors
        """
        pass

    def __repr__(self) -> cython.basestring:...

    def __str__(self) -> cython.basestring:...

    def cross(self, other : 'Vector') -> 'Vector':
        """
        Vectorial product
        """
        pass

    @property
    def squared_mod(self) -> cython.double:
        """
        Get square or vector module
        """
        pass

    @property
    def mod(self) -> cython.double:
        """
        Get vector module
        """
        pass

    def normalize(self) -> None:
        """
        Normalize vector in-place
        """
        pass

    def normalized(self) -> 'Vector':
        """
        Return normalized vector
        """
        pass

    def __abs__(self) -> cython.double:...

    def copy(self) -> 'Vector':
        """
        Returns an identical copy of the vector
        in a different address
        """
        pass
