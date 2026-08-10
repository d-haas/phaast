from __future__ import annotations
import time
from typing import Any, Iterable, Optional, Sequence, TypedDict, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from phaast.surface_explorator.genetic.individual import IndividualData
import json, random, re, base64
from math import floor

from phaast.calculators.xtb import XTB
from phaast.computer import Computer
from phaast.structure import Structure
from phaast.structure.comparator import ComparisonAlgorithm, GrigoryanSpringborg
from phaast.surface_explorator import SurfaceExplorator
from phaast.surface_explorator.genetic.migration import Migrator
from phaast.surface_explorator.genetic.mutation import Mutator
from phaast.surface_explorator.genetic.crossover import Crossover
from phaast.surface_explorator.genetic.individual import ChildIndividual, Individual, MutantIndividual, OptimizedIndividual

from phaast.utils import ObjectData, import_object
from phaast.utils.custom_iter import distinct_pairs

class GenerationData(TypedDict):
    best_energy : list[float]
    population  : list[int]

class GeneticData(TypedDict):

    population_size          : int
    end_loop_number          : int

    do_remove_unbonded       : bool
    bonding_tolerance        : float

    sequential_mutations     : int
    mutation_batches         : int

    cycle_counter            : int
    minimum_lifetime         : int
    best_energy              : float
    best_energies            : list[int]
    best_energy_loops        : int
    best_energy_num          : int

    total_optimizations      : int
    total_converged          : int
    total_duplicates_removed : int
    total_unfeasible_removed : int
    total_not_bonded_removed : int
    total_mutations          : int
    total_mating             : int
    total_migrated           : int

    generations              : list[GenerationData]
    population               : list[int]
    population_ids           : dict[int, IndividualData]
    #population_ids           : list[str]
    max_id                   : int

    mutations                : list[tuple[float, ObjectData]]
    crossovers               : list[tuple[float, ObjectData]]
    migrators                : list[tuple[float, ObjectData]]

    comparison_algorithm     : ObjectData

class PopulationRegister(dict[int, Individual]):
    def __init__(self, init : dict[int, Individual] = {}):
        super().__init__(init)

    def __setitem__(self, key : int, value : Individual):
        if key in self:
            raise KeyError(f"Id [{repr(key)}] was already set in this population:\n{self}")
        else:
            super().__setitem__(key, value)

    def as_data(self, max_id) -> list[str]:
        population_bins : list[str] = []
        for i in range(max_id):
            if i in self:
                population_bins.append(
                    base64.b64encode(self[i].as_bytes()).decode("ascii")
                )
            else:
                population_bins.append("")

        return population_bins


    @classmethod
    def from_data(cls, data : list[str]) -> PopulationRegister:
        return PopulationRegister(
            {
                i : Individual.from_bytes(base64.b64decode(v.encode("ascii")))
                for i, v in enumerate(data)
                if v
            }
        )

