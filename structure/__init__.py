from typing import Iterable, Iterator, Optional, Self
from structure.constants import *
import itertools, bisect
from utils.typecheck import check_types
from vec import Vector
import subprocess, tempfile
import struct

class Element:
    """
    Class representing an atomic element
    mostly used for Stoichiometry expressions
    """
    z : AtomicNumber
    def __init__(self, atomic_number : AtomicNumber):
        self.z = atomic_number

    @property
    def symbol(self) -> str:
        """
        Get atomic symbol for element
        """
        return AtomicSymbols[self.z]

    @property
    def mass(self) -> float:
        """
        Get average atomic mass
        (based on isotopic proportions)
        """
        return AtomicMass[self.z]

    @property
    def radius(self) -> float:
        """
        Get atom covalent radius
        (based on same-element bondings)
        """
        return AtomicRadi[self.z]

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return str(self)


class Atom(Element):
    pos : Vector
    def __init__(self, atomic_number : AtomicNumber, pos : Optional[Vector] = None):
        super().__init__(atomic_number)
        if pos:
            self.pos = pos.copy()
        else:
            self.pos = Vector()

    def __str__(self) -> str:
        return f"{self.symbol} ({', '.join([str(round(self.pos[i], 1)) for i in range(3)])})"

    def copy(self) -> Self:
        return self.__class__(
            self.z,
            self.pos.copy(),
        )

    @staticmethod
    def from_xyz_str(line) -> 'Atom':
        s : str = line.replace("\t", "")

        parsed_line : list[str] = s.split()

        return Atom(
            AtomicNumbers[parsed_line[0]],
            Vector(*[
                float(parsed_line[i])
                for i
                in range(1, 4)
            ])
        )


    def to_xyz_str(self) -> str:
        return f"{self.symbol} {self.pos.x} {self.pos.y} {self.pos.z}"

    def to_bytes(self) -> bytes:
        return struct.pack(
            b"Iddd",
            self.z,
            self.pos.x,
            self.pos.y,
            self.pos.z,
        )

class Structure:
    """
    Main class for representing molecular/cluster
    structure geometry
    """
    __charge : int
    __atoms : tuple[Atom, ...]
    @check_types
    def __init__(self, atoms : Iterable[Atom], charge : int = 0):
        self.__charge = charge
        self.__atoms = tuple(atoms)

    def __getitem__(self, key : int) -> Atom:
        return self.__atoms[key]

    def __len__(self) -> int:
        return len(self.__atoms)

    def __iter__(self) -> Iterator[Atom]:
        return iter(self.__atoms)

    def __repr__(self) -> str:
        self_text = str(self).replace("\n", "\n\t")
        return f"Structure\n\t{self_text}"

    def __str__(self) -> str:
        return "\n".join((str(atom) for atom in self.__atoms))

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
        for atom in self.__atoms:
            if atom.z in r:
                r[atom.z]+= 1
            else:
                r[atom.z] = 1
        return r

    @property
    def charge(self) -> int:
        return self.__charge

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
        for atom in self.__atoms:
            sum_vector+= atom.pos * atom.mass
            mass_counter+= atom.mass

        if mass_counter:
            sum_vector/= mass_counter
            return sum_vector
        else:
            raise Exception("No atoms in structure")

    def compare_geometry(self, other : Self) -> float:
        """
        Compare different structures using the
        Grigoryan-Springborn algorithm
        DOI: 10.1140/epjd/e2005-00141-6
        Equation (1)
        """
        atoms_num : int = len(self) # Number of atoms in structure

        #Check if number of atoms is the same in both structures
        assert atoms_num == len(other), "Both structure should have the same number of atoms"

        ####################################################################################
        ### SUM DISTANCES BETWEEN ATOMS OF EACH STRUCTURE AND STORE IT IN A ORDERED LIST ###
        ### FOR EACH STRUCTURE                                                           ###
        ####################################################################################
        self_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(self.__atoms, 2):
            diff : Vector = atom_i.pos - atom_j.pos
            bisect.insort(
                self_dists,
                diff.mod_sqr,
            )
        other_dists : list[float] = []
        for atom_i, atom_j in itertools.combinations(other.__atoms, 2):
            diff = atom_i.pos - atom_j.pos
            bisect.insort(
                other_dists,
                diff.mod_sqr,
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
        q : float = ( ( 2/(atoms_num*(atoms_num-1)) ) * sum(distances_squared_diff) )**.5
        s : float = 1 / ( 1 + q )

        return s
    
    @staticmethod
    def from_xyz(file_path : str, charge : int) -> 'Structure':
        with open(file_path) as xyz_file:
            return Structure.from_xyz_str(xyz_file.read(), charge)

    def to_xyz(self) -> tempfile._TemporaryFileWrapper:
        file = tempfile.NamedTemporaryFile(
            mode = "w+",
            prefix="phaast_xyz_",
            suffix=".xyz"
        )

        file.write(self.to_xyz_str())
        # For some GD reason, the files needs to be read before xtb uses it
        # (????)
        file.read()


        return file

    @staticmethod
    def from_xyz_str(s : str, charge : int) -> 'Structure':
        atoms : list[Atom] = []

        for line in s.splitlines()[2:]:
            atoms.append(
                Atom.from_xyz_str(line)
            )

        return Structure(atoms, charge)

    def to_xyz_str(self) -> str:
        lines : list[str] = [
            str(len(self)),
            "",
        ] + [
            atom.to_xyz_str()
            for atom
            in self.__atoms
        ]

        return "\n".join(lines)

    def plot(self) -> None:
        with self.to_xyz() as xyz_file:
            subprocess.run(
                [
                    "jmol",
                    xyz_file.name,
                ],
            )


    def copy(self) -> Self:
        return self.__class__(
            (
                atom.copy()
                for atom
                in self.__atoms
            ),
        )

    def to_bytes(self) -> bytes:
        r = struct.pack(b"Ii", len(self), self.__charge)

        for atom in self.__atoms:
            r+= atom.to_bytes()

        return r

class Molecule(Structure):
    """
    A class representing a molecule, inheriting from Structure.
    Can be extended with molecule-specific properties and methods.
    """
    energy : float

    def __init__(self, atoms: Iterable[Atom], charge : int, energy : float):
        super().__init__(atoms,  charge)
        self.energy = energy

    @staticmethod
    def from_xyz(file_path: str, charge : int) -> 'Molecule':
        """
        Create a Molecule from a xyz file 
        """
        with open(file_path) as file:
            s : str = file.read()
            return Molecule.from_xyz_str(s, charge)

    @staticmethod
    def from_xyz_str(s : str, charge : int) -> 'Molecule':
        """
        Create a Molecule from a xyz string
        (this operation is exclusive to xtb geometry
        optimization output xyz file)
        """
        lines = s.splitlines()
        energy = float(lines[1].split()[1])
        struct = Structure.from_xyz_str(s, charge)
        return Molecule(
            struct,
            charge,
            energy,
        )

    def to_bytes(self) -> bytes:
        r = struct.pack(b"Iid", len(self), self.__charge, self.energy)

        for atom in self:
            r+= atom.to_bytes()

        return r
