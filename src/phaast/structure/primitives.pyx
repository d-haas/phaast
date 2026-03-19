import cython
from cython.view cimport array as cvarray
from cython.parallel import prange
from phaast.vector cimport Vector
from cpython cimport array

import sys

from typing import Any, Callable, Iterable, Iterator, Optional, Self

from phaast.structure.constants import *
from phaast.vector import Vector
import subprocess, tempfile
import struct

@cython.auto_pickle(True)
cdef class Element:
    """
    Class representing an atomic element
    mostly used for Stoichiometry expressions
    """

    z : cython.uint

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

    def __eq__(self, other : Any | Element) -> bool:
        if isinstance(other, Element):
            return self.z == other.z
        else:
            return False

    def __str__(self) -> str:
        """
        str(Atom) implementation
        """
        return self.symbol

    def __repr__(self) -> str:
        return str(self)

class Base:
    __slots__ = ("elements",)

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

    def __len__(self) -> int:
        return len(self.elements)

    def __iter__(self) -> Iterator[Element]:
        """
        Iterate over Base
        """
        return iter(self.elements)

    def to_formula(self) -> dict[str, int]:
        element_counter = {}
        for element in self.elements:
            if element.symbol in element_counter:
                element_counter[element.symbol]+= 1
            else:
                element_counter[element.symbol] = 1

        return sum(
            [
                symbol+str(num)
                for symbol, num
                in element_counter.items()
            ],
            start = "",
        )

    def as_data(self) -> dict[str, int]:
        return {
            "import" : "phaast.structure.primitives.Base",
            "args"   : (self.to_formula(),),
            "kwargs" : {},
        }

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


cpdef Atom create_atom(unsigned int atomic_number, Vector pos):
    return Atom(atomic_number, pos)

@cython.auto_pickle(True)
cdef class Atom(Element):
    """
    Atom class that represents an atom
    in space
    """

    pos : Vector

    def __init__(self, atomic_number : cython.uint, pos : Vector = None):
        super().__init__(atomic_number)
        if pos:
            self.pos = pos.copy()
        else:
            self.pos = Vector()

    def is_touching(self, other : Self, bonding_tolerance : float = 0) -> bool:
        """
        Checks if bonding radius of both atoms
        are touching or overlapping
        
        bonding_tolerance is added as a tolerance variable
        to increase the radius of either one of the atoms
        """
        return (self.pos - other.pos).mod_sqr <= (self.radius + other.radius)**2 + bonding_tolerance


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

    def as_data(self) -> dict:
        return {
            "z" : self.z,
            "pos" : self.pos.as_data(),
        }
    
    def __reduce__(self):
        return (create_atom, (self.z, self.pos))

cpdef Structure create_structure(object atoms):
    return Structure(atoms)

