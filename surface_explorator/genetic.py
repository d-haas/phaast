import random
from typing import Iterable
from math import ceil, floor

from calculators import Calculator
from calculators.xtb import XTB
from computer import Computer
from structure import Molecule, Structure

from surface_explorator import SurfaceExplorator
from utils.typecheck import check_types
from utils.custom_iter import distinct_pairs
import structure.recombiner
import structure.mutator

class Genetic(SurfaceExplorator):
    population_size : int
    population : list[Molecule]
    calculator : Calculator
    computer : Computer
    energy_threshold : float
    geometry_threshold : float
    children_mutant_ratio : float

    @check_types
    def __init__(
        self,
        structures : Iterable[Structure | Molecule],
        population_size : int,
        computers : Computer,
        energy_threshold : float,
        geometry_threshold : float,
        children_mutant_ratio : float,
    ):
        self.population_size = population_size

        self.computer = computers

        self.energy_threshold = energy_threshold
        self.geometry_threshold = geometry_threshold

        self.population : list[Molecule] = self.computer.optimize(XTB, list(structures))

        self.children_mutant_ratio = children_mutant_ratio

    def remove_duplicates(self) -> None:
        for i in reversed(range(len(self.population))):
            for j in reversed(range(i+1, len(self.population))):
                # Compare energies
                if abs(self.population[i].energy-self.population[j].energy) <= self.energy_threshold:
                    # Then compare geometries
                    if Structure.compare_geometry(self.population[i], self.population[j]) <= self.geometry_threshold:
                        del self.population[j]

    def reproduce(self) -> list[Molecule]:
        remaining_population : int = self.population_size - len(self.population)
        remaining_population*= ceil(self.children_mutant_ratio/(self.children_mutant_ratio+1))

        children : list[Structure] = []

        parents = [
            (mother, father)
            for mother, father
            in distinct_pairs(self.population)
        ]
        for mother, father in random.sample(parents, remaining_population):
            children.append(
                structure.recombiner.plane_mating(mother, father)
            )

        return self.computer.optimize(XTB, children)

    def mutate(self) -> list[Molecule]:
        remaining_population : int = self.population_size - len(self.population)
        remaining_population*= floor(1/(self.children_mutant_ratio+1))

        mutants : list[Structure] = []

        for mutant in random.sample(mutants, remaining_population):
            mutants.append(
                structure.mutator.mut_random(mutant, 0.5)
            )

        return self.computer.optimize(XTB, mutants)

    def loop(self) -> None:
        self.remove_duplicates()
        children : list[Molecule] = self.reproduce()
        mutants : list[Molecule] = self.mutate()
        self.population+= children
        self.population+= mutants

    def save(self, file : str) -> None:
        print(file)
        pass

