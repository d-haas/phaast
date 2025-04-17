from typing import Iterable, Self
import structure.constants as constants
import itertools, bisect
import numpy as np
from numpy.typing import NDArray
from math import sqrt

class Atom:
    z : int
    pos : NDArray[np.float64]

    def __init__(self, atomic_number : int, pos : NDArray[np.float64]):
        self.z = atomic_number
        self.pos = pos

    @property
    def name(self) -> str:
        return constants.atomic_name[self.z]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.name} ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})"

class Structure(tuple[Atom, ...]):
    """
    Main class for representing molecular/cluster
    structures
    """
    def __new__(cls, atoms : Iterable[Atom]):
        return super().__new__(cls, tuple(atoms))

    def __repr__(self) -> str:
        return f"Structure\n\t{str(self).replace("\n", "\n\t")}"

    def __str__(self) -> str:
        return "\n".join((str(atom) for atom in super()))

    def compare(self, other : Self) -> float:
        """
        Compare different structures using the
        Grigoryan-Springborn algorithm
        DOI: 10.1140/epjd/e2005-00141-6
        Equation (1)
        """
        #Check if number of atoms is the same in both structures
        assert len(self) == len(other), "Both structure should have the same number of atoms"

        atoms_num : int = len(self) # Number of atoms in structure

        ####################################################################################
        ### SUM DISTANCES BETWEEN ATOMS OF EACH STRUCTURE AND STORE IT IN A ORDERED LIST ###
        ####################################################################################
        self_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(self, 2):
            diff = atom_i.pos - atom_j.pos
            bisect.insort(
                self_dists,
                sqrt(diff @ diff),
            )
        other_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(other, 2):
            diff = atom_i.pos - atom_j.pos
            bisect.insort(
                other_dists,
                sqrt(diff @ diff),
            )

        ### Get difference between each distance in each molecule (squared) ###
        distances_squared_diff : NDArray[np.float64] = (
            np.array(self_dists) - np.array(other_dists)
        )**2

        q : float = sqrt( ( 2/(atoms_num*(atoms_num-1)) ) * distances_squared_diff.sum() )
        s : float = 1 / (1 + q)

        return s
