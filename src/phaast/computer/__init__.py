from __future__ import annotations

from abc import ABC, abstractmethod
import multiprocessing, sys

if sys._is_gil_enabled():
    from multiprocessing import Pool
else:
    from multiprocessing.dummy import Pool

from typing import Any, Callable, Iterable, overload

from phaast.structure import Molecule, Structure

from phaast.calculators import Calculator

class BaseComputer(ABC):
    cpu_count_limit : int # Maximum number of processes the computer can handle (or performs the best)
    calculators : dict[str, Calculator] 

    @abstractmethod
    def optimize(self, calculator_key : str, structures : Iterable[Structure]) -> list[Molecule | None]: ...

    @abstractmethod
    def parallelize[T](self, args : Iterable[tuple[Any, ...]] | int, func : Callable[..., T], chunksize : int | None = None) -> list[T]: ...


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
    def optimize(self, calculator_key : str, structures : Structure | Iterable[Structure], chunksize : int | None = None) -> Molecule | None | list[Molecule | None]:
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
                size_args = sum((1 for _ in structures),)
                chunk_size = chunksize if chunksize else max(round((size_args/self.cpu_count_limit)/100), 1)
                molecules : list[Molecule | None] = pool.map(
                    self.calculators[calculator_key].optimize,
                    structures,
                    chunksize = chunk_size,
                )
            return [mol for mol in molecules]

    def parallelize[T](self, args : Iterable[tuple[Any, ...]] | int, func : Callable[..., T], chunksize : int | None = None) -> list[T]:
        """
        Run any task in parallel
        Since its supposed to run with the genetic algorithm,
        chunksize was tuned for that purpose
        (huge quantities of processes (>>> cpu_count))
        """

        with Pool(self.cpu_count_limit) as pool:
            if isinstance(args, int):
                return pool.starmap(
                    func,
                    [() for _ in range(args)],
                    chunksize=chunksize if chunksize else args//self.cpu_count_limit,
                )
            else:
                size_args = sum((1 for _ in args),)
                chunk_size = chunksize if chunksize else max(round((size_args/self.cpu_count_limit)/100), 1)
                return pool.starmap(
                    func,
                    args,
                    chunksize = chunk_size,
                )

    def add_calculator(self, key : str, calculator : Calculator) -> None:
        self.calculators[key] = calculator
