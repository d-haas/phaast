from __future__ import annotations

from abc import ABC, abstractmethod
import multiprocessing, sys

if sys._is_gil_enabled():
    from multiprocessing import Pool
else:
    from multiprocessing.dummy import Pool

from typing import Any, Callable, Iterable, TypeVar, TypeVarTuple, overload

from phaast.structure import Molecule, Structure


from phaast.calculators import Calculator

ParA = TypeVarTuple('ParA')
ParT = TypeVar('ParT')

class BaseComputer(ABC):
    cpu_count_limit : int # Maximum number of processes the computer can handle (or performs the best)
    #memory_limit : int # Maximum memory the software can use (in KiB)
    #calculators : list[Calculator] 
    calculators : dict[str, Calculator] 
    #max_processes : dict[Calculator, int] # Calculators that will be used the for software

    @abstractmethod
    def optimize(self, calculator_key : str, structures : Iterable[Structure]) -> list[Molecule | None]:
        pass


class Computer(BaseComputer):
    def __init__(
        self,
        cpu_count_limit : int = 0,
    ):
        # Set core count on computer automatically if it was not set
        max_core_count = multiprocessing.cpu_count()
        assert isinstance(cpu_count_limit, int) and 0<=cpu_count_limit<=max_core_count, "core_count_limit should be an int and between 0 and the number of cores available"
        self.cpu_count_limit = max_core_count if cpu_count_limit == 0 else cpu_count_limit

        #Set calculators dictionary
        self.calculators = {}

    @overload
    def optimize(self, calculator_key : str, structures : Structure) -> Molecule | None:...
    @overload
    def optimize(self, calculator_key : str, structures : Iterable[Structure]) -> list[Molecule | None]:...
    def optimize(self, calculator_key : str, structures : Structure | Iterable[Structure]) -> Molecule | None | list[Molecule | None]:
        """
        Execute Structures optimization for a list of Structures
        turning them into a list of Molecules

        If a single Structure is given as as argument,
        only a single molecule will be returned
        """
        if isinstance(structures, Structure):
            return self.calculators[calculator_key].optimize(structures)

        else:
            with Pool(self.cpu_count_limit) as pool:
                molecules : list[Molecule | None] = pool.map(
                    self.calculators[calculator_key].optimize,
                    structures,
                )
            return [mol for mol in molecules]

    #def parallelize(self, args : Iterable[tuple[Unpack[ParA]]] | int, func : Callable[[Unpack[ParA]], ParT]) -> list[ParT]:
    def parallelize(self, args : Iterable[tuple[Any, ...]] | int, func : Callable[..., ParT], chunksize : int | None = None) -> list[ParT]:
        with Pool(self.cpu_count_limit) as pool:
            if isinstance(args, int):
                return pool.starmap(
                    func,
                    [() for _ in range(args)],
                    chunksize=chunksize,
                )
            else:
                return pool.starmap(
                    func,
                    args,
                    chunksize=chunksize,
                )

    def add_calculator(self, key : str, calculator : Calculator) -> None:
        self.calculators[key] = calculator
