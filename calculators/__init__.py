
from abc import ABC, abstractmethod

from structure import Molecule, Structure


class Calculator(ABC):
    @staticmethod
    @abstractmethod
    def optimize(structure : Structure, charge : int) -> Molecule:
        pass

    @staticmethod
    @abstractmethod
    def measure_memory_usage(structure : Structure, charge : int) -> int:
        pass
