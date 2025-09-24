from abc import ABC, abstractmethod
import multiprocessing, sys

if sys._is_gil_enabled():
    from multiprocessing import Pool
else:
    from multiprocessing.dummy import Pool

#import threading
from typing import Iterable, overload
from calculators import Calculator
from structure import Molecule, Structure
import socket

class BaseComputer(ABC):
    cpu_count_limit : int # Maximum number of processes the computer can handle (or performs the best)
    #memory_limit : int # Maximum memory the software can use (in KiB)
    #calculators : list[Calculator] 
    calculators : dict[str, Calculator] 
    #max_processes : dict[Calculator, int] # Calculators that will be used the for software

    @abstractmethod
    def optimize(self, calculator_key : str, structures : Iterable[Structure]) -> list[Molecule]:
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
    def optimize(self, calculator_key : str, structures : Iterable[Structure]) -> list[Molecule]:...
    def optimize(self, calculator_key : str, structures : Structure | Iterable[Structure]) -> Molecule | None | list[Molecule]:
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
            return [mol for mol in molecules if mol]

    def add_calculator(self, key : str, calculator : Calculator) -> None:
        self.calculators[key] = calculator


class RemoteComputerClient(BaseComputer):
    def __init__(self, ip : str, port : int = 3333):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

        self.cpu_count_limit = self.get_cpu_count_limit()

    @abstractmethod
    def optimize(self, calculator_key : str, structures : Iterable[Structure]) -> list[Molecule]:
        pass

    def get_cpu_count_limit(self) -> int:
        self.socket.send(
            b"\1" + b"\0"*8,
        )
        return 0

"""
class RemoteComputerServer(Computer):
    def __init__(
        self,
        cpu_count_limit : int = 0,
        port : int = 3333,
    ):
        super().__init__(cpu_count_limit)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), port))
        self.connector()

    def connector(self) -> None:
        while True:
            conn, addr = self.socket.accept()
            data : bytes = conn.recv(9)
            if not data: break
            conn.send(data) # Server end of handshake
            threading.Thread(
                target = self.optimization_listener,
                args = (conn,),
            ).run()

    def optimization_listener(self, connection : socket.socket):
        while True:
            data : bytes = connection.recv(9)
            pass
"""
