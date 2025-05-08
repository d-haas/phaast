import cython
from typing import Iterable, Optional, Self
import structure.constants as constants
import itertools, bisect
from vec cimport Vector

cdef class Atom:
    def __init__(self, atomic_number : cython.uint, pos : Optional[Vector] = None):
        self.z = atomic_number
        if pos:
            self.pos = pos.copy()
        else:
            self.pos = Vector()

    @staticmethod
    cdef Atom create(unsigned int atomic_number, Vector pos):
        cdef Atom new_atom = Atom.__new__(Atom)

        new_atom.z = atomic_number
        new_atom.pos = pos.copy()

        return new_atom

    @property
    def name(self) -> cython.basestring:
        return constants.AtomicName[self.z]

    @property
    def mass(self) -> cython.double:
        return constants.AtomicMass[self.z]

    def __repr__(self) -> cython.basestring:
        return str(self)

    def __str__(self) -> cython.basestring:
        return f"{self.name} ({', '.join([str(round(self.pos[i], 1)) for i in range(3)])})"

    cpdef Atom copy(self):
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

    def __repr__(self) -> cython.basestring:
        self_text = str(self).replace("\n", "\n\t")
        return f"Structure\n\t{self_text}"

    def __str__(self) -> cython.basestring:
        return "\n".join((str(atom) for atom in self))

    def is_equal_to(self, other : Self) -> bool:
        if len(self)==len(other):
            other_count = other.element_count()
            for z, quantity in self.element_count().items():
                if z in other_count:
                    if quantity == other_count[z]:
                        continue
                    else:
                        return False
                else:
                    return False
            return True

        else:
            return False

    def element_count(self) -> dict[int, int]:
        """
        Returns dict with quantity of each atom in each molecule
        """
        r : dict[int, int] = {}
        for atom in self:
            if atom.z in r:
                r[atom.z]+= 1
            else:
                r[atom.z] = 1
        return r

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

    def compare(self, other : Self) -> cython.double:
        """
        Compare different structures using the
        Grigoryan-Springborn algorithm
        DOI: 10.1140/epjd/e2005-00141-6
        Equation (1)
        """
        atoms_num : cython.uint = len(self) # Number of atoms in structure

        #Check if number of atoms is the same in both structures
        assert atoms_num == len(other), "Both structure should have the same number of atoms"

        ####################################################################################
        ### SUM DISTANCES BETWEEN ATOMS OF EACH STRUCTURE AND STORE IT IN A ORDERED LIST ###
        ### FOR EACH STRUCTURE                                                           ###
        ####################################################################################
        self_dists : list[cython.double] = []
        for atom_i, atom_j in itertools.combinations(self, 2):
            diff : Vector = atom_i.pos - atom_j.pos
            bisect.insort(
                self_dists,
                diff.squared_mod,
            )
        other_dists : list[cython.double] = []
        for atom_i, atom_j in itertools.combinations(other, 2):
            diff = atom_i.pos - atom_j.pos
            bisect.insort(
                other_dists,
                diff.squared_mod,
            )

        ### Get difference between each distance in each molecule (squared) ###
        distances_squared_diff : list[cython.double] = [
            (self_dist - other_dist)**2
            for self_dist, other_dist
            in zip(
                self_dists,
                other_dists
            )
        ]

        # Calculate final value of Grigoryan-Springborn algorithm
        q : cython.double = ( ( 2/(atoms_num*(atoms_num-1)) ) * sum(distances_squared_diff) )**.5
        s : cython.double = 1 / ( 1 + q )

        return s
    
    def copy(self) -> Self:
        return self.__class__(
            (
                atom.copy()
                for atom
                in self
            ),
        )
