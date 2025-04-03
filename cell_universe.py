
from typing import Tuple
import numpy as np
from numpy.typing import NDArray

def get_circle_cell_pattern(cell_size : float, atom_radius : float) -> NDArray[np.bool_]:
    """
        Create an array filled with the pattern the atom creates on the cell universe
        with the fields.
    """

    # Number of cell the atom radius can reach from the middle
    cell_range : int = int(atom_radius//cell_size)

    # Coordinate of the middle of the pattern array
    middle : int = 1 + cell_range

    # Array of the pattern (to be filled)
    arr : NDArray[np.bool_] = np.ndarray(
        (1 + cell_range*2),
        dtype = int,
    )

    # Filling array fields
    for cell_row in range(1 + cell_range*2):
        for cell_col in range(1 + cell_range*2):
            # Set field to True if its distance to the middle is inferior to the atom radius
            if ((cell_row-middle)**2 + (cell_col-middle)**2) < atom_radius**2:
                arr[cell_row][cell_col] = True
            else:
                arr[cell_row][cell_col] = False

    return arr

class CellUniverse():
    """
        A base class to define the cell-separated universe
        used to place and model the initial population
    """
    def __init__(
        self,
        cell_size : float,
        cell_num : int | Tuple[int, int],
        atom_radius : float,
    ):
        self.cell_size = cell_size
        self.cell_num = cell_num
        self.atom_radius = atom_radius
        self._arr : NDArray[np.int64] = np.ndarray(
            (cell_num)*2 if isinstance(cell_num, int) else cell_num,
            dtype = np.int64,
        )
        self.pattern = get_circle_cell_pattern(cell_size, atom_radius)

    def __getitem__(self, key):
        return self._arr[key]
