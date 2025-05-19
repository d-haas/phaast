from typing import Iterable

from calculators import Calculator
from calculators.xtb import XTB
from computer import Computer
from structure import Molecule, Structure

from surface_explorator import SurfaceExplorator
from typecheck import check_types

class Genetic(SurfaceExplorator):
    population_size : int
    population : list[Molecule]
    calculator : Calculator
    computer : Computer
    energy_threshold : float
    geometry_threshold : float

    @check_types
    def __init__(
        self,
        structures : Iterable[Structure | Molecule],
        population_size : int,
        computers : Computer,
        energy_threshold : float,
        geometry_threshold : float,
    ):
        self.population_size = population_size

        self.computer = computers

        self.energy_threshold = energy_threshold
        self.geometry_threshold = geometry_threshold

        self.population : list[Molecule] = self.computer.optimize(XTB, list(structures))

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

