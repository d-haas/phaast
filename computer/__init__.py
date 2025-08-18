from abc import ABC, abstractmethod
import multiprocessing
from multiprocessing.dummy import Pool
import threading
from typing import Iterable
from calculators import Calculator
from structure import Molecule, Structure
import socket
import struct
#from structure import Atom, Base
#import math

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
        #memory_limit : int,
        #calculators : Iterable[Calculator],
        #structure_type : Base,
    ):
        # Set core count on computer automatically if it was not set
        max_core_count = multiprocessing.cpu_count()
        assert isinstance(cpu_count_limit, int) and 0<=cpu_count_limit<=max_core_count, "core_count_limit should be an int and between 0 and the number of cores available"
        self.cpu_count_limit = max_core_count if cpu_count_limit == 0 else cpu_count_limit

        # Set memory limit based on physical memory accessible on pc
        """
        assert isinstance(memory_limit, int) and 0<=memory_limit, "Memory limit should be 0 or above"
        if memory_limit == 0:
            with open("/proc/meminfo") as mem_info_file:
                for line in mem_info_file.readlines():
                    if "MemTotal:" in line:
                        memory_limit = int(line.split()[1])
            if memory_limit == 0:
                raise Exception("Could not find MemTotal in /proc/mem_info")
        self.memory_limit = memory_limit
        """

        # Get maximum memory consumed per structure optimization
        """
        self.max_processes = {}
        for calculator in calculators:
            self.max_processes[calculator] = min(
                math.floor(
                    self.memory_limit/max(
                        *[
                            calculator.measure_optimization_memory_usage(
                                Structure([Atom(element.z) for element in structure_type]),
                            )
                            for _ in range(10)
                        ]
                    )
                ),
                self.cpu_count_limit,
            )
        """

    def optimize(self, calculator_key : str, structures : Iterable[Structure]) -> list[Molecule]:
        #with Pool(self.max_processes[calculator]) as pool:
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
