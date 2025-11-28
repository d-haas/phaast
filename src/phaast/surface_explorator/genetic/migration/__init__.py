from abc import ABC, abstractmethod

from phaast.structure import Structure
from phaast.structure.constants import *

#@check_types
class Migrator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def __call__(self) -> Structure:
        pass
