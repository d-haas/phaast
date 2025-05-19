from typing import Iterable

from calculators import Calculator
from computer import Computer
from structure import Molecule, Structure

from multiprocessing.dummy import Pool

from surface_explorator import SurfaceExplorator
from typecheck import check_types

class Genetic(SurfaceExplorator):
    population_size : int
    population : list[Molecule]
    calculator : Calculator
    computers : list[Computer]
    energy_threshold : float
    geometry_threshold : float

    @check_types
    def __init__(
        self,
        structures : Iterable[Structure | Molecule],
        population_size : int,
        computers : Iterable[Computer],
        energy_threshold : float,
        geometry_threshold : float,
    ):
        self.population_size = population_size

        self.computers = [cpu for cpu in computers]

        self.energy_threshold = energy_threshold
        self.geometry_threshold = geometry_threshold

        # Remove hard-coded 8, please
        with Pool(self.computers[0].cpu_count_limit) as p:
            self.population : list[Molecule] = p.starmap(
                self.calculator.optimize,
                [
                    (structure,)
                    for structure in structures
                    if isinstance(structure, Structure)
                ]
            ) + [
                molecule for molecule in structures
                if isinstance(molecule, Molecule)
            ]

    def remove_duplicates(self) -> None:
        for i in reversed(range(len(self.population))):
            for j in reversed(range(i+1, len(self.population))):
                # Compare energies
                if abs(self.population[i].energy-self.population[j].energy) <= self.energy_threshold:
                    # Then compare geometries
                    if Structure.compare_geometry(self.population[i], self.population[j]) <= self.geometry_threshold:
                        del self.population[j]

    def reproduce(self):
        pass

    def create(self) -> None:
        pass

    def loop(self) -> None:
        self.reproduce()
        pass

    def save(self, file : str) -> None:
        print(file)
        pass

