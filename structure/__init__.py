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
        """
        Sets only atomic number for element
        """
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

class Base:
    elements : tuple[Element, ...]

    def __init__(self, elements : Iterable[Element] | str):
        """
        Create base (alias to chemical composition)
        of a molecule
        """
        if isinstance(elements, str):
            self.elements = self.parse_formula(elements)
        else:
            self.elements = tuple(elements)

    def __iter__(self) -> Iterator[Element]:
        # Iterate over Base
        return iter(self.elements)

    def parse_formula(self, formula : str) -> tuple[Element, ...]:
        """
        Parse composition string formula
        """
        # Raise error if formula is invalid
        # (empty or not alphanumeric)
        if not formula:
            raise ValueError("Formula is empty")
        elif not formula.isalnum():
            raise ValueError("Formula is not alphanumeric")

        # Set element list for storage
        elements : list[Element] = []

        # Create temporary variable to store
        # chemical term, such as O3
        temp_term : str = ""

        # While there's still a formula string
        while formula:
            # If first character is a letter
            if formula[0].isalpha():
                """
                Iterate over formula and while letters are
                found, add them to temp_term. Then, test if
                it matches any chemical element, add it
                to the element list and remove it from the
                formula string
                """
                for c in formula:
                    if c.isalpha():
                        temp_term+= c
                    else:
                        break

                if temp_term in AtomicNumbers:
                    elements.append(
                        Element(AtomicNumbers[temp_term])
                    )
                    formula = formula.replace(temp_term, "", 1)
                    temp_term = ""

                else:
                    raise KeyError(
                        f"No element with symbol \"{temp_term}\""
                    )

            # If first char is a number
            elif formula[0].isdigit():
                """
                Iterate over formula and while numbers are
                found, add them to temp_term. Then, multiply the
                last element by the number written in temp_term
                and remove it from the formula string
                """
                for c in formula:
                    if c.isdigit():
                        temp_term+= c
                    else:
                        break

                if elements:
                    elements+= [elements.pop()]*int(temp_term)
                    formula = formula.replace(temp_term, "", 1)
                    temp_term = ""
                else:
                    raise ValueError("Numbers must follow an element symbol in the chemical formula")


        return tuple(elements)



