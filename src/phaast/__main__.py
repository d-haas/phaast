#!/usr/bin/env python3
import argparse
import time
import os
from typing import cast

from phaast.surface_explorator.genetic.crossover import PlaneMating
from phaast.surface_explorator.genetic.migration.hedron_universe import HedronMigrator
from phaast.surface_explorator.genetic.mutation import DisplacementMutator, PermuteMutator, TwistMutator

arg_parser = argparse.ArgumentParser(
    prog="P.H.A.A.S.T",
    description="A heuristic-algorithm-driven software made for global minima search",
    epilog="Thanks for choosing Phaast",
    formatter_class = argparse.RawTextHelpFormatter,
)

arg_parser.add_argument(
    "stoichiometry",
    help = "The structure composition (example = C6H6)",
)

arg_parser.add_argument(
    "output_prefix",
    help = "Prefix of the output files (a prefix of \"OUTPUT\" will result in files named OUTPUT0, OUTPUT1, ...)",
)

arg_parser.add_argument(
    "--return_number",
    type = int,
    default = 10,
    help = "Number of least energy molecules to return at the end of the algorithm (default = %(default)s)",
)

arg_parser.add_argument(
    "-pop",
    "--population_size",
    type = int,
    default = 10000,
    help = "Number of molecules in the population (default = %(default)s)",
)

arg_parser.add_argument(
    "-c",
    "--charge",
    type = int,
    default = 0,
    help = "Structure's charge (default = %(default)s)",
)

arg_parser.add_argument(
    "-t", "--threads",
    type = int,
    default = 0,
    help = "Number of threads to be used by the algorithm (default = number of threads on cpu)",
)

arg_parser.add_argument(
    "-xtbt", "--xtb-threads",
    type = int,
    default = 1,
    help = "Number of threads to be used by each -t xtb instance (default = %(default)s)",
)

arg_parser.add_argument(
    "--xtb_path",
    type = str,
    default = "xtb",
    help = "Path to be used for the xtb binary (default = %(default)s)",
)

arg_parser.add_argument(
    "-et",
    "--energy_threshold",
    type = float,
    default = 1e-3,
    help = "Maximum energy difference [in hartree] so molecules are considered alike (default = %(default)s)",
)

arg_parser.add_argument(
    "-gt",
    "--geometry_threshold",
    type = float,
    default = 0.9,
    help = "Maximum geometry difference so molecules are considered the same so one of them is discarded [must be a value between 0 and 1] (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_disp_w",
    type = float,
    default = 1,
    help = "Mutation displacement weight (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_perm_w",
    type = float,
    default = 1,
    help = "Mutation permutation weight (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_twist_w",
    type = float,
    default = 1,
    help = "Mutation twist weight (default = %(default)s)",
)

arg_parser.add_argument(
    "--crov_w",
    type = float,
    default = 1,
    help = "Crossing-over weight (default = %(default)s)",
)

arg_parser.add_argument(
    "--migr_w",
    type = float,
    default = 1,
    help = "Migrator weight (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_disp_min",
    type = float,
    default = 1.0,
    help = "Minimum distance (Å) to be used in mutation of atomic displacement (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_disp_max",
    type = float,
    default = 2.0,
    help = "Maximum distance (Å) to be used in mutation of atomic displacement (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_disp_num",
    type = int,
    default = 1,
    help = "Number of atoms to move in mutations of atomic displacement (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_perm_num",
    type = int,
    default = 0,
    help = "Number of permutations in mutations of that type (default = Half the number of atoms)",
)

arg_parser.add_argument(
    "--mut_twist_min_angle",
    type = float,
    default = 90,
    help = "Minimum angle to be used in twist mutations (default = %(default)s)",
)

arg_parser.add_argument(
    "--mut_twist_max_angle",
    type = float,
    default = 270,
    help = "Maximum angle to be used in twist mutations (default = %(default)s)",
)

arg_parser.add_argument(
    "-loops",
    "--end_loop_number",
    default = 11,
    type = int,
    help = "Number of loops the algorithm will run with the least energy molecule until a new one is found, terminating it (default = %(default)s)",
)

