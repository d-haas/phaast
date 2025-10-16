import random
import sys
from typing import Any, Callable, Iterable, Sequence, overload
from math import floor

from structure.geometry import grigoryan_springborn, haas_oliveira
from surface_explorator.genetic.utils import mut_permute, mut_random, plane_mating

if sys._is_gil_enabled():
    from multiprocessing import Pool
else:
    from multiprocessing.dummy import Pool

from computer import Computer
from structure import Atom, Base, Molecule, Structure
from structure.creator import generate_random_structures_hedron

from surface_explorator import SurfaceExplorator
from utils.custom_iter import distinct_pairs


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

def is_pop_index_duplicate(
    population : list[Individual],
    i : int,
    energy_threshold : float,
    geometry_threshold : float,
    comparison_algorithm : Callable[[Molecule, Molecule], float],
) -> bool:

    for j in range(i+1, len(population)):
        # Compare energies
        if abs(population[i].energy-population[j].energy) <= energy_threshold:
            # Then compare geometries
            if comparison_algorithm(population[i], population[j]) > geometry_threshold:
                return True

    return False

class Genetic(SurfaceExplorator):
    population_size : int
    population      : list[Individual]
    end_loop_number : int

    calculator          : str
    computer            : Computer
    structure_generator : Callable[[Base, int, Computer], Sequence[Structure]]
    base                : Base

    energy_threshold     : float
    geometry_threshold   : float
    comparison_algorithm : Callable[[Molecule, Molecule], float]

    generation_children_mutant_proportion   : tuple[float, float, float]
    children_mutant_proportion              : tuple[float, float]
    mut_displacement_permutation_proportion : tuple[float, float]

    mut_displacement_number : int
    mut_displacement_max    : float
    mut_permutation_num     : int

    cycle_counter     : int
    minimum_lifetime  : int
    best_energy       : float
    best_energy_loops : int

    total_optimizations          : int
    total_converged              : int
    total_duplicates_removed     : int
    total_mutations              : int
    total_mutations_displacement : int
    total_mutations_permutation  : int
    total_mating                 : int

    def __init__(
        self,
        base : Base,
        population_size : int,
        computer : Computer,
        energy_threshold : float,
        geometry_threshold : float,
        calculator : str,

        structure_generator : Callable[[Base, int, Computer], Sequence[Structure]] = lambda base, n, comp : generate_random_structures_hedron(base, n, comp, 20),
        comparison_algorithm : Callable[[Molecule, Molecule], float] = grigoryan_springborn,

        generation_children_mutant_proportion : tuple[float, float, float] = (1.0, 1.0, 1.0),
        mut_displacement_permutation_proportion : tuple[float, float] = (1.0, 1.0),

        mut_displacement_number : int = 1,
        mut_displacement_max : float = 1.0,
        mut_permutation_num : int = 0,

        minimum_lifetime : int = -1,

        end_loop_number : int = 9,
    ):
        """
        Define initial variables for genetic algorithm
        """
        self.computer = computer
        self.calculator = calculator
        if population_size < 100:
            raise ValueError(
                "Population size is too small",
            )
        self.base = base
        self.structure_generator = structure_generator
        self.population_size = population_size
        self.population : list[Individual] = [
            Individual(mol) for mol
            in self.computer.optimize(
                self.calculator,
                self.structure_generator(
                    self.base,
                    self.population_size,
                    self.computer,
                ),
            )
        ]


        self.population_size = len(self.population)

        self.energy_threshold     = energy_threshold
        self.geometry_threshold   = geometry_threshold
        self.comparison_algorithm = comparison_algorithm

        self.generation_children_mutant_proportion = generation_children_mutant_proportion

        ###########################
        ### Mutation parameters ###
        ###########################
        self.mut_displacement_permutation_proportion = mut_displacement_permutation_proportion

        # Added explicit type conversion to manage vector multiplication errors
        self.mut_displacement_number = int(mut_displacement_number)
        self.mut_displacement_max    = float(mut_displacement_max)
        self.mut_permutation_num     = int(mut_permutation_num)

        # Generation parameters
        self.end_loop_number   = end_loop_number
        self.cycle_counter     = 0
        self.minimum_lifetime  = minimum_lifetime
        self.best_energy       = min([mol.energy for mol in self.population])
        self.best_energy_loops = 0

        #Statistics variables (start with prefix "total")
        self.total_optimizations          = self.population_size
        self.total_converged              = len(self.population)
        self.total_unfeasible_removed     = 0
        self.total_duplicates_removed     = 0
        self.total_mutations              = 0
        self.total_mutations_displacement = 0
        self.total_mutations_permutation  = 0
        self.total_mating                 = 0


    """
    def is_pop_index_duplicate(self, i : int) -> bool:
        for j in range(i+1, len(self.population)):
            # Compare energies
            if abs(self.population[i].energy-self.population[j].energy) <= self.energy_threshold:
                # Then compare geometries
                if self.population[i].compare_geometry(self.population[j]) > self.geometry_threshold:
                    return True

        return False
    """

    def remove_duplicates(self) -> None:

        def is_pop_index_duplicate(
            population : list[Individual],
            i : int,
        ) -> bool:

            if population[i].generations_alive <= self.minimum_lifetime:
                for j in range(i+1, len(population)):
                    # Compare energies
                    if abs(population[i].energy-population[j].energy) <= self.energy_threshold:
                        # Then compare geometries
                        if self.comparison_algorithm(population[i], population[j]) > self.geometry_threshold:
                            return True

            return False

        with Pool(self.computer.cpu_count_limit) as pool:
            remove_mask : list[bool]  = pool.starmap(
                is_pop_index_duplicate,
                [
                    (
                        self.population,
                        i,
                        self.energy_threshold,
                        self.geometry_threshold,
                        self.comparison_algorithm,
                    )
                    for i in range(len(self.population))
                ],
            )

        new_population = [
            mol for mol, is_duplicate
            in zip(self.population, remove_mask)
            if not is_duplicate
        ]

        self.total_duplicates_removed = len(self.population) - len(new_population)

        self.population = new_population


    def generate(self) -> list[Individual]:
        remaining_population : int = self.population_size# - len(self.population)
        remaining_population = floor(remaining_population * self.generation_children_mutant_proportion[0]/sum(self.generation_children_mutant_proportion))

        generated : list[Individual] = [
            Individual(mol) for mol
            in self.computer.optimize(
                self.calculator,
                self.structure_generator(
                    self.base,
                    remaining_population,
                    self.computer,
                ),
            )
        ]

        return generated

    def reproduce(self) -> list[Individual]:
        remaining_population : int = self.population_size# - len(self.population)
        remaining_population = floor(remaining_population * self.generation_children_mutant_proportion[1]/sum(self.generation_children_mutant_proportion))

        parents = [
            (mother, father)
            for mother, father
            in distinct_pairs(self.population)
        ]

        children : list[Structure] = []

        for mother, father in random.choices(
            parents,
            k = remaining_population,
        ):
            children.append(
                plane_mating(mother, father)
            )

        children_individuals = [Individual(mol) for mol in self.computer.optimize(self.calculator, children) if mol is not None]

        self.total_optimizations+= remaining_population
        self.total_converged+= len(children_individuals)
        self.total_mating+= len(children_individuals)

        return children_individuals

    def mutate(self) -> list[Individual]:
        # Get the number of individuals that will be choosen to mutate
        remaining_population : int = self.population_size# - len(self.population)
        remaining_population = floor(remaining_population * self.generation_children_mutant_proportion[2]/sum(self.generation_children_mutant_proportion))

        # Get actual number of individuals that will be choosen to have their atoms displaced
        remaining_displacement : int = floor(remaining_population * self.mut_displacement_permutation_proportion[0]/sum(self.mut_displacement_permutation_proportion))

        # Get actual number of individuals that will be choosen to have their atoms permutates (switch positions)
        remaining_permute : int = floor(remaining_population * self.mut_displacement_permutation_proportion[1]/sum(self.mut_displacement_permutation_proportion))

        mutants : list[Structure] = []

        for mutant in random.choices(
            self.population,
            k = remaining_displacement,
        ):
            mutants.append(
                mut_random(
                    mutant,
                    self.mut_displacement_number,
                    self.mut_displacement_max,
                )
            )

        for mutant in random.choices(
            self.population,
            k = remaining_permute,
        ):
            mutants.append(
                mut_permute(
                    mutant,
                    len(mutant)//2 if self.mut_permutation_num<=0 else self.mut_permutation_num,
                )
            )

        mutant_molecules : list[Individual] = [Individual(mol) for mol in self.computer.optimize(self.calculator, mutants) if mol is not None]

        self.total_optimizations+= remaining_displacement + remaining_permute
        self.total_converged+= len(mutant_molecules)
        self.total_mutations+= len(mutant_molecules)

        return mutant_molecules

    def remove_unfeasible(self) -> None:
        min_energy : float = min([mol.energy for mol in self.population])
        max_energy : float = max([mol.energy for mol in self.population])
        median_energy : float = (min_energy + max_energy)/2

        pop_size_before = len(self.population)

        self.population = [
            mol for mol in self.population
            if mol.energy<= median_energy
        ]

        pop_size_after = len(self.population)

        self.total_unfeasible_removed+= pop_size_before - pop_size_after

    def remove_excess(self) -> None:
        self.population = sorted(
            self.population,
            key = lambda ind : ind.energy,
        )[0:min(len(self.population), self.population_size)]

    def get_best_energy(self) -> None:
        new_best_energy : float = min([mol.energy for mol in self.population])
        if new_best_energy < self.best_energy:
            self.best_energy = new_best_energy
            self.best_energy_loops = 0
        else:
            self.best_energy_loops+= 1

    """
    def loop(self) -> bool:
        self.cycle_counter+= 1

        self.remove_unfeasible()
        self.remove_duplicates()

        children : list[Individual] = self.reproduce()
        mutants : list[Individual] = self.mutate()
        generated : list[Individual] = self.generate()

        self.population+= children
        self.population+= mutants
        self.population+= generated

        self.remove_duplicates()

        self.get_best_energy()
        return self.best_energy_loops < self.end_loop_number
    """

    def loop(self) -> bool:
        self.cycle_counter+= 1

        children : list[Individual] = self.reproduce()
        mutants : list[Individual] = self.mutate()
        generated : list[Individual] = self.generate()

        self.population+= children
        self.population+= mutants
        self.population+= generated

        self.remove_duplicates()
        self.remove_excess()

        self.get_best_energy()
        return self.best_energy_loops < self.end_loop_number


    def save(self, file : str) -> None:
        print(file)
        # Do later
        pass
