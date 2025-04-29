
from typing import Self, overload


class Vector:
    x : float
    y : float
    z : float
    def __init__(self, *args : float):
        match len(args):
            case 0:
                self.x, self.y, self.z = 0, 0, 0
            case 1:
                self.x, self.y, self.z = args*3
            case 3:
                self.x, self.y, self.z = args
            case _:
                raise ValueError(
                    f"There should be 0, 1 or 3 arguments, not {len(args)}",
                )

    def __add__(self, other : Self) -> Self:
        return self.__class__(
            self.x+other.x,
            self.y+other.y,
            self.z+other.z,
        )

    def __sub__(self, other : Self) -> Self:
        return self.__class__(
            self.x-other.x,
            self.y-other.y,
            self.z-other.z,
        )

    @overload
    def __mul__(self, other : Self) -> float:...
    @overload
    def __mul__(self, other : float) -> Self:...
    def __mul__(self, other : Self | float) -> Self | float:
        if isinstance(other, Vector):
            return self.x*other.x + self.y+other.y + self.z+other.z
        elif isinstance(other, float):
            return self.__class__(
                other*self.x,
                other*self.y,
                other*self.z,
            )
        else:
            raise ValueError(
                f"Multiplication only accepts a Vector or float, not {type(other)}."
            )

    def __div__(self, other : float) -> Self:
        return self.__class__(
            self.x/other,
            self.y/other,
            self.z/other,
        )

    def __



