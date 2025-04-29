from typing import Iterable, Self
import structure.constants as constants
import itertools, bisect
import numpy as np
from numpy.typing import NDArray
from math import sqrt

class Atom(tuple[int, NDArray[np.float64]]):

    def __new__(cls, atomic_number : int, pos : NDArray[np.float64]):
        copy_pos = pos.copy()
        copy_pos.flags.writeable = False
        return super().__new__(cls, (atomic_number, copy_pos))

    @property
    def z(self) -> int:
        return self[0]
    @property
    def pos(self) -> NDArray[np.float64]:
        return self[1]

    @property
    def name(self) -> str:
        return constants.AtomicName[self.z]

    @property
    def mass(self) -> float:
        return constants.AtomicMass[self.z]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.name} ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})"

    def copy(self) -> Self:
        return self.__class__(
            self.z,
            self.pos.copy(),
        )

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

    @property
    def cm(self) -> NDArray[np.float64]:
        """
        Return structure's center of mass
        """
        # Sum vector to accumulate ponderate positions (A.U.)
        sum_vector = np.array((0,0,0), dtype=np.float64)

        # Accumulated mass of all atoms (A.U.)
        mass_counter = 0

        # Adds positions to sum_vector and atomic masses to center of mass
        for atom in self:
            sum_vector+= atom.mass * atom.pos
            mass_counter+= atom.mass

        sum_vector/= mass_counter

        return sum_vector

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
    
    def copy(self) -> Self:
        return self.__class__(
            (
                atom.copy()
                for atom
                in self
            )
        )
