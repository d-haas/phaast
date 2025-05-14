from typing import Iterable

from structure import Molecule, Structure
from structure.optimizer import optimize_structure

from multiprocessing.dummy import Pool


class Generation(list[Molecule]):
    def __init__(
        self,
        structures : Iterable[Structure | Molecule],
        charge : int,
    ):

        # Remove hard-coded 8, please
        with Pool(8) as p:
            molecules : list[Molecule] = p.starmap(
                optimize_structure,
                [
                    (structure, charge)
                    for structure in structures
                    if isinstance(structure, Structure)
                ]
            ) + [
                molecule for molecule in structures
                if isinstance(molecule, Molecule)
            ]

        super().__init__(molecules)

    def remove_duplicates(self, geometry_threshold : float, energy_threshold : float = 0.0) -> None:
        for i in reversed(range(len(self))):
            for j in reversed(range(i+1, len(self))):
                if abs(self[i].energy-self[j].energy) <= energy_threshold:
                    if self[i].compare(self[j]):
                        del self[j]

    def reproduce(self, top_k : int):
        pass

