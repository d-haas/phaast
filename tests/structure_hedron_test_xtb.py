import time, sys
from tabulate import tabulate #type: ignore
from calculators.xtb import XTB
from computer import Computer
from structure.creator.filter_list import FilterList, FilterMode
from structure import Base, Molecule, Structure
import structure.creator
import itertools

def run():
    base = Base("C6H6")
    Structures_numbers : tuple[int, ...] = (10000,)
    Processes_numbers : tuple[int, ...] = (8,)

    calc = XTB(
        charge = 2,
        threads = 1,
    )

    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
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


    time_data : list[tuple[str, int, int, int, int, float, float]] = []

    converged : list[Molecule] = []
    print(f"Have we got GIL? {'Yes' if sys._is_gil_enabled() else 'No'}!!")
    for p_num, struct_num in itertools.product(Processes_numbers, Structures_numbers):

        start = time.perf_counter_ns()

        total_population = 0

        converged = []

        for i in range(100):
            population = structure.creator.generate_random_structures_hedron(
                base,
                struct_num//100,
                computer,
                20,
                2345678,
                filter_list = filter_list,
            )
            total_population+= len(population)

            converged+= computer.optimize("xtb", population)
            print(f"Done batch {i+1}/200")

        end = time.perf_counter_ns()
        total_s = (end - start)/1e9
        per_struct_ms = ((end - start)/1e6)/struct_num
        time_data.append(
            (
                "Hedron",
                p_num,
                struct_num,
                total_population,
                len(converged),
                round(total_s, 2),
                round(per_struct_ms, 2),
            )
        )

    print(
        tabulate(
            time_data,
            tablefmt = "github",
            floatfmt = ".2f",
            headers = [
                "Generator",
                "Threads",
                "Structures",
                "Generated number",
                "Converged number",
                "Total time (s)",
                "Time per structure (ms)",
            ],
        )
    )


    """
    for i in reversed(range(len(converged))):
        for j in reversed(range(i+1, len(converged))):
            if converged[i].compare_geometry(converged[j]) > 0.9:
                del converged[j]
    """
    for i in reversed(range(len(converged))):
        if converged[i].compare_geometry(benzene_dication) < 0.9:
            del converged[i]

    best = sorted(
        converged,
        key = lambda mol : mol.energy,
    )
    for i in best[0:min(10,len(best))]:
        i.plot()