arg_parser.add_argument(
    "--comparison_algorithm",
    default = "mixed",
    type = str,
    help = """Algorithm to be used for structures comparison, the recomendes usage is:
\t- \"grigoryan_springborn\" for clusters;
\t- \"haas_oliveira\" for organic and general shaped structures (check --comparison_bonding_tolerance too);
\t- \"mixed\" for both at the same time (sqrt(grigoryan_springborg * haas_oliveira);
(default = %(default)s)""",
)

arg_parser.add_argument(
    "--comparison_bonding_tolerance",
    default = 0.25,
    type = float,
    help = "Distance tolerable so two atoms can be considered bonded within the haas_oliveira molecule comparison algorithm",
)

arg_parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
)

args = arg_parser.parse_args()
print(f"Args: {args}")

actual_cwd = os.getcwd()
os.chdir(
    "/".join(__file__.split("/")[:-1])
)

from phaast.calculators.xtb import XTB
from phaast.computer import Computer
from phaast.structure import Base, Molecule
from phaast.surface_explorator.genetic.migration.filter_list import FilterList, FilterMode
from phaast.surface_explorator.genetic import Genetic
from phaast.structure.geometry import grigoryan_springborn, haas_oliveira

base = Base(args.stoichiometry)

calc = XTB(
    charge = args.charge,
    threads = args.xtb_threads,
    xtb_path = args.xtb_path,
)

computer = Computer(
    cpu_count_limit = args.threads,
)

computer.add_calculator("xtb", calc)

start = time.monotonic_ns()

filter_list = FilterList(FilterMode.EXCLUDE, ((1,1),))

migrator = cast(
    list,
    [
        (
            args.migr_w,
            HedronMigrator(base, 20, filter_list, None),
        ),
    ],
)

mutators = [
    (
        args.mut_dist_w,
        DisplacementMutator(
            base,
            args.mut_disp_num,
            args.mut_disp_min,
            args.mut_disp_max,
            None,
        ),
    ),
    (
        args.mut_perm_w,
        PermuteMutator(
            base,
            args.mut_perm_num,
            None,
        )
    ),
    (
        args.mut_twist_w,
        TwistMutator(
            args.mut_twist_min_angle,
            args.mut_twist_max_angle,
            None,
        )
    ),
]

crossover = cast(
    list,
    [
        (
            args.crov_w,
            PlaneMating(None),
        ),
    ],
)

def haas_oliveira_comparator(mol1 : Molecule, mol2 : Molecule) -> float:
    return haas_oliveira(mol1, mol2, bonding_tolerance = args.comparison_bonding_tolerance)

def mixed_comparator(mol1 : Molecule, mol2 : Molecule) -> float:
    return (haas_oliveira_comparator(mol1, mol2) * grigoryan_springborn(mol1, mol2))**.5


match args.comparison_algorithm:
    case "haas_oliveira":
        comparison_algorithm = haas_oliveira_comparator
    case "grigoryan_springborn":
        comparison_algorithm = grigoryan_springborn
    case "mixed":
        comparison_algorithm = mixed_comparator
    case _:
        raise ValueError(
            f"Incompatible comparison_algorithm: {args.comparison_algorithm}"
        )
        

genetic = Genetic(
    base = base,
    population_size = args.population_size,
    computer = computer,
    calculator = "xtb",

    mutations = mutators,
    crossovers = crossover,
    migrators = migrator,

    energy_threshold = args.energy_threshold,
    geometry_threshold = args.geometry_threshold,
    comparison_algorithm = comparison_algorithm,

    end_loop_number = args.end_loop_number,
)

while genetic.loop():
    print(f"========================================")
    print(f"Generation {genetic.cycle_counter} done")
    print(f"Best energy is {genetic.best_energy}")
    print(f"========================================")

end = time.monotonic_ns()
delta_time = (end - start)/1e9

best = sorted(
    genetic.population,
    key = lambda mol: mol.energy,
)

best_list = best[0 : min(len(best), args.return_number)]

print(f"The process is done. Elapsed time: {round(delta_time)} s")
print(f"Total optimizations: {genetic.total_optimizations}")
print(f"Total converged: {genetic.total_converged}")

os.chdir(actual_cwd)

for i, mol in enumerate(best_list):
    mol.to_xyz(f"{args.output_prefix}{i}.xyz")
