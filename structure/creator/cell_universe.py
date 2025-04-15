
from typing import Tuple
import itertools
import numpy as np
from numpy.typing import NDArray

class CellUniverse(list[list[list[int]]]): #Fuck speed, I want readability (list for the win)
    """
        A base class to define the cell-separated universe
        used to place and model each element of the population
    """
    def __init__(
        self,
        cell_size : float,
        cell_num : int | Tuple[int, int, int],
        atom_radius : float,
    ):
        universe_size = (cell_num,cell_num,cell_num) if isinstance(cell_num, int) else cell_num

        super().__init__(
            [[[0]*universe_size[0]]*universe_size[1]]*universe_size[2],
        )

        self.cell_size = cell_size
        self.cell_num = cell_num
        self.atom_radius = atom_radius