class GeneticComputer(Computer):
    parent               : Genetic
    chosen_calculator    : str
    mutation_time_ns     : int
    crossover_time_ns    : int
    migration_time_ns    : int
    optimization_time_ns : int
    duplicate_time_ns    : int
    def __init__(self, parent : Genetic, computer : Computer, calculator : str):
        super().__init__(computer.cpu_count_limit)
        self.parent = parent
        self.calculators = computer.calculators
        self.chosen_calculator : str = calculator
        self.mutation_time_ns     = 0
        self.crossover_time_ns    = 0
        self.migration_time_ns    = 0
        self.optimization_time_ns = 0
        self.duplicate_time_ns    = 0

    @property
    def mutation_time(self) -> float:
        return self.mutation_time_ns/1e9
    @property
    def crossover_time(self):
        return self.crossover_time_ns/1e9
    @property
    def migration_time(self):
        return self.migration_time_ns/1e9
    @property
    def optimization_time(self):
        return self.optimization_time_ns/1e9
    @property
    def duplicate_time(self):
        return self.duplicate_time_ns/1e9

    def mutate(self, structs : Iterable[Individual], mutator : Mutator) -> list[MutantIndividual]:
        start = time.monotonic_ns()

        mutants = self.parallelize(
            [(struct,) for struct in structs],
            mutator,
        )

        inds = [
            MutantIndividual(mutant, ancestor.id, self.parent.max_id + i)
            for i, (mutant, ancestor)
            in enumerate(zip(mutants, structs))
        ]
        self.parent.max_id+= len(inds)
        for ind in inds:
            self.parent.population_ids[ind.id] = ind
            self.parent.population_ids[ind.ancestor].add_descendant(ind.id)

        self.parent.total_mutations+= len(mutants)

        self.mutation_time_ns+= time.monotonic_ns()-start

        return inds

    def crossover(
        self,
        struct_pairs : Iterable[tuple[Individual, Individual]],
        crossover : Crossover
    ) -> list[ChildIndividual]:

        start = time.monotonic_ns()

        children = self.parallelize(
            struct_pairs,
            crossover,
        )

        inds = [
            ChildIndividual(child, (parents[0].id, parents[1].id), self.parent.max_id + i)
            for i, (child, parents)
            in enumerate(zip(children, struct_pairs))
        ]
        self.parent.max_id+= len(inds)
        for ind in inds:
            self.parent.population_ids[ind.id] = ind
            for parent_id in ind.parents:
                self.parent.population_ids[parent_id].add_descendant(ind.id)

        self.parent.total_mating+= len(children)

        self.crossover_time_ns+= time.monotonic_ns()-start

        return inds

    def migrate(self, num : int, migrator : Migrator) -> list[Individual]:
        start = time.monotonic_ns()

        new_born = self.parallelize(num, migrator)

        inds = [
            Individual(struct, self.parent.max_id + i)
            for i, struct in enumerate(new_born)
        ]
        self.parent.max_id+= len(inds)
        for ind in inds: self.parent.population_ids[ind.id] = ind

        self.parent.total_migrated+= num

        self.migration_time_ns+= time.monotonic_ns()-start

        return inds

    def genetic_optimize(self, structs : Iterable[Individual]) -> list[OptimizedIndividual]:
        start = time.monotonic_ns()

        mols = [mol for mol in self.optimize(self.chosen_calculator, structs) if mol]

        inds = [
            OptimizedIndividual(mol, struct.id, self.parent.max_id + i, mol.energy)
            for i, (mol, struct)
            in enumerate(zip(mols, structs))
        ]
        self.parent.max_id+= len(inds)
        for ind in inds:
            self.parent.population_ids[ind.id] = ind
            self.parent.population_ids[ind.ancestor].add_descendant(ind.id)

        self.parent.total_optimizations+= len(list(structs)) # This list(...) is dumb and shouldn't be used... Anyway..
        self.parent.total_converged+= len(mols)

        self.optimization_time_ns+= time.monotonic_ns()-start

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
        i_id = inds[i].id
        i_energy = inds[i].energy
        for rng in ( range(i), range(i+1, len(inds)) ):
            for j in rng:
                if comparison_algorithm(inds[i], inds[j]):
                    j_id = inds[j].id
                    j_energy = inds[j].energy
                    if i_energy > j_energy:
                        return True
                    elif i_energy == j_energy and i_id > j_id:
                        return True

        return False

    def get_duplicate_mask(self, inds : Sequence[OptimizedIndividual], comparison_algorithm : ComparisonAlgorithm) -> list[bool]:
        start = time.monotonic_ns()

        mask = self.parallelize(
            [
                (i, inds, comparison_algorithm)
                for i in range(len(inds))
            ],
            self.get_duplicate,
        )
        self.parent.total_duplicates_removed+= mask.count(True)

        self.duplicate_time_ns+= time.monotonic_ns()-start

        return mask


