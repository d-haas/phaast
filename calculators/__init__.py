from abc import ABC, abstractmethod
from structure import Molecule, Structure


class Calculator(ABC):
    @abstractmethod
    def optimize(self, structure : Structure) -> Molecule | None:...

    @abstractmethod
    def measure_optimization_memory_usage(self, structure : Structure) -> int:...

    @abstractmethod
    def measure_optimization_time(self, structure : Structure) -> float:...

    @abstractmethod
    def __hash__(self) -> int:...
