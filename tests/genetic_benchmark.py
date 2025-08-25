import itertools
import time

from tabulate import tabulate
import statistics
from computer import Computer
from structure import Base, Molecule, Structure
import structure.creator
from calculators.xtb import XTB

from structure.creator.filter_list import FilterList, FilterMode
from surface_explorator.genetic import Genetic

def run():
    base = Base(
        "C6H6",
    )

    calc = XTB(
        charge = 2,
        threads = 1,
    )

    computer = Computer(
        cpu_count_limit = 0,
        #memory_limit = 0,
        #calculators = [calc],
        #structure_type = base,
    )

    computer.add_calculator("xtb", calc)

    benzene_dication : Molecule = computer.optimize(
        "xtb",
        [
            Structure.from_xyz_str(
                """12

                H 0.57031558944458 -0.71512482887087 -0.61947322560183
                C -0.28841000604806 -1.23148746314092 -1.04925180490272
                C -1.48648695461343 -0.72593434211214 -2.0710739731313
                C -1.61716607853925 -1.24638116400561 -0.50674454647007
                H -1.93997917964386 -0.7436649702442 0.40535796322691
                H -1.69086799098777 0.23141130657192 -2.54478182823585
                C -0.32605787441742 -1.87408245290782 -2.33267757044084
                C -2.47627280579508 -1.89794146092667 -1.45487886424629
                C -1.67806510594839 -2.28657092331682 -2.58294062576861
                H 0.49915794477982 -1.92893781891371 -3.04325393057159
                H -3.56160137383557 -1.97433095513516 -1.38441412115668
                H -2.05456616439559 -2.706954926998 -3.51586747270114"""
            )
        ]
    )[0]

    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
    )

    seed = None #2345678

    #struct_nums = (5000, 10000, 15000, 20000)
    #geometry_thresholds = (0.5, 0.6, 0.7, 0.8, 0.9)
    #children_mutant_ratios = (0.0, 0.5, 1.0, 2.0, 100000.0)
    struct_nums = (10000, 15000, 20000)
    geometry_threshold = 0.9
    children_mutant_ratios = (0.0, 0.5, 1.0, 2.0, 100000.0)

    table_columns : list[str] = [
        "Struct num",
        "Geometry threshold",
        "Child-to-mut ratio",
        "Execution time (s)",
        "Std dev (time)",
        f"Success rate ({geometry_threshold})",
    ]

    table_rows : list[tuple[float,...]] = []

    for struct_num, children_mutant_ratio in itertools.product(
        struct_nums,
        children_mutant_ratios
    ):
        successes = 0
        times = []
        for _ in range(10):
            start = time.monotonic_ns()
            structs = structure.creator.generate_random_structures_hedron(
                base,
                struct_num,
                computer,
                20,
                seed,
                filter_list,
            )

            genetic = Genetic(
                structures = structs,
                computer = computer,
                energy_threshold = 1.0,
                geometry_threshold = geometry_threshold,
                children_mutant_ratio = children_mutant_ratio,
                calculator = "xtb",
            )
            end = time.monotonic_ns()
            delta_time = end - start/1e9
            times.append(delta_time)

            best = sorted(
                genetic.population,
                key = lambda mol: mol.energy,
            )

            best_list = best[0 : min(len(best), 50)]

            for mol in best_list:
                if benzene_dication.compare_geometry(mol) >= geometry_threshold:
                    successes+= 1

        table_rows.append(
            (
                struct_num,
                geometry_threshold,
                children_mutant_ratio,
                statistics.mean(times),
                statistics.stdev(times),
                successes,
            )
        )
        print(
            tabulate(
                table_rows,
                tablefmt = "github",
                floatfmt = ".2f",
                headers = table_columns,
            )
        )
