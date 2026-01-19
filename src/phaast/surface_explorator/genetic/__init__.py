import random
from typing import Callable, Iterable
from math import floor

from phaast.structure.geometry import grigoryan_springborg

from phaast.surface_explorator.genetic.migration import Migrator
from phaast.surface_explorator.genetic.mutation import Mutator
from phaast.surface_explorator.genetic.crossover import Crossover
from phaast.surface_explorator.genetic.individual import Individual
from phaast.surface_explorator.genetic.duplicate import remove_duplicates

from phaast.computer import Computer
from phaast.structure import Base, Molecule, Structure

from phaast.surface_explorator import SurfaceExplorator
from phaast.utils.custom_iter import distinct_pairs

class GeneticComputer(Computer):
    def __init__(self, computer : Computer):
        super().__init__(computer.cpu_count_limit)
        self.calculators = computer.calculators

    def mutate(self, structs : Iterable[Structure], mutator : Mutator) -> list[Structure]:
        return self.parallelize(
            ((struct,) for struct in structs),
            mutator,
        )

    def crossover(self, struct_pairs : Iterable[tuple[Structure, Structure]], crossover : Crossover) -> list[Structure]:
        return self.parallelize(
            struct_pairs,
            crossover,
        )

    def migrate(self, num : int, migrator : Migrator) -> list[Structure]:
        return self.parallelize(num, migrator)

