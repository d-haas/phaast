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
    best_energy : float
    best_energy_loops : int
    cycle_counter : int

    @check_types
    def __init__(
        self,
        structures : Iterable[Structure | Molecule],
        computer : Computer,
        energy_threshold : float,
        geometry_threshold : float,
        children_mutant_ratio : float,
    ):
        self.computer = computer
        self.population : list[Molecule] = [
            mol for mol
            in self.computer.optimize(XTB, list(structures))
            if mol is not None
        ]
        self.population_size = len(self.population)

        self.energy_threshold = energy_threshold
        self.geometry_threshold = geometry_threshold

        self.children_mutant_ratio = children_mutant_ratio

        self.best_energy = min([mol.energy for mol in self.population])
        self.best_energy_loops = 0
        self.cycle_counter = 0

    def remove_duplicates(self) -> None:
        for i in reversed(range(len(self.population))):
            for j in reversed(range(i+1, len(self.population))):
                # Compare energies
                if abs(self.population[i].energy-self.population[j].energy) <= self.energy_threshold:
                    # Then compare geometries
                    if Structure.compare_geometry(self.population[i], self.population[j]) > self.geometry_threshold:
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

        return [mol for mol in self.computer.optimize(XTB, children) if mol is not None]

    def mutate(self) -> list[Molecule]:
        remaining_population : int = self.population_size - len(self.population)
        remaining_population*= floor(1/(self.children_mutant_ratio+1))

        mutants : list[Structure] = []

        for mutant in random.sample(mutants, remaining_population):
            mutants.append(
                structure.mutator.mut_random(mutant, 0.5)
            )

        return [mol for mol in self.computer.optimize(XTB, mutants) if mol is not None]

    def get_best_energy(self) -> None:
        new_best_energy : float = min([mol.energy for mol in self.population])
        if new_best_energy < self.best_energy:
            self.best_energy = new_best_energy
            self.best_energy_loops = 0
        else:
            self.best_energy_loops+= 1

    def loop(self) -> bool:
        self.cycle_counter+= 1

        self.remove_duplicates()
        print(f"After removing duplicates, population now has {len(self.population)} molecules.")

        children : list[Molecule] = self.reproduce()
        mutants : list[Molecule] = self.mutate()
        self.population+= children
        self.population+= mutants

        self.get_best_energy()
        return self.best_energy_loops <=8

    def save(self, file : str) -> None:
        print(file)
        pass

