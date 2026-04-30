import argparse
import time

from phaast.structure.comparator import BondingLength, ChargeComparator, ComparisonSequence, EnergyDifference, GrigoryanSpringborg
from phaast.structure.primitives import Molecule
from phaast.surface_explorator.genetic.crossover import PlaneMating
from phaast.surface_explorator.genetic.migration.hedron_universe import HedronMigrator
from phaast.surface_explorator.genetic.mutation import DisplacementMutator, PermuteMutator, TwistMutator

def main():
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

    """
    arg_parser.add_argument(
        "output_prefix",
        help = "Prefix of the output files (a prefix of \"OUTPUT\" will result in files named OUTPUT0, OUTPUT1, ...)",
    )
    """

    arg_parser.add_argument(
        "--return-number",
        type = int,
        default = 100,
        help = "Number of least energy molecules to return at the end of the algorithm (default = %(default)s)",
    )

    arg_parser.add_argument(
        "-pop",
        "--population-size",
        type = int,
        default = 500,
        help = "Number of molecules in the population (default = %(default)s)",
    )

    arg_parser.add_argument(
        "-best-num",
        type = int,
        default = 10,
        help = "Number of unchanged minima to consider algorithm termination (default = %(default)s)",
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
        default = 4,
        help = "Number of threads to be used by each -t xtb instance (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--xtb-path",
        type = str,
        default = "xtb",
        help = "Path to be used for the xtb binary (default = %(default)s)",
    )

    arg_parser.add_argument(
        "-et",
        "--energy-threshold",
        type = float,
        default = 1e-3,
        help = "Maximum energy difference [in hartree] so molecules are considered alike (default = %(default)s)",
    )

    arg_parser.add_argument(
        "-gt",
        "--geometry-threshold",
        type = float,
        default = 0.85,
        help = "Maximum geometry difference so molecules are considered the same so one of them is discarded [must be a value between 0 and 1] (default = %(default)s)",
    )

    arg_parser.add_argument(
        "-ct",
        "--charge-threshold",
        type = float,
        default = 0.95,
        help = "Maximum partial charge difference so molecules are considered the same so one of them is discarded [must be a value between 0 and 1] (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-disp-w",
        type = float,
        default = 3,
        help = "Mutation displacement weight (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-perm-w",
        type = float,
        default = 2,
        help = "Mutation permutation weight (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-twist-w",
        type = float,
        default = 1,
        help = "Mutation twist weight (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--crov-w",
        type = float,
        default = 1,
        help = "Crossing-over weight (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--migr-w",
        type = float,
        default = 1,
        help = "Migrator weight (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-disp-min",
        type = float,
        default = 1.3,
        help = "Minimum distance (Å) to be used in mutation of atomic displacement (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-disp-max",
        type = float,
        default = 2.3,
        help = "Maximum distance (Å) to be used in mutation of atomic displacement (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-disp-num",
        type = int,
        default = 1,
        help = "Number of atoms to move in mutations of atomic displacement (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-perm-num",
        type = int,
        default = 0,
        help = "Number of permutations in mutations of that type (default = Half the number of atoms)",
    )

    arg_parser.add_argument(
        "--mut-twist-min-angle",
        type = float,
        default = 90,
        help = "Minimum angle to be used in twist mutations (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--mut-twist-max-angle",
        type = float,
        default = 270,
        help = "Maximum angle to be used in twist mutations (default = %(default)s)",
    )

    arg_parser.add_argument(
        "-loops",
        "--end-loop-number",
        default = 11,
        type = int,
        help = "Number of loops the algorithm will run with the least energy molecule until a new one is found, terminating it (default = %(default)s)",
    )

    arg_parser.add_argument(
        "--comparison-algorithm",
        default = "grigoryan-springborg",
        type = str,
        help = """Algorithm to be used for structures comparison, the recomendes usage is:
    \t- \"grigoryan-springborg\" for clusters;
    \t- \"bonding-length\" for organic and general shaped structures (check --comparison-bonding-tolerance too);
    (default = %(default)s)""",
    )

    arg_parser.add_argument(
        "--comparison-bonding-tolerance",
        default = 0.25,
        type = float,
        help = "Distance tolerable so two atoms can be considered bonded within the bonding-length molecule comparison algorithm",
    )

    arg_parser.add_argument(
        "--remove-unbonded",
        default = "always",
        help = """Choose to not remove unbonded structures from genetic algorithm population
    \t- \"always\": Remove unbonded in every loop;
    \t- \"final\": Remove only from final population to not contaminate results;
    \t- \"never\": Do not remove unbonded;
    (default = %(default)s)""",
    )

    arg_parser.add_argument(
        "--benchmark-structure",
        default = "",
        type = str,
        help = """Input Molecule (xyz with energy) to be used at the end to determine if the benchmark was successfull of not""",
    )

    arg_parser.add_argument(
        "--benchmark-num",
        default = 100,
        type = int,
        help = """Number of benchmarks to run to define a result"""
    )

    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )

    args = arg_parser.parse_args()

    from phaast.calculators.xtb import XTB
    from phaast.computer import Computer
    from phaast.structure import Base
    from phaast.surface_explorator.genetic.migration.filter_list import FilterList, FilterMode
    from phaast.surface_explorator.genetic import Genetic

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


    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),)
    )

    migrator = [
        (
            args.migr_w,
            HedronMigrator(base, 20, filter_list),
        ),
    ]

    mutators = [
        (
            args.mut_disp_w,
            DisplacementMutator(
                args.mut_disp_num,
                args.mut_disp_min,
                args.mut_disp_max,
            ),
        ),
        (
            args.mut_perm_w,
            PermuteMutator(
                args.mut_perm_num,
            )
        ),
        (
            args.mut_twist_w,
            TwistMutator(
                args.mut_twist_min_angle,
                args.mut_twist_max_angle,
            )
        ),
    ]

    crossover = [
        (
            args.crov_w,
            PlaneMating(),
        ),
    ]

    grigoryan_springborg = GrigoryanSpringborg(args.geometry_threshold)
    bonding_length_comparator = BondingLength(args.geometry_threshold, bonding_tolerance = args.comparison_bonding_tolerance)


    match args.comparison_algorithm:
        case "bonding-length":
            comparison_algorithm = ComparisonSequence(
                EnergyDifference(args.energy_threshold),
                ChargeComparator(args.charge_threshold),
                bonding_length_comparator,
            )
        case "grigoryan-springborg":
            comparison_algorithm = ComparisonSequence(
                EnergyDifference(args.energy_threshold),
                ChargeComparator(args.charge_threshold),
                grigoryan_springborg,
            )
        case _:
            raise ValueError(
                f"Incompatible comparison_algorithm: {args.comparison_algorithm}"
            )

    assert args.remove_unbonded in ("always", "final", "never"), "Wrong remove_unbonded option"
    if args.remove_unbonded == "always":
        do_remove_unbonded = True
    else:
        do_remove_unbonded = False

    def new_genetic() -> Genetic:
        return Genetic(
            population_size = args.population_size,
            computer = computer,
            calculator = "xtb",

            mutations = mutators,
            crossovers = crossover, #type: ignore
            migrators = migrator, #type: ignore

            comparison_algorithm = comparison_algorithm,

            do_remove_unbonded = do_remove_unbonded,

            end_loop_number = args.end_loop_number,

            best_energy_num = args.best_num,
        )

    def run_genetic(
        save_name = "phaast_genetic",
        report_name = "phaast_report",
        output_name = "OUTPUT_PHAAST_",
    ):
        start = time.monotonic_ns()
        genetic = new_genetic()

        while genetic.loop():
            print(genetic.status())

            genetic.save(f"{save_name}_temp")
            genetic.save(save_name)

        end = time.monotonic_ns()
        delta_time = (end - start)/1e9

        if args.remove_unbonded == "final":
            genetic.remove_unbonded()

        best = sorted(
            genetic.population,
            key = lambda mol: mol.energy,
        )

        best_list = best[0 : min(len(best), args.return_number)]

        print(
            genetic.statistics(
                [f"The process is done. Elapsed time: {round(delta_time)} s"]
            ),
        )

        max_num_len = len(str( len(best_list)-1 ))
        for i, mol in enumerate(best_list):
            out_num = str(i).rjust(max_num_len, "0")
            mol.to_xyz(f"{output_name}{out_num}.xyz")

        genetic.save(save_name)
        genetic.save_report(report_name)

        return genetic

    if args.benchmark_structure:
        benchmark_mol = Molecule.from_xyz(args.benchmark_structure)
        max_num_len = len(str( args.benchmark_num-1 ))
        accumulated_success = 0
        for i in range(args.benchmark_num):
            out_num = str(i).rjust(max_num_len, "0")
            genetic = run_genetic(
                save_name = f"phaast_genetic_benchmark_{out_num}",
                report_name = f"phaast_report_{out_num}",
                output_name = f"OUTPUT_PHAAST_{out_num}_",
            )
            best = sorted(
                genetic.population,
                key = lambda mol: mol.energy,
            )
            best_list = best[0 : min(len(best), args.return_number)]
            best_found = []
            for j, mol in enumerate(best_list):
                if comparison_algorithm(mol, benchmark_mol):
                    best_found.append(j)

            if best_found:
                accumulated_success+= 1

            print("╔"+"═"*57+"╗")
            print("║"+" "*57+"║")
            print("║"+f"Benchmark status: {accumulated_success}/{i+1} ({"%.2f" % (100*accumulated_success/(i+1))} %)".ljust(57)+"║")
            print("║"+" "*57+"║")
            print("╚"+"═"*57+"╝")


    else:
        run_genetic()

if __name__ == "__main__":
    main()
