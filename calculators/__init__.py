
from abc import ABC, abstractmethod

from structure import Molecule, Structure


class Calculator(ABC):
    @staticmethod
    @abstractmethod
    def optimize(structure : Structure) -> Molecule:
        pass

    @staticmethod
    @abstractmethod
    def measure_optimization_memory_usage(structure : Structure) -> int:
        pass
