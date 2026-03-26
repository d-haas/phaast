from abc import abstractmethod

from phaast.structure import Structure
from phaast.utils import ObjectData


class Mutator:
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def __call__(self, struct : Structure) -> Structure: ...

    @abstractmethod
    def as_data(self) -> ObjectData: ...

class DisplacementMutator(Mutator):
    num : int
    min_displacement : float
    max_displacement : float

    def __init__(self, num : int = 1, min_displacement : float = 0.7, max_displacement : float = 2.3): ...

    def __call__(self, structure : Structure) -> Structure: ...

    def as_data(self) -> ObjectData: ...


class PermuteMutator(Mutator):
    num : int
    def __init__(self, num : int): ...

    def __call__(self, structure : Structure) -> Structure: ...

    def as_data(self) -> ObjectData: ...

class TwistMutator(Mutator):
    min_angle : float
    max_angle : float

    def __init__(self, min_angle : float, max_angle : float): ...

    def __call__(self, structure : Structure) -> Structure: ...

    def as_data(self) -> ObjectData: ...
