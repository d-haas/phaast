from abc import ABC, abstractmethod
from phaast.structure import Molecule, Structure


class Calculator(ABC):
    @abstractmethod
    def optimize(self, structure : Structure) -> Molecule | None:...

    @abstractmethod
    def __hash__(self) -> int:...
