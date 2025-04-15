from typing import Iterable
import structure.constants as constants
import vector

class Atom:
    z : int
    pos : vector.Vector3D

    def __init__(self, atomic_number : int, pos : vector.Vector3D):
        self.z = atomic_number
        self.pos = pos

    """
    @property
    def mass(self):
        return constants.atomic_masses[self.z]
    """

    @property
    def name(self) -> str:
        return constants.atomic_name[self.z]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.name} ({self.pos.x}, {self.pos.y}, {self.pos.z})"

class Structure(tuple[Atom, ...]):
    def __new__(cls, atoms : Iterable[Atom]):
        return super().__new__(cls, tuple(atoms))

    def __repr__(cls) -> str:
        return "\n".join((str(atom) for atom in super()))