class Genetic(SurfaceExplorator):
    population_size : int
    population      : list[Individual]
    end_loop_number : int

    calculator          : str
    computer            : GeneticComputer
    base                : Base

    energy_threshold     : float
    geometry_threshold   : float
    comparison_algorithm : Callable[[Molecule, Molecule], float]
    do_remove_unbonded   : bool

    mutations : list[tuple[float, Mutator]]
    crossovers : list[tuple[float, Crossover]]
    migrators : list[tuple[float, Migrator]]
    operations_weight : float
    sequential_mutations : int
    mutation_batches : int

    cycle_counter     : int
    minimum_lifetime  : int
    best_energy       : float
    best_energy_loops : int

    total_optimizations          : int
    total_converged              : int
    total_duplicates_removed     : int
    total_unfeasible_removed     : int
    total_not_bonded_removed     : int
    total_mutations              : int
    total_mating                 : int
    total_migrated               : int

    def __init__(
        self,
        base : Base,
        population_size : int,
        computer : Computer,
        energy_threshold : float,
        geometry_threshold : float,
        calculator : str,

        mutations  : list[tuple[float, Mutator]],
        crossovers : list[tuple[float, Crossover]],
        migrators  : list[tuple[float, Migrator]],
        sequential_mutations : int = 1,
        mutation_batches : int = 10,

        comparison_algorithm : Callable[[Molecule, Molecule], float] = grigoryan_springborg,
        do_remove_unbonded    : bool = True,

        minimum_lifetime : int = -1,

        end_loop_number : int = 9,

        bonding_tolerance : float = 0.25,
    ):
        """
        Define initial variables for genetic algorithm
        """
        self.computer = GeneticComputer(computer)
        self.calculator = calculator
        if population_size < 100:
            raise ValueError(
                "Population size is too small",
            )
        self.base = base
        self.population_size = population_size
        self.population : list[Individual] = []

        migrator_total_weight = sum([weight for weight, _ in migrators])
        for weight, migrator in migrators:
            generated_num = floor(self.population_size*weight/migrator_total_weight)
            self.population+= [
                Individual(mol) for mol
                in computer.optimize(
                    self.calculator,
                    self.computer.migrate(
                        generated_num,
                        migrator,
                    )
                )
            ]

        self.mutations = mutations
        self.crossovers = crossovers
        self.migrators = migrators
        self.operations_weight = sum([
            weight for weight, _
            in mutations+crossovers+migrators
        ])
        self.sequential_mutations = sequential_mutations
        self.mutation_batches = mutation_batches

        self.energy_threshold     = energy_threshold
        self.geometry_threshold   = geometry_threshold
        self.comparison_algorithm = comparison_algorithm
        self.do_remove_unbonded    = do_remove_unbonded

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
        self.total_not_bonded_removed     = 0
        self.total_mutations              = 0
        self.total_mating                 = 0
        self.total_migrated               = 0

        self.bonding_tolerance            = bonding_tolerance

    def remove_duplicates(self) -> None:

        pop_size_before : int = len(self.population)

        self.population = remove_duplicates(
            self.computer,
            self.population,
            self.energy_threshold,
            self.geometry_threshold,
            self.comparison_algorithm,
        )

        pop_size_after : int = len(self.population)

        self.total_duplicates_removed = pop_size_before - pop_size_after

    def migrate(self) -> list[Individual]:
        migrated : list[Structure] = []

        for weight, migrator in self.migrators:
            op_num : int = floor(self.population_size*weight/self.operations_weight)

            migrated+= self.computer.migrate(op_num, migrator)

        migrated_individuals = [
            Individual(mol) for mol
            in self.computer.optimize(self.calculator, migrated)
            if mol is not None
        ]

        self.total_migrated+= len(migrated)
        self.total_optimizations+= len(migrated)
        self.total_converged+= len(migrated_individuals)

        return migrated_individuals

    def reproduce(self) -> list[Individual]:
        children : list[Structure] = []

        for weight, crossover in self.crossovers:
            op_num : int = floor(self.population_size*weight/self.operations_weight)

            chosen_parents = random.choices(
                list(distinct_pairs(self.population)),
                k = op_num,
            )

            children+= self.computer.crossover(
                chosen_parents,
                crossover,
            )

        children_individuals = [
            Individual(mol) for mol
            in self.computer.optimize(self.calculator, children)
            if mol is not None
        ]

        self.total_optimizations+= len(children)
        self.total_converged+= len(children_individuals)
        self.total_mating+= len(children)

        return children_individuals

    def mutate(self) -> list[Individual]:
        mutants : list[Structure] = []

        if self.sequential_mutations > 1:
            operation_pools = [
                random.choices(
                    *list(zip(*self.mutations))[::-1], # This is basically both lists of mutators and weights
                    k = self.sequential_mutations,
                )
                for _ in range(self.mutation_batches)
            ]
            mutations_weight = sum([
                weight for weight, _
                in self.mutations
            ])/self.mutation_batches
            op_num : int = floor(self.population_size*mutations_weight/self.operations_weight)

            for pool in operation_pools:
                temp_mutants = random.choices(
                    self.population,
                    k = op_num,
                )

                for operation in pool:
                    temp_mutants = self.computer.mutate(
                        temp_mutants,
                        operation,
                    )

                mutants+= temp_mutants

        else:
            for weight, mutation in self.mutations:
                op_num : int = floor(self.population_size*weight/self.operations_weight)

                chosen_mutants = random.choices(
                    self.population,
                    k = op_num,
                )
                mutants+= self.computer.mutate(
                    chosen_mutants,
                    mutation,
                )

        mutant_molecules : list[Individual] = [
            Individual(mol) for mol
            in self.computer.optimize(self.calculator, mutants)
            if mol is not None
        ]

        self.total_optimizations+= len(mutants)
        self.total_converged+= len(mutant_molecules)
        self.total_mutations+= len(mutants)*self.sequential_mutations

        return mutant_molecules

    def remove_unfeasible(self) -> None:
        min_energy : float = min(
            [mol.energy for mol in self.population]
        )
        max_energy : float = max(
            [mol.energy for mol in self.population]
        )
        median_energy : float = (min_energy + max_energy)/2

        pop_size_before = len(self.population)

        for ind in self.population:
            ind.generations_alive+= 1

        self.population = [
            ind for ind in self.population
            if ind.energy <=median_energy or ind.generations_alive <= self.minimum_lifetime
        ]

        pop_size_after = len(self.population)

        self.total_unfeasible_removed+= pop_size_before - pop_size_after

    def remove_unbonded(self) -> None:

        pop_size_before = len(self.population)

        self.population = [
            ind for ind in self.population
            if ind.is_bonded(self.bonding_tolerance) or ind.generations_alive <= self.minimum_lifetime
        ]

        pop_size_after = len(self.population)

        self.total_not_bonded_removed+= pop_size_before - pop_size_after

    def get_best_energy(self) -> None:
        new_best_energy : float = min([mol.energy for mol in self.population])
        if new_best_energy < self.best_energy:
            self.best_energy = new_best_energy
            self.best_energy_loops = 0
        else:
            self.best_energy_loops+= 1

    def loop(self) -> bool:
        self.cycle_counter+= 1

        children : list[Individual] = self.reproduce()
        mutants : list[Individual] = self.mutate()
        migrated : list[Individual] = self.migrate()

        self.population+= children
        self.population+= mutants
        self.population+= migrated

        self.remove_duplicates()
        if self.do_remove_unbonded:
            self.remove_unbonded()

        self.get_best_energy()

        return self.best_energy_loops < self.end_loop_number


    def save(self, file : str) -> None:
        print(file)
        # Do later
        pass
