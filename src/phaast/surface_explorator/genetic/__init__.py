from __future__ import annotations
import random
import re
from typing import Any, Iterable, Self, Sequence, TypedDict, cast
from math import floor
import json

from phaast.computer import Computer
from phaast.structure import Molecule, Structure
from phaast.structure.comparator import ComparisonAlgorithm, GrigoryanSpringborg
from phaast.surface_explorator import SurfaceExplorator
from phaast.surface_explorator.genetic.migration import Migrator
from phaast.surface_explorator.genetic.mutation import Mutator
from phaast.surface_explorator.genetic.crossover import Crossover
from phaast.surface_explorator.genetic.individual import ChildIndividual, Individual, MutantIndividual, OptimizedIndividual

from phaast.utils import JsonType
from phaast.utils.custom_iter import distinct_pairs

class GeneticData(TypedDict):

    population_size          : int
    end_loop_number          : int

    cycle_counter            : int
    minimum_lifetime         : int
    best_energy              : float
    best_energy_loops        : int

    total_optimizations      : int
    total_converged          : int
    total_duplicates_removed : int
    total_unfeasible_removed : int
    total_not_bonded_removed : int
    total_mutations          : int
    total_mating             : int
    total_migrated           : int

    generations              : list[list[int]]
    population               : list[int]
    population_ids           : dict[int, JsonType]

class PopulationRegister(dict[int, Individual]):
    def __init__(self):
        super().__init__()

    def __setitem__(self, key : int, value : Individual):
        if key in self:
            raise KeyError(f"Id [\"{key}\"] was already set in this population:\n{self}")
        else:
            super().__setitem__(key, value)

class GeneticComputer(Computer):
    def __init__(self, parent : Genetic, computer : Computer, calculator : str):
        super().__init__(computer.cpu_count_limit)
        self.parent = parent
        self.calculators = computer.calculators
        self.chosen_calculator : str = calculator

    def mutate(self, structs : Iterable[Individual], mutator : Mutator) -> list[MutantIndividual]:
        mutants = self.parallelize(
            ((struct,) for struct in structs),
            mutator,
        )

        inds = [
            MutantIndividual(mutant, ancestor, self.parent.max_id + i)
            for i, (mutant, ancestor)
            in enumerate(zip(mutants, structs))
        ]
        self.parent.max_id+= len(inds)
        for ind in inds: self.parent.population_ids[ind.id] = ind

        self.parent.total_mutations+= len(mutants)

        return inds

    def crossover(self, struct_pairs : Iterable[tuple[Individual, Individual]], crossover : Crossover) -> list[ChildIndividual]:
        children = self.parallelize(
            struct_pairs,
            crossover,
        )

        inds = [
            ChildIndividual(child, parents, self.parent.max_id + i)
            for i, (child, parents)
            in enumerate(zip(children, struct_pairs))
        ]
        self.parent.max_id+= len(inds)
        for ind in inds: self.parent.population_ids[ind.id] = ind

        self.parent.total_mating+= len(children)

        return inds

    def migrate(self, num : int, migrator : Migrator) -> list[Individual]:
        new_born = self.parallelize(num, migrator)

        inds = [
            Individual(struct, self.parent.max_id + i)
            for i, struct in enumerate(new_born)
        ]
        self.parent.max_id+= len(inds)
        for ind in inds: self.parent.population_ids[ind.id] = ind

        self.parent.total_migrated+= num

        return inds

    def genetic_optimize(self, structs : Iterable[Individual]) -> list[OptimizedIndividual]:
        mols = [mol for mol in self.optimize(self.chosen_calculator, structs) if mol]

        inds = [
            OptimizedIndividual(mol, struct, self.parent.max_id + i, mol.energy)
            for i, (mol, struct)
            in enumerate(zip(mols, structs))
        ]
        self.parent.max_id+= len(inds)
        for ind in inds: self.parent.population_ids[ind.id] = ind

        self.parent.total_optimizations+= len(list(structs)) # This list(...) is dumb and shouldn't be used... Anyway..
        self.parent.total_converged+= len(mols)

        return inds

    def incorporate(self, structs : list[Structure]) -> list[OptimizedIndividual]:
        inds = [
            Individual(struct, self.parent.max_id + i)
            for i, struct in enumerate(structs)
        ]
        self.parent.max_id+= len(inds)
        for ind in inds: self.parent.population_ids[ind.id] = ind

        return self.genetic_optimize(inds)

    def get_duplicate(self, i : int, inds : Sequence[OptimizedIndividual], comparison_algorithm : ComparisonAlgorithm) -> bool:
        for j in range(i+1, len(inds)):
            if comparison_algorithm(inds[i], inds[j]):
                return True
        return False

    def get_duplicate_mask(self, inds : Sequence[OptimizedIndividual], comparison_algorithm : ComparisonAlgorithm) -> list[bool]:
        mask = self.parallelize(
            [(i, inds, comparison_algorithm) for i in range(len(inds))],
            self.get_duplicate,
        )
        return mask