@cython.auto_pickle(True)
cdef class Structure:
    """
    Main class for representing molecular/cluster
    structure geometry
    """
    atoms : Atom[:]
    length : cython.Py_ssize_t

    def __init__(self, atoms : Iterable[Atom]):
        
        self.length = len(atoms)
        cdef Atom[:] temp_atoms = cvarray(shape=(self.length,), itemsize = sizeof(Atom*), format="O")

        cdef int i
        cdef Atom atom_ptr
        for i in range(self.length):
            atom_ptr = atoms[i]
            temp_atoms[i] = atom_ptr

        self.atoms = temp_atoms


    def __getitem__(self, key : int) -> Atom:
        cdef int ckey = key
        assert 0 <= ckey < self.length
        return self.atoms[ckey]

    def __len__(self) -> int:
        return self.length

    def __iter__(self) -> Iterator[Atom]:
        for i in range(self.length):
            yield self.atoms[i]

    def __reversed__(self) -> Iterator[Atom]:
        return reversed(self.atoms)

    def __contains__(self, value : Atom) -> bool:
        return value in self.atoms

    def count(self, value : AtomicNumber) -> int:
        """
        Count how many atoms of a given
        atomic number are in the structure
        """
        return [atom.z for atom in self].count(value)

    def __repr__(self) -> str:
        self_text = str(self).replace("\n", "\n\t")
        return f"Structure\n\t{self_text}"

    def __str__(self) -> str:
        return "\n".join((str(atom) for atom in self.atoms))

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
        for atom in self.atoms:
            if atom.z in r:
                r[atom.z]+= 1
            else:
                r[atom.z] = 1
        return r

    cdef Vector get_cm(self):
        """
        Returns structure's center of mass
        """
        cdef Vector total = Vector(0, 0, 0)

        cdef double mass_counter = 0

        cdef double mass

        for atom in self.atoms:
            mass = atom.mass
            total.x+= atom.pos.x * mass
            total.y+= atom.pos.y * mass
            total.z+= atom.pos.z * mass
            mass_counter+= mass

        return total.div(mass_counter)

    @property
    def cm(self) -> Vector:
        """
        Also returns structure's center of mass
        """
        # Sum vector to accumulate ponderate positions (A.U.)
        sum_vector : Vector = Vector(0,0,0)

        # Accumulated mass of all atoms (A.U.)
        mass_counter = 0

        # Adds positions to sum_vector and atomic masses to center of mass
        for atom in self.atoms:
            sum_vector+= atom.pos * atom.mass
            mass_counter+= atom.mass

        if mass_counter:
            sum_vector/= mass_counter
            return sum_vector
        else:
            raise Exception("No atoms in structure")

    def center_mass(self):
        """
        Translates the molecule so it's center of mass
        is centered at (0.0, 0.0, 0.0)
        """
        cm = self.cm
        for atom in self:
            atom.pos-= cm

    
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
        # For some GD reason, the files needs to be read
        # before xtb uses it (TF????)
        file.read()

        return file

    def to_xyz(self, name : str, comment : str = "") -> None:
        """
        Export structure to xyz file
        """
        file = open(name, "w+")
        file.write(self.to_xyz_str(comment))
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

    def to_xyz_str(self, comment : str = "") -> str:
        """
        Export structure to xyz formated string
        """
        assert not ("\n" in comment), "There shouldn't be any line breaks in xyz comment"
        lines : list[str] = [
            str(len(self)),
            comment,
        ] + [
            atom.to_xyz_str()
            for atom
            in self.atoms
        ]

        return "\n".join(lines)

    def plot(self) -> None:
        """
        Open the structure in phaast-gui (if available)
        """
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
        """


    def copy(self) -> Self:
        """
        Return a deep copy of itself
        """
        return self.__class__(
            [
                atom.copy()
                for atom
                in self.atoms
            ],
        )

    def to_bytes(self) -> bytes:
        """
        Convert structure data to bytes
        """
        r = struct.pack(b"I", len(self))

        for atom in self:
            r+= atom.to_bytes()

        return r

    def as_data(self) -> dict:
        return {
            "length" : self.length,
            "atoms"  : [atom.as_data() for atom in self.atoms],
        }

    def __reduce__(self):
        return (create_structure, (tuple(self),))

cpdef Molecule create_molecule(object atoms, double energy):
    return Molecule(atoms, energy)

@cython.auto_pickle(True)
cdef class Molecule(Structure):
    """
    A class representing a molecule, inheriting from Structure.
    Can be extended with molecule-specific properties and methods.
    """

    energy : cython.double

    def __init__(self, atoms: Iterable[Atom], energy : float):
        super().__init__(atoms)
        self.energy = energy

    cpdef bool is_bonded(self, double bonding_tolerance = 0.1):
        """
        Test of molecule is in a bonded state

        Which means testing if this object is
        only a single molecule
        """
        if len(self)<2: return False

        cdef list infected_atoms = [self[0]]
        cdef list healthy_atoms = list(self)[1:]

        cdef bool someone_was_infected = True

        # Loop until there are no more infections possible
        while someone_was_infected:
            someone_was_infected = False
            for infected_index in reversed(range(len(infected_atoms))):
                infected = infected_atoms[infected_index]
                for healthy_index in reversed(range(len(healthy_atoms))):
                    healthy = healthy_atoms[healthy_index]
                    # Check if distance between infected and healthy is
                    # equal or lower than bonding distance
                    if infected.is_touching(healthy, bonding_tolerance):
                        # Tells loop someone was infected
                        someone_was_infected = True
                        # Add new atom to infected pool
                        infected_atoms.append(healthy)
                        # Remove it from healthy pool
                        del healthy_atoms[healthy_index]
                # Delete infected atom from the pool, since it
                # has already infected everyone in its range
                del infected_atoms[infected_index]

        #return not healthy_atoms
        if healthy_atoms:
            return False
        else:
            return True

    def get_bondings_lenghts(self, bonding_tolerance : float = 0.1) -> dict[tuple[AtomicNumber, AtomicNumber], list[float]]:
        result = {}

        for atom_i in self:
            for atom_j in self:
                if atom_i.is_touching(atom_j, bonding_tolerance):
                    dict_key = (min(atom_i.z, atom_j.z), max(atom_i.z, atom_j.z))
                    if dict_key in result:
                        result[dict_key].append((atom_i.pos - atom_j.pos).mod_sqr)
                    else:
                        result[dict_key] = [(atom_i.pos - atom_j.pos).mod_sqr]

        return result

    @staticmethod
    def from_xyz(file_path: str) -> Molecule:
        """
        Create a Molecule from a xyz file 
        """
        with open(file_path) as file:
            s : str = file.read()
            return Molecule.from_xyz_str(s)

    @staticmethod
    def from_xyz_str(s : str) -> Molecule:
        """
        Create a Molecule from a xyz formated string
        """
        lines = s.splitlines()
        if lines[1].startswith("Coordinates from ORCA-job") or lines[1].startswith("P.H.A.A.S.T job"):
            energy = float(lines[1].split()[-1])
        elif lines[1].startswith(" energy:"):
            energy = float(lines[1].split()[1])
        else:
            raise ValueError("xyz file should contain energy in xtb or orca pattern")
        struct = Structure.from_xyz_str(s)
        return Molecule(
            struct,
            energy,
        )

    def to_xyz_str(self, comment : str = "") -> str:
        """
        Export Molecule to xyz formated string
        """
        full_comment = "P.H.A.A.S.T job "
        if comment:
            assert not ("\n" in comment), "There shouldn't be any line breaks in xyz comment"
            full_comment+= f"({comment}) "
        full_comment+= f"Eh: {self.energy}"

        lines : list[str] = [
            str(len(self)),
            full_comment,
        ] + [
            atom.to_xyz_str()
            for atom
            in self
        ]
        return "\n".join(lines)

    def to_xyz(self, name : str, comment : str = "") -> None:
        """
        Export Molecule to xyz file
        """
        file = open(name, "w+")
        file.write(self.to_xyz_str(comment))
        file.close()

    def copy(self) -> Self:
        """
        Return a deep copy of itself
        """
        return self.__class__(
            [
                atom.copy()
                for atom
                in self.atoms
            ],
            self.energy,
        )

    def to_bytes(self) -> bytes:
        """
        Convert molecule data to bytes
        """
        r = struct.pack(b"Id", len(self), self.energy)

        for atom in self:
            r+= atom.to_bytes()

        return r

    def as_data(self) -> dict:
        return super().as_data() | {
            "energy" : self.energy,
        }

    def __reduce__(self):
        return (create_molecule, (tuple(self), self.energy))
