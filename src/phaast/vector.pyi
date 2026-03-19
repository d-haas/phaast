from typing import Any, Iterator, Union, overload

type VectorData = tuple[float, float, float]

class Vector:
    x : float
    y : float
    z : float

    @overload
    def __init__(self, x : float, y : float, z : float):...
    @overload
    def __init__(self, xyz : float):...
    @overload
    def __init__(self):...
    def __init__(self, *args : float):...

    def __getitem__(self, key : int) -> float:
        """
        Get item function, in case its needed
        to index by attribute number
        """
        pass

    def __setitem__(self, key : int, value : float) -> None:...

    def __iter__(self) -> Iterator[float]:
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
    def __mul__(self, other : 'Vector') -> float:...
    @overload
    def __mul__(self, other : float) -> 'Vector':...
    def __mul__(self, other : Union['Vector',float]) -> Union[float, 'Vector']:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        pass

    @overload
    def __rmul__(self, other : float) -> 'Vector':...
    @overload
    def __rmul__(self, other : 'Vector') -> 'Vector':...
    def __rmul__(self, other : Union['Vector', float]) -> Union[float, 'Vector']:
        """
        This function contains both vector multiplication by scalar
        and scalar product, depending on the other variable
        """
        pass

    def __imul__(self, other : float) -> 'Vector':
        """
        In-place multiplication by scalar
        """
        pass

    def __truediv__(self, other : float) -> 'Vector':
        """
        Division by scalar
        """
        pass

    def __itruediv__(self, other : float) -> 'Vector':
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

    def __repr__(self) -> str:...

    def __str__(self) -> str:...

    def cross(self, other : 'Vector') -> 'Vector':
        """
        Vectorial product
        """
        pass

    def rotate_x(self, ang : float) -> None:
        """
        Rotate vector over x-axis
        """

    def rotated_x(self, ang : float) -> Vector:
        """
        Return rotated vector over x-axis
        """

    def rotate_y(self, ang : float) -> None:
        """
        Rotate vector over y-axis
        """

    def rotated_y(self, ang : float) -> Vector:
        """
        Return rotated vector over y-axis
        """

    def rotate_z(self, ang : float) -> None:
        """
        Rotate vector over z-axis
        """

    def rotated_z(self, ang : float) -> Vector:
        """
        Return rotated vector over z-axis
        """


    @property
    def mod_sqr(self) -> float:
        """
        Get square or vector module
        """
        pass

    @property
    def mod(self) -> float:
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

    def __abs__(self) -> float: ...

    def as_data(self) -> VectorData: ...

    def copy(self) -> 'Vector':
        """
        Returns an identical copy of the vector
        in a different address
        """
        pass

    def __getstate__(self) -> tuple[float, float, float]: ...

    def __setstate__(self, state : tuple[float, float, float]) -> None:...
