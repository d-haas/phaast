from abc import ABC, abstractmethod

from phaast.structure import Structure
from phaast.structure.constants import *
from phaast.utils import ObjectData

#@check_types
class Migrator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def __call__(self) -> Structure: ...

    @abstractmethod
    def as_data(self) -> ObjectData: ...
