from typing import Iterable, Self, cast
import structure.constants as constants
import vector, itertools, bisect
from math import sqrt

class Atom:
    z : int
    pos : vector.VectorObject3D

    def __init__(self, atomic_number : int, pos : vector.VectorObject3D):
        self.z = atomic_number
        self.pos = pos

    @property
    def name(self) -> str:
        return constants.atomic_name[self.z]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.name} ({self.pos.x}, {self.pos.y}, {self.pos.z})"

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
        assert len(self) == len(other), "Both structure should have the same number of atoms"

        atoms_num : int = len(self)

        ### SUM DISTANCES BETWEEN ATOMS OF EACH STRUCTURE AND STORE IT IN A ORDERED LIST ###
        self_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(self, 2):
            diff = cast(vector.VectorObject3D, atom_i.pos - atom_j.pos)
            bisect.insort(
                self_dists,
                diff.mag,
            )
        other_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(other, 2):
            diff = cast(vector.VectorObject3D, atom_i.pos - atom_j.pos)
            bisect.insort(
                other_dists,
                diff.mag,
            )
        ####################################################################################

        # Get difference between each distance in each molecule (squared)
        distances_squared_diff : list[float] = [(i-j)**2 for i, j  in zip(self_dists, other_dists)]

        q : float = sqrt( ( 2/(atoms_num*(atoms_num-1)) ) * sum(distances_squared_diff) )
        s : float = 1 / (1 + q)

        return s
