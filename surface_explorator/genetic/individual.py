from typing import Any, Callable, Iterable, overload
from structure import Atom, Molecule

def create_individual(atoms : Iterable[Atom], energy : float, generations_alive : int) -> "Individual":
    ind = Individual(atoms, energy)
    ind.generations_alive = generations_alive
    return ind

class Individual(Molecule):
    generations_alive : int

    @overload
    def __init__(self, atoms_or_mol : Iterable[Atom], energy : float): ...
    @overload
    def __init__(self, atoms_or_mol : Molecule): ...
    def __init__(self, atoms_or_mol : Iterable[Atom] | Molecule, energy : float | None = None):
        if isinstance(atoms_or_mol, Molecule):
            super().__init__(atoms_or_mol, atoms_or_mol.energy)
        elif isinstance(energy, float):
            super().__init__(atoms_or_mol, energy)
        else:
            raise ValueError("No energy was given")
        self.generations_alive = 0

    def __reduce__(self) -> tuple[ Callable[..., "Individual"], tuple[Any, ...] ]:
        return (create_individual, super().__reduce__()[1] + (self.generations_alive,))