class Atom(Element):
    """
    Atom class that represents an atom
    in space
    """
    pos : Vector
    def __init__(self, atomic_number : AtomicNumber, pos : Optional[Vector] = None):
        super().__init__(atomic_number)
        if pos:
            self.pos = pos.copy()
        else:
            self.pos = Vector()

    def __str__(self) -> str:
        return f"{self.symbol} ({', '.join([str(round(self.pos[i], 1)) for i in range(3)])})"

    def copy(self) -> "Atom":
        """
        Return a deep copy of itself
        """
        return Atom(
            self.z,
            self.pos.copy(),
        )

    @staticmethod
    def from_xyz_str(line) -> 'Atom':
        """
        Import atom from xyz formated line
        """
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
        """
        Export atom as xyz formated line
        """
        return f"{self.symbol} {self.pos.x} {self.pos.y} {self.pos.z}"

    def to_bytes(self) -> bytes:
        """
        Convert atom data to bytes
        """
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
    __atoms : tuple[Atom, ...]
    @check_types
    def __init__(self, atoms : Iterable[Atom]):
        self.__atoms = tuple(atoms)

    def __getitem__(self, key : int) -> Atom:
        return self.__atoms[key]

    def __len__(self) -> int:
        return len(self.__atoms)

    def __iter__(self) -> Iterator[Atom]:
        return iter(self.__atoms)

    def __reversed__(self) -> Iterator[Atom]:
        return reversed(self.__atoms)

    def __contains__(self, value : Atom) -> bool:
        return value in self.__atoms

    def index(self, value : Atom) -> int:
        return self.__atoms.index(value)

    def count(self, value : AtomicNumber) -> int:
        """
        Count how many atoms of a given
        atomic number are in the structure
        """
        return [atom.z for atom in self.__atoms].count(value)

    def __repr__(self) -> str:
        self_text = str(self).replace("\n", "\n\t")
        return f"Structure\n\t{self_text}"

    def __str__(self) -> str:
        return "\n".join((str(atom) for atom in self.__atoms))

    def is_equal_to(self, other : Self) -> bool:
        """
        Test if two structures are equal 
        (composition-wise)
        """
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
        assert self.is_equal_to(other), "Both structure should have the same number of atoms"

        """
        Sum distances between atoms of each structure and
        store it in a ordered list for each structure
        """
        self_dists : dict[tuple[AtomicNumber, AtomicNumber], list[float]] = {}
        for atom_i, atom_j in itertools.combinations(self.__atoms, 2):
            dict_key = (atom_i.z, atom_j.z) if atom_j.z>atom_i.z else (atom_j.z, atom_i.z)
            if not dict_key in self_dists:
                self_dists[dict_key] = []
            diff : Vector = atom_i.pos - atom_j.pos
            bisect.insort(
                self_dists[dict_key],
                diff.mod_sqr,
            )
        other_dists : dict[tuple[AtomicNumber, AtomicNumber], list[float]] = {}
        for atom_i, atom_j in itertools.combinations(other.__atoms, 2):
            dict_key = (atom_i.z, atom_j.z) if atom_j.z>atom_i.z else (atom_j.z, atom_i.z)
            if not dict_key in other_dists:
                other_dists[dict_key] = []
            diff = atom_i.pos - atom_j.pos
            bisect.insort(
                other_dists[dict_key],
                diff.mod_sqr,
            )

        # Get difference between each distance in each molecule (squared)
        sum_distances_squared_diff : float = 0
        for dict_key in self_dists:
            sum_distances_squared_diff+= sum([
                (i - j)**2
                for i, j
                in zip(self_dists[dict_key], other_dists[dict_key])
            ])

        # Calculate final value of Grigoryan-Springborn algorithm
        q : float = ( ( 2/(atoms_num*(atoms_num-1)) ) * sum_distances_squared_diff )**.5
        s : float = 1 / ( 1 + q )

        return s

    def is_bonded(self, bonding_tolerance : float = 0.1) -> bool:
        if len(self.__atoms)<2: return False

        bonded_atoms : list[Atom] = [self.__atoms[0]]
        stray_atoms : list[Atom] = list(self.__atoms[1:])
        adopted_atoms : list[Atom] = []

        while True:
            for bonded in bonded_atoms:
                for stray in reversed(stray_atoms):
                    # Check if distance between bonded and stray is equal or lower than bonding distance
                    if (bonded.pos - stray.pos).mod_sqr <= (bonded.radius + stray.radius)**2 + bonding_tolerance:
                        adopted_atoms.append(stray)
                        stray_atoms.remove(stray)

            # Atoms will be adopted (going to bonded group)
            if adopted_atoms:
                # There's still strays remaining
                if stray_atoms:
                    # Adopt atoms to bonded group
                    for adopted in adopted_atoms:
                        bonded_atoms.append(adopted)
                        adopted_atoms.remove(adopted)
                # There's no more stray atom (everyone is bonded)
                else:
                    # Atom is definitelly bonded
                    return True
            # There's no atom up for adoption
            else:
                if stray_atoms: #That IF is actually not necessary, but who knows ¯\_(ツ)_/¯
                    return False






    
    @staticmethod
    def from_xyz(file_path : str) -> 'Structure':
        """
        Create structure from xyz file
        """
        with open(file_path) as xyz_file:
            return Structure.from_xyz_str(xyz_file.read())

    def to_temp_xyz(self) -> tempfile._TemporaryFileWrapper:
        """
        Export structure to temporary xyz file
        """
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

    def to_xyz(self, name : str) -> None:
        """
        Export structure to xyz file
        """
        file = open(name, "w+")
        file.write(self.to_xyz_str())
        file.close()

    @staticmethod
    def from_xyz_str(s : str) -> 'Structure':
        """
        Create structure from xyz formated string
        """
        atoms : list[Atom] = []

        for line in s.splitlines()[2:]:
            atoms.append(
                Atom.from_xyz_str(line)
            )

        return Structure(atoms)

    def to_xyz_str(self) -> str:
        """
        Export structure to xyz formated string
        """
        lines : list[str] = [
            str(len(self)),
            "",
        ] + [
            atom.to_xyz_str()
            for atom
            in self.__atoms
        ]

        return "\n".join(lines)

    def plot(self, jmol_path = "jmol") -> None:
        """
        Open the structure in jmol (if available)
        """
        with self.to_temp_xyz() as xyz_file:
            subprocess.run(
                [
                    jmol_path,
                    xyz_file.name,
                ],
                capture_output = False,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL,
            )


    def copy(self) -> "Structure":
        """
        Return a deep copy of itself
        """
        return Structure(
            [
                atom.copy()
                for atom
                in self.__atoms
            ],
        )

    def to_bytes(self) -> bytes:
        """
        Convert structure data to bytes
        """
        r = struct.pack(b"I", len(self))

        for atom in self.__atoms:
            r+= atom.to_bytes()

        return r

class Molecule(Structure):
    """
    A class representing a molecule, inheriting from Structure.
    Can be extended with molecule-specific properties and methods.
    """
    energy : float

    def __init__(self, atoms: Iterable[Atom], energy : float):
        super().__init__(atoms)
        self.energy = energy

    @staticmethod
    def from_xyz(file_path: str) -> 'Molecule':
        """
        Create a Molecule from a xyz file 
        """
        with open(file_path) as file:
            s : str = file.read()
            return Molecule.from_xyz_str(s)

    @staticmethod
    def from_xyz_str(s : str) -> 'Molecule':
        """
        Create a Molecule from a xyz formated string
        """
        lines = s.splitlines()
        energy = float(lines[1].split()[1])
        struct = Structure.from_xyz_str(s)
        return Molecule(
            struct,
            energy,
        )

    def to_bytes(self) -> bytes:
        """
        Convert molecule data to bytes
        """
        r = struct.pack(b"Id", len(self), self.energy)

        for atom in self:
            r+= atom.to_bytes()

        return r
