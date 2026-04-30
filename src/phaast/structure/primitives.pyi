from __future__ import annotations
from typing import Any, Callable, Iterable, Iterator, Optional, Self, TypedDict
from phaast.structure.constants import *
from phaast.utils import ObjectData
from phaast.vector import Vector, VectorData
import tempfile

class Element:
    """
    Class representing an atomic element
    mostly used for Stoichiometry expressions
    """
    z : AtomicNumber
    def __init__(self, atomic_number : AtomicNumber):
        """
        Sets atomic number for element
        """
        pass

    @property
    def symbol(self) -> str:
        """
        Get atomic symbol for element
        """
        pass

    @property
    def mass(self) -> float:
        """
        Get average atomic mass
        (based on isotopic proportions)
        """
        pass

    @property
    def radius(self) -> float:
        """
        Get atom covalent radius
        (based on same-element bondings)
        """
        pass

    def __eq__(self, other : Any | Element) -> bool:
        pass

    def __str__(self) -> str:
        """
        str(Atom) implementation
        """
        pass

    def __repr__(self) -> str:
        pass


class Base:
    elements : tuple[Element, ...]

    def __init__(self, elements : Iterable[Element] | str):
        """
        Create base (alias to chemical composition)
        of a molecule
        """
        pass

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator[Element]:
        """
        Iterate over Base
        """
        pass

    def as_data(self) -> ObjectData:
        """
        Return Base as a JSON-parseable object
        """
        pass

    def parse_formula(self, formula : str) -> tuple[Element, ...]:
        """
        Parse composition string formula
        """
        pass

def create_atom(atomic_number : AtomicNumber, pos : Vector) -> Atom:
    pass

class AtomData(TypedDict):
    z   : int
    pos : VectorData
    charge : float

class Atom(Element):
    """
    Atom class that represents an atom
    in space
    """
    pos : Vector
    p_charge : float
    def __init__(self, atomic_number : AtomicNumber, pos : Optional[Vector] = None):
        pass

    def is_touching(self, other : Self, bonding_tolerance : float = 0) -> bool:
        """
        Checks if bonding radius of both atoms
        are touching or overlapping
        
        bonding_tolerance is added as a tolerance variable
        to increase the radius of either one of the atoms
        """
        pass


    def __str__(self) -> str:
        return f"{self.symbol} ({', '.join([str(round(self.pos[i], 1)) for i in range(3)])})"

    def copy(self) -> "Atom":
        """
        Return a deep copy of itself
        """
        pass

    @staticmethod
    def from_xyz_str(line) -> 'Atom':
        """
        Import atom from xyz formated line
        """
        pass


    def to_xyz_str(self) -> str:
        """
        Export atom as xyz formated line
        """
        pass

    def to_bytes(self) -> bytes:
        """
        Convert atom data to bytes
        """
        pass

    def as_data(self) -> AtomData:
        """
        Export to JSON importable dict
        """
        pass

    @classmethod
    def from_data(cls, data : AtomData) -> Atom:
        pass
    
    def __reduce__(self):
        pass

def create_structure(atoms : Iterable[Atom]) -> Structure:
    pass

class StructureData(TypedDict):
    length : int
    atoms  : list[AtomData]

class Structure:
    """
    Main class for representing molecular/cluster
    structure geometry
    """
    atoms : list[Atom]

    def __init__(self, atoms : Iterable[Atom]):
        pass

    def __getitem__(self, key : int) -> Atom:
        pass

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator[Atom]:
        pass

    def __reversed__(self) -> Iterator[Atom]:
        pass

    def __contains__(self, value : Atom) -> bool:
        pass

    def index(self, value : Atom) -> int:
        pass

    def count(self, value : AtomicNumber) -> int:
        """
        Count how many atoms of a given
        atomic number are in the structure
        """
        pass

    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass

    def is_equal_to(self, other : Self) -> bool:
        """
        Test if two structures are equal 
        (composition-wise)
        """
        pass

    def element_count(self) -> dict[int, int]:
        """
        Returns dict with quantity of each atom in each molecule
        """
        pass

    @property
    def cm(self) -> Vector:
        """
        Return structure's center of mass
        """
        pass

    def center_mass(self):
        """
        Translates the molecule so it's center of mass
        is centered at (0.0, 0.0, 0.0)
        """
        pass

    
    @staticmethod
    def from_xyz(file_path : str) -> 'Structure':
        """
        Create structure from xyz file
        """
        pass

    def to_temp_xyz(self) -> tempfile._TemporaryFileWrapper:
        """
        Export structure to temporary xyz file
        """
        pass

    def to_xyz(self, name : str, comment : str = "") -> None:
        """
        Export structure to xyz file
        """
        pass

    @staticmethod
    def from_xyz_str(s : str) -> 'Structure':
        """
        Create structure from xyz formated string
        """
        pass

    def to_xyz_str(self, comment : str = "") -> str:
        """
        Export structure to xyz formated string
        """
        pass

    def plot(self) -> None:
        """
        Open the structure in the phaast GUI (if available)
        """
        pass

    def copy(self) -> Self:
        """
        Return a deep copy of itself
        """
        pass

    def to_bytes(self) -> bytes:
        """
        Convert structure data to bytes
        """
        pass

    def as_data(self) -> StructureData:
        """
        Export to JSON importable dict
        """
        pass

    @classmethod
    def from_data(cls, data : StructureData) -> Structure:
        pass

    def __reduce__(self) -> tuple[ Callable[..., Structure], tuple[Any, ...] ]:
        pass

def create_molecule(atoms : Iterable[Atom], energy : float) -> Molecule:
    pass

class MoleculeData(StructureData):
    energy : float

class Molecule(Structure):
    """
    A class representing a molecule, inheriting from Structure.
    Can be extended with molecule-specific properties and methods.
    """

    energy : float

    def __init__(self, atoms: Iterable[Atom], energy : float):
        pass

    def is_bonded(self, bonding_tolerance : float = 0.1) -> bool:
        """
        Test of molecule is in a bonded state

        Which means testing if this object is
        only a single molecule
        """
        pass

    def get_bondings_lenghts(self, bonding_tolerance : float = 0.1) -> dict[tuple[AtomicNumber, AtomicNumber], list[float]]:
        pass

    @staticmethod
    def from_xyz(file_path: str) -> Molecule:
        """
        Create a Molecule from a xyz file 
        """
        pass

    @staticmethod
    def from_xyz_str(s : str) -> Molecule:
        """
        Create a Molecule from a xyz formated string
        """
        pass

    def to_xyz_str(self, comment : str = "") -> str:
        """
        Export Molecule to xyz formated string
        """
        pass

    def to_xyz(self, name : str, comment : str = "") -> None:
        """
        Export Molecule to xyz file
        """
        pass

    def copy(self) -> Self:
        """
        Return a deep copy of itself
        """
        pass

    def to_bytes(self) -> bytes:
        """
        Convert molecule data to bytes
        """
        pass

    def as_data(self) -> MoleculeData:
        """
        Export to JSON importable dict
        """
        pass

    @classmethod
    def from_data(cls, data : MoleculeData) -> Molecule: # type: ignore[override]
        pass

    def __reduce__(self) -> tuple[ Callable[..., Molecule], tuple[tuple[Atom, ...], float] ]:
        pass