class Genetic(SurfaceExplorator):
    population_growth : int
    population_limit  : int
    population        : list[OptimizedIndividual]
    generations       : list[list[OptimizedIndividual]]
    population_ids    : PopulationRegister
    end_loop_number   : int

    calculator          : str
    computer            : GeneticComputer

    comparison_algorithm : ComparisonAlgorithm
    do_remove_unbonded   : bool
    do_remove_unfeasible : bool

    mutations  : list[tuple[float, Mutator]]
    crossovers : list[tuple[float, Crossover]]
    migrators  : list[tuple[float, Migrator]]
    operations_weight : float
    sequential_mutations : int
    mutation_batches : int

    cycle_counter       : int
    minimum_lifetime    : int
    best_energy         : float
    best_energies       : list[OptimizedIndividual]
    best_energy_history : list[list[float]]
    best_energy_num     : int
    best_energy_loops   : int
    last_diff           : list[bool]
    max_id              : int

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

        population_limit : int = 0,

        comparison_algorithm : ComparisonAlgorithm = GrigoryanSpringborg(0.85),
        do_remove_unbonded    : bool = True,
        do_remove_unfeasible  : bool = False,

        minimum_lifetime : int = -1,

        end_loop_number : int = 9,

        best_energy_num : int = 10,

        bonding_tolerance : float = 0.25,

        custom_population : list[Structure] | None = None,

        generate_population : bool = True,

        loaded : bool = False,
    ):
        """
        Define initial variables for genetic algorithm
        """
        self.computer = GeneticComputer(self, computer, calculator)
        self.population_ids = PopulationRegister()
        self.max_id   = 0
        self.population = []
        self.population_growth = population_size
        if population_limit and population_limit > 0:
            self.population_limit = population_limit
        else:
            self.population_limit = population_size

        self.generations = []
        self.mutations = mutations
        self.crossovers = crossovers
        self.migrators = migrators

        self.sequential_mutations = sequential_mutations
        self.mutation_batches = mutation_batches

        self.comparison_algorithm = comparison_algorithm
        self.do_remove_unbonded   = do_remove_unbonded
        self.do_remove_unfeasible = do_remove_unfeasible

        self.end_loop_number      = end_loop_number
        self.cycle_counter        = 0
        self.minimum_lifetime     = minimum_lifetime
        self.best_energy_num      = best_energy_num
        self.best_energy_loops    = 0

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

        if not loaded:
            if custom_population:
                self.population+= self.computer.incorporate(custom_population)

            if generate_population:
                migrator_total_weight = sum([weight for weight, _ in migrators])
                for weight, migrator in migrators:
                    generated_num = floor(self.population_growth*weight/migrator_total_weight)
                    self.population+= self.computer.genetic_optimize(
                        self.computer.migrate(
                            generated_num,
                            migrator,
                        )
                    )

            self.generations.append(self.population.copy())

            self.best_energies       = sorted(self.population, key = lambda mol : mol.energy)[:min(self.best_energy_num, len(self.population))]
            self.best_energy         = self.best_energies[0].energy
            self.best_energy_history = [[ind.energy for ind in self.best_energies], ]

        else:
            self.best_energies       = []
            self.best_energy         = 0
            self.best_energy_history = []


        self.last_diff : list[bool] = []
        self.operations_weight = sum([
            weight for weight, _
            in mutations+crossovers+migrators
        ])

    def remove_duplicates(self) -> None:

        self.population = [
            ind
            for ind, is_duplicate
            in zip(
                self.population,
                self.computer.get_duplicate_mask(self.population, self.comparison_algorithm),
            )
            if not is_duplicate #or ( ind in self.best_energies )
        ]

    def migrate(self) -> list[OptimizedIndividual]:
        """
        Run the migration algorithm and return the optimized individuals as a list.
        """
        migrated : list[Individual] = []

        for weight, migrator in self.migrators:
            op_num : int = floor(self.population_growth*weight/self.operations_weight)

            migrated+= self.computer.migrate(op_num, migrator)

        migrated_individuals = self.computer.genetic_optimize(migrated)

        return migrated_individuals

    def reproduce(self) -> list[OptimizedIndividual]:
        """
        Run the crossover algorithms for random individuals in population and
        return the optimized children as a list.
        """
        children : list[ChildIndividual] = []

        for weight, crossover in self.crossovers:
            op_num : int = floor(self.population_growth*weight/self.operations_weight)

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
        """
        Run the mutation algorithms for random individuals in population and
        return the optimized ancestors as a list.
        """
        mutants : list[MutantIndividual] = []

        if self.sequential_mutations > 1:
            operation_pools = [
                random.choices(
                    *list(zip(*self.mutations))[::-1],
                    k = self.sequential_mutations,
                )
                for _ in range(self.mutation_batches)
            ]
            mutations_weight = sum([
                weight for weight, _
                in self.mutations
            ])/self.mutation_batches
            op_num : int = floor(
                self.population_growth*mutations_weight/self.operations_weight,
            )

            for pool in operation_pools:
                temp_mutants = random.choices(
                    self.population,
                    k = op_num,
                    #weights = [ind.energy**2 for ind in self.population],
                )

                for operation in pool:
                    temp_mutants = self.computer.mutate(
                        temp_mutants,
                        operation,
                    )

                mutants+= cast(list[MutantIndividual], temp_mutants)

        else:
            for weight, mutation in self.mutations:
                op_num : int = floor(
                    self.population_growth*weight/self.operations_weight,
                )

                chosen_mutants = random.choices(
                    self.population,
                    k = op_num,
                    weights = [ind.energy**2 for ind in self.population],
                )
                mutants+= self.computer.mutate(
                    chosen_mutants,
                    mutation,
                )

        mutant_molecules : list[OptimizedIndividual]
        mutant_molecules = self.computer.genetic_optimize(mutants)

        return mutant_molecules

    def remove_unfeasible(self) -> None:
        """
        Cap population by defined ceil (self.population_limit) keeping the least
        energy individuals.
        """
        pop_size_before = len(self.population)

        self.population = sorted(
            self.population,
            key = lambda ind : ind.energy,
        )[:min(self.population_limit, len(self.population))]

        pop_size_after = len(self.population)

        self.total_unfeasible_removed+= pop_size_before - pop_size_after

    def remove_unbonded(self) -> None:
        """
        Removed unbonded states
        """
        pop_size_before = len(self.population)

        self.population = [
            ind for ind in self.population
            if ind.is_bonded(self.bonding_tolerance) #or ind.generations_alive <= self.minimum_lifetime
        ]

        pop_size_after = len(self.population)

        self.total_not_bonded_removed+= pop_size_before - pop_size_after

    def get_best_energy(self) -> list[bool]:
        """
        Refresh algorithm's energy list with the new ones and reset energy loop
        counter if it has changed or add 1 otherwise
        """
        new_best_energies : list[OptimizedIndividual] = sorted(
            # New energies
            self.population,
            key = lambda ind : (ind.energy, ind.id),
        )[ : min( self.best_energy_num, len(self.population) ) ]

        if len(new_best_energies) == len(self.best_energies):
            ind_equals : list[bool] = [
                # A list that determines if the last best energies are equal to
                # the new ones, even if the structure are not the same
                # (but are geometrically/energetically equal)
                ind_a.id == ind_b.id or self.comparison_algorithm(ind_a, ind_b)
                for ind_a, ind_b
                in zip(self.best_energies, new_best_energies)
            ]
            if all(ind_equals):
                self.best_energy_loops+= 1
            else:
                self.best_energy_loops = 0
        else:
            ind_equals = []
            self.best_energy_loops = 0

        self.best_energies = new_best_energies
        self.best_energy = new_best_energies[0].energy
        self.best_energy_history.append( [ind.energy for ind in self.best_energies] )

        return [not i for i in ind_equals]

    def loop(self) -> bool:
        """
        Run the main Genetic Algorithm's loop, returning true if it should
        continue or not (termination criteria met).
        """
        if len(self.population) == 0:
            print("Population was erradicated, can't proceed correctly with algorithm")
        if len(self.population) < 10:
            print("Population length is not enough to proceed with genetic algorithm properly")

        self.cycle_counter+= 1

        if len(self.population) > 0:
            children : list[OptimizedIndividual] = self.reproduce()
            mutants  : list[OptimizedIndividual] = self.mutate()
        else:
            children, mutants = [], []


        migrated : list[OptimizedIndividual] = self.migrate()

        self.population+= children
        self.population+= mutants
        self.population+= migrated

        if self.do_remove_unbonded: self.remove_unbonded()
        if self.do_remove_unfeasible: self.remove_unfeasible()

        self.remove_duplicates()

        self.last_diff = self.get_best_energy()

        self.generations.append(self.population.copy())

        return self.best_energy_loops < self.end_loop_number


    def as_data(self) -> GeneticData:
        """
        Wrap the actual state of the genetic algorithm as a GeneticData type,
        which can be stored as a JSON file for later import.
        """
        results : GeneticData = {
            "population_size"          : self.population_growth,
            "end_loop_number"          : self.end_loop_number,

            "cycle_counter"            : self.cycle_counter,
            "minimum_lifetime"         : self.minimum_lifetime,
            "best_energy"              : self.best_energy,
            "best_energies"            : [ind.id for ind in self.best_energies],
            "best_energy_loops"        : self.best_energy_loops,
            "best_energy_num"          : self.best_energy_num,

            "total_optimizations"      : self.total_optimizations,
            "total_converged"          : self.total_converged,
            "total_duplicates_removed" : self.total_duplicates_removed,
            "total_unfeasible_removed" : self.total_unfeasible_removed,
            "total_not_bonded_removed" : self.total_not_bonded_removed,
            "total_mutations"          : self.total_mutations,
            "total_mating"             : self.total_mating,
            "total_migrated"           : self.total_migrated,

            "generations"              : [
                {
                    "best_energy" : self.best_energy_history[i],
                    "population"  : [ind.id for ind in gen],
                }
                for i, gen in enumerate(self.generations)
            ],
            "population"               : [ind.id for ind in self.population],
            "population_ids"           : { k : v.as_data() for k, v in self.population_ids.items() },
            #"population_ids"           : self.population_ids.as_data(self.max_id),
            "max_id"                   : self.max_id,

            "mutations"                : [(weight, mutation.as_data()) for weight, mutation in self.mutations],
            "crossovers"               : [(weight, crossover.as_data()) for weight, crossover in self.crossovers],
            "migrators"                : [(weight, migrator.as_data()) for weight, migrator in self.migrators],

            "comparison_algorithm"     : self.comparison_algorithm.as_data(),

            "do_remove_unbonded"       : self.do_remove_unbonded,
            "bonding_tolerance"        : self.bonding_tolerance,

            "mutation_batches"         : self.mutation_batches,
            "sequential_mutations"     : self.sequential_mutations,
        }

        return results

    def save(self, file_path : str = "phaast_genetic") -> None:
        """
        Save the algorithm as a json file.
        """
        if not file_path.endswith(".json"): file_path+= ".json"

        with open(file_path, "w") as file: 

            json_string = json.dumps(
                self.as_data(),
                sort_keys = True,
            )

            file.write(json_string)

    @classmethod
    def from_data(cls, data : GeneticData, computer : Optional[Computer] = None, calculator_key : str = "xtb") -> Genetic:
        if computer is None:
            computer = Computer()
            xtb = XTB()
            computer.add_calculator(calculator_key, xtb)

        population_ids = PopulationRegister()
        for i, v in data["population_ids"].items():
            population_ids[int(i)] = Individual.from_data(v)

        algorithm = Genetic(
            population_size      = data["population_size"],
            computer             = computer, 
            calculator           = calculator_key,

            mutations            = [(weight, import_object(obj_data)) for weight, obj_data in data["mutations"]], # type: ignore[override]
            crossovers           = [(weight, import_object(obj_data)) for weight, obj_data in data["crossovers"]], # type: ignore[override],
            migrators            = [(weight, import_object(obj_data)) for weight, obj_data in data["migrators"]], # type: ignore[override]

            mutation_batches     = data["mutation_batches"],
            sequential_mutations = data["sequential_mutations"],

            comparison_algorithm = import_object(data["comparison_algorithm"]), # type: ignore[override]
            do_remove_unbonded   = data["do_remove_unbonded"],

            minimum_lifetime     = data["minimum_lifetime"],

            end_loop_number      = data["end_loop_number"],
            best_energy_num      = data["best_energy_num"],

            bonding_tolerance    = data["bonding_tolerance"],

            loaded               = True,
        )

        algorithm.population_ids = population_ids
        algorithm.generations = [
            [
                cast(OptimizedIndividual, population_ids[id])
                for id in gen["population"]
            ] for gen in data["generations"]
        ]
        algorithm.best_energy_history = [
            gen["best_energy"]
            for gen in data["generations"]
        ]
        algorithm.best_energies = [
            cast(OptimizedIndividual, population_ids[id])
            for id in data["best_energies"]
        ]
        algorithm.population = [
            cast(OptimizedIndividual, population_ids[id])
            for id in data["population"]
        ]

        for attr, value in data.items():
            if isinstance(value, (int, float, bool)):
                setattr(algorithm, attr, value)

        return algorithm


    @classmethod
    def load(cls, file_path : str) -> Genetic:
        with open(file_path, "r") as file:
            data : GeneticData = json.load(file)
            return Genetic.from_data(data)

    def get_report(self) -> dict[str, Any]:
        report = {
            "Population Size"          : self.population_growth,
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

            "Migration Time"           : self.computer.migration_time,
            "Crossover Time"           : self.computer.crossover_time,
            "Mutation Time"            : self.computer.mutation_time,
            "Optimization Time"        : self.computer.optimization_time,
            "Duplicate removal time"   : self.computer.duplicate_time,

            "Minima"                   : [ind.as_data() for ind in self.get_best(self.best_energy_num)],
        }

        return report

    def save_report(self, file_path : str = "phaast_report") -> None:
        if not file_path.endswith(".json"): file_path+= ".json"

        with open(file_path, "w") as file: 

            json_string = json.dumps(
                self.get_report(),
                sort_keys = True,
                indent = "  ",
            )

            file.write(json_string)

    def get_best(self, n : int = 10) -> list[OptimizedIndividual]:
        return sorted(
            self.population,
            key = lambda ind : ind.energy,
        )[ : min(n, len(self.population) ) ]

    #Using list constructor as default might result in some shenanigans
    def status(self, fields : Iterable[str] = ()):
        return "\n".join(
            [
                "╔"+"═"*59+"╗",
            ] + [
                "║"+line.ljust(59)+"║"
                for line in fields
            ] + [
                "║"+f" Generation {self.cycle_counter} done".ljust(59)+"║",
                "║"+f" Best energy: {self.best_energy}{"*" if any(self.last_diff) else ""}".ljust(59)+"║",
                "║"+f" Population size: {len(self.population)}".ljust(59)+"║",
                "╚"+"═"*59+"╝",
            ],
        )

    def statistics(self, fields : list[str] = []) -> str:
        fields = fields if fields else []

        lines = fields + [
            f"Total optimizations: {self.total_optimizations} "
            f"({self.computer.optimization_time} s)",

            f"Total converged: {self.total_converged}",

            f"Total duplicates removed: {self.total_duplicates_removed} "
            f"({self.computer.duplicate_time} s)",

            f"Total unfeasible removed: {self.total_unfeasible_removed}",

            f"Total not-bonded removed: {self.total_not_bonded_removed}",

            f"Total migration: {self.total_migrated} "
            f"({self.computer.migration_time} s)",

            f"Total mutations: {self.total_mutations} "
            f"({self.computer.mutation_time} s)",

            f"Total crossovers: {self.total_mating} "
            f"({self.computer.crossover_time} s)",
        ]

        return "\n".join(
            [
                f"╔{"═"*59}╗",
            ] + [
                f"║{line.ljust(59)}║"
                for line in lines
            ] + [
                f"╚{"═"*59}╝",
            ]
        )
