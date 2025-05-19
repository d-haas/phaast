from abc import ABC, abstractmethod
import multiprocessing
from multiprocessing.dummy import Pool
from typing import Iterable
from calculators import Calculator
from structure import Molecule, Structure

class BaseComputer(ABC):
    cpu_count_limit : int # Maximum number of processes the computer can handle (or performs the best)
    memory_limit : int # Maximum memory the software can use (in KiB)
    calculators : list[Calculator] 
    max_processes : dict[Calculator, int] # Calculators that will be used the for software

    @abstractmethod
    def optimize(self, calculator : type[Calculator], structures : Iterable[Structure]) -> list[Molecule]:
        pass

class Computer(BaseComputer):
    def __init__(
        self,
        cpu_count_limit : int,
        memory_limit : int,
        calculators : Iterable[Calculator],
        structure_type : Structure,
    ):
        # Set core count on computer automatically if it was not set
        max_core_count = multiprocessing.cpu_count()
        assert isinstance(cpu_count_limit, int) and 0<=cpu_count_limit<=multiprocessing.cpu_count(), "core_count should be an int and between 0 and the number of cores available"
        self.core_count = max_core_count if cpu_count_limit == 0 else cpu_count_limit

        # Set memory limit based on physical memory accessible on pc
        assert isinstance(memory_limit, int) and 0<=memory_limit, "Memory limit should be 0 or above"
        if memory_limit == 0:
            with open("/proc/meminfo") as mem_info_file:
                for line in mem_info_file.readlines():
                    if "MemTotal:" in line:
                        memory_limit = int(line.split()[1])
            if memory_limit == 0:
                raise Exception("Could not find MemTotal in /proc/mem_info")
        self.memory_limit = memory_limit

        # Get maximum memory consumed per structure optimization
        self.max_processes = {}
        for calculator in calculators:
            self.max_processes[calculator] = max(
                *[
                    calculator.measure_optimization_memory_usage(structure_type)
                    for _ in range(10)
                ]
            )

        def optimize(self, calculator : type[Calculator], structures : Iterable[Structure]) -> list[Molecule]:
            with Pool(self.max_processes[calculator]) as pool:
                return pool.map(
                    calculator.optimize,
                    structures,
                )
