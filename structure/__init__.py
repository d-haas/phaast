from typing import Iterable, Self
import structure.constants as constants
import itertools, bisect
from vec import Vector
from math import sqrt

class Atom(tuple[int, Vector]):

    def __new__(cls, atomic_number : int, pos : Vector):
        return super().__new__(cls, (atomic_number, pos.copy()))

    @property
    def z(self) -> int:
        return self[0]
    @property
    def pos(self) -> Vector:
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
    def cm(self) -> Vector:
        """
        Return structure's center of mass
        """
        # Sum vector to accumulate ponderate positions (A.U.)
        sum_vector : Vector = Vector(0,0,0)

        # Accumulated mass of all atoms (A.U.)
        mass_counter = 0

        # Adds positions to sum_vector and atomic masses to center of mass
        for atom in self:
            sum_vector+= atom.pos * atom.mass
            mass_counter+= atom.mass

        if mass_counter:
            sum_vector/= mass_counter
            return sum_vector
        else:
            raise Exception("No atoms in structure")

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
        ### FOR EACH STRUCTURE                                                           ###
        ####################################################################################
        self_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(self, 2):
            diff = atom_i.pos - atom_j.pos
            bisect.insort(
                self_dists,
                diff.squared_mod,
            )
        other_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(other, 2):
            diff = atom_i.pos - atom_j.pos
            bisect.insort(
                other_dists,
                diff.squared_mod,
            )

        ### Get difference between each distance in each molecule (squared) ###
        distances_squared_diff : list[float] = [
            (self_dist - other_dist)**2
            for self_dist, other_dist
            in zip(
                self_dists,
                other_dists
            )
        ]

        # Calculate final value of Grigoryan-Springborn algorithm
        q : float = sqrt( ( 2/(atoms_num*(atoms_num-1)) ) * sum(distances_squared_diff) )
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