class Genetic(SurfaceExplorator):
    population_size : int
    population      : list[OptimizedIndividual]
    generations     : list[list[OptimizedIndividual]]
    population_ids  : PopulationRegister
    end_loop_number : int

    calculator          : str
    computer            : GeneticComputer

    comparison_algorithm : ComparisonAlgorithm
    do_remove_unbonded   : bool

    mutations  : list[tuple[float, Mutator]]
    crossovers : list[tuple[float, Crossover]]
    migrators  : list[tuple[float, Migrator]]
    operations_weight : float
    sequential_mutations : int
    mutation_batches : int

    cycle_counter     : int
    minimum_lifetime  : int
    best_energy       : float
    best_energy_loops : int
    max_id            : int

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
        population_size : int,
        computer : Computer,
        calculator : str,

        mutations  : list[tuple[float, Mutator]],
        crossovers : list[tuple[float, Crossover]],
        migrators  : list[tuple[float, Migrator]],
        sequential_mutations : int = 1,
        mutation_batches : int = 10,

        comparison_algorithm : ComparisonAlgorithm = GrigoryanSpringborg(0.85),
        do_remove_unbonded    : bool = True,

        minimum_lifetime : int = -1,

        end_loop_number : int = 9,

        bonding_tolerance : float = 0.25,

        custom_population : list[Structure] | None = None,

        generate_population : bool = True,
    ):
        """
        Define initial variables for genetic algorithm
        """
        self.computer = GeneticComputer(self, computer, calculator)
        self.population_ids = PopulationRegister()
        self.max_id   = 0
        self.population : list[OptimizedIndividual] = []
        self.population_size = population_size
        self.generations = []
        self.mutations = mutations
        self.crossovers = crossovers
        self.migrators = migrators

        self.sequential_mutations = sequential_mutations
        self.mutation_batches = mutation_batches

        self.comparison_algorithm = comparison_algorithm
        self.do_remove_unbonded    = do_remove_unbonded

        self.end_loop_number   = end_loop_number
        self.cycle_counter     = 0
        self.minimum_lifetime  = minimum_lifetime
        self.best_energy_loops = 0

        # Statistic counters
        self.total_optimizations          = 0
        self.total_converged              = 0
        self.total_unfeasible_removed     = 0
        self.total_duplicates_removed     = 0
        self.total_not_bonded_removed     = 0
        self.total_mutations              = 0
        self.total_mating                 = 0
        self.total_migrated               = 0

        self.bonding_tolerance            = bonding_tolerance

        if population_size < 10:
            raise ValueError(
                "Population size is too small",
            )

        migrator_total_weight = sum([weight for weight, _ in migrators])
        for weight, migrator in migrators:
            generated_num = floor(self.population_size*weight/migrator_total_weight)
            self.population+= self.computer.genetic_optimize(
                self.computer.migrate(
                    generated_num,
                    migrator,
                )
            )
        print(f"Population size is {len(self.population)}")

        if None in self.population: raise ValueError("There is a None in the population")
        self.generations.append(self.population.copy())


        self.operations_weight = sum([
            weight for weight, _
            in mutations+crossovers+migrators
        ])

        # Generation parameters
        self.best_energy       = min([mol.energy for mol in self.population])

        #Statistics variables (start with prefix "total")

    def remove_duplicates(self) -> None:

        pop_size_before : int = len(self.population)

        self.population = [
            ind
            for ind, is_duplicate
            in zip(
                self.population,
                self.computer.get_duplicate_mask(self.population, self.comparison_algorithm),
            )
            if not is_duplicate
        ]

        pop_size_after : int = len(self.population)

        self.total_duplicates_removed = pop_size_before - pop_size_after

    def migrate(self) -> list[OptimizedIndividual]:
        migrated : list[Individual] = []

        for weight, migrator in self.migrators:
            op_num : int = floor(self.population_size*weight/self.operations_weight)

            migrated+= self.computer.migrate(op_num, migrator)

        migrated_individuals = self.computer.genetic_optimize(migrated)

        return migrated_individuals

    def reproduce(self) -> list[OptimizedIndividual]:
        children : list[ChildIndividual] = []

        for weight, crossover in self.crossovers:
            op_num : int = floor(self.population_size*weight/self.operations_weight)

            pairs : list[tuple[Individual, Individual]] = list(distinct_pairs(self.population))
            chosen_parents = random.choices(
                pairs,
                k = op_num,
            )

            children+= self.computer.crossover(
                chosen_parents,
                crossover,
            )

        children_individuals = self.computer.genetic_optimize(children)

        return children_individuals

    def mutate(self) -> list[OptimizedIndividual]:
        mutants : list[MutantIndividual] = []

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

                mutants+= cast(list[MutantIndividual], temp_mutants)

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

        mutant_molecules : list[OptimizedIndividual] = self.computer.genetic_optimize(mutants)

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
            if ind.energy <= median_energy or ind.generations_alive <= self.minimum_lifetime
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

        children : list[OptimizedIndividual] = self.reproduce()
        mutants  : list[OptimizedIndividual] = self.mutate()
        migrated : list[OptimizedIndividual] = self.migrate()

        self.population+= children
        self.population+= mutants
        self.population+= migrated

        self.remove_unfeasible()
        self.remove_duplicates()
        if self.do_remove_unbonded:
            self.remove_unbonded()

        self.get_best_energy()

        self.generations.append(self.population.copy())

        return self.best_energy_loops < self.end_loop_number

    def as_data(self) -> GeneticData:
        results = {
            "population_size"          : self.population_size,
            "end_loop_number"          : self.end_loop_number,

            "cycle_counter"            : self.cycle_counter,
            "minimum_lifetime"         : self.minimum_lifetime,
            "best_energy"              : self.best_energy,
            "best_energy_loops"        : self.best_energy_loops,

            "total_optimizations"      : self.total_optimizations,
            "total_converged"          : self.total_converged,
            "total_duplicates_removed" : self.total_duplicates_removed,
            "total_unfeasible_removed" : self.total_unfeasible_removed,
            "total_not_bonded_removed" : self.total_not_bonded_removed,
            "total_mutations"          : self.total_mutations,
            "total_mating"             : self.total_mating,
            "total_migrated"           : self.total_migrated,

            "generations"              : [],
        }

        results["generations"] = [
            [ind.id for ind in gen]
            for gen in self.generations
        ]

        results["population"] = [ind.id for ind in self.population]

        results["population_ids"] = {
            k : v.as_data()
            for k, v in self.population_ids.items()
        }
        return results

    def save(self, file_path : str) -> None:
        if not file_path.endswith(".json"): file_path+= ".json"

        with open(file_path, "w") as file:
            json_string = json.dumps(
                self.as_data(),
                sort_keys = True,
                indent = "  ",
            )

            # Removal of indentation in numeric lists was done with AI (improve that shit later)
            json_string_f = re.sub(
                r'\[[\s\d,\.\-]+\]',
                lambda match: re.sub(r'\s+', ' ', match.group(0)).replace('[ ', '[').replace(' ]', ']'),
                json_string
            )

            file.write(json_string_f)

    @classmethod
    def from_data(cls, data : dict[str, Any]) -> Self:
        #return Genetic()
        pass

    @classmethod
    def load(cls, file_path : str) -> Self:
        with open(file_path, "r") as file:
            data = json.load(file)
            return Genetic.from_data(data)

    def get_report(self) -> dict[str, Any]:
        report = {
            "Population Size"          : self.population_size,
            "End Loop Number"          : self.end_loop_number,

            "Cycle Counter"            : self.cycle_counter,
            "Minimum Lifetime"         : self.minimum_lifetime,
            "Best Energy"              : self.best_energy,
            "Best Energy Loops"        : self.best_energy_loops,

            "Total Optimizations"      : self.total_optimizations,
            "Total Converged"          : self.total_converged,
            "Total Duplicates Removed" : self.total_duplicates_removed,
            "Total Unfeasible Removed" : self.total_unfeasible_removed,
            "Total Not Bonded Removed" : self.total_not_bonded_removed,
            "Total Mutations"          : self.total_mutations,
            "Total Mating"             : self.total_mating,
            "Total Migrated"           : self.total_migrated,
        }
        optimizeds = [ind for ind in self.population_ids.values() if isinstance(ind, OptimizedIndividual)]
        report["Minima"] = sorted(
            optimizeds,
            key = lambda ind : ind.energy,
        )[0:min(len(optimizeds), 50)]

        return report

    def save_report(self, file_path : str = "phaast_report.json"):
        if not file_path.endswith(".json"): file_path+= ".json"

        with open(file_path, "w") as file:
            json_string = json.dumps(
                self.as_data(),
                sort_keys = True,
                indent = "  ",
            )

            # Removal of indentation in numeric lists was done with AI (improve that shit later)
            json_string_f = re.sub(
                r'\[[\s\d,\.\-]+\]',
                lambda match: re.sub(r'\s+', ' ', match.group(0)).replace('[ ', '[').replace(' ]', ']'),
                json_string
            )

            file.write(json_string_f)
