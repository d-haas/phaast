from typing import Iterable

from calculators import Calculator
from computer import Computer
from structure import Molecule, Structure

from multiprocessing.dummy import Pool

from surface_explorator import SurfaceExplorator

class Genetic(SurfaceExplorator, list[Molecule]):
    charge : int
    population_size : int
    calculator : Calculator

    def __init__(
        self,
        structures : Iterable[Structure | Molecule],
        charge : int,
        population_size : int,
        computer : Computer,
        calculator : Calculator,
    ):
        self.charge = charge
        self.population_size = population_size
        self.calculator = calculator

        # Remove hard-coded 8, please
        with Pool(8) as p:
            molecules : list[Molecule] = p.starmap(
                self.calculator.optimize,
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
                # Compare energies
                if abs(self[i].energy-self[j].energy) <= energy_threshold:
                    # Then compare geometries
                    if self[i].compare(self[j]) <= geometry_threshold:
                        del self[j]

    def reproduce(self, top_k : int):
        pass

    def loop(self) -> None:
        pass

    def save(self, file : str) -> None:
        pass

