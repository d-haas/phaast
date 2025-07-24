import time, sys
from tabulate import tabulate #type: ignore
from calculators.xtb import XTB
from computer import Computer
from structure.creator.filter_list import FilterList, FilterMode
from structure import Base, Molecule
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

    computer = Computer(
        cpu_count_limit = 0,
        memory_limit = 0,
        calculators = [calc],
        structure_type = base,
    )

    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
    )


    time_data : list[tuple[str, int, int, int, int, float, float]] = []

    converged : list[Molecule] = []
    print(f"Have we got GIL? {'Yes' if sys._is_gil_enabled() else 'No'}!!")
    for p_num, struct_num in itertools.product(Processes_numbers, Structures_numbers):

        start = time.perf_counter_ns()

        population = structure.creator.generate_random_structures_hedron(
            base,
            10000,
            computer,
            2345678,
        )

        converged = computer.optimize(calc, population)

        end = time.perf_counter_ns()
        total_s = (end - start)/1e9
        per_struct_ms = ((end - start)/1e6)/struct_num
        time_data.append(
            (
                "Hedron",
                p_num,
                struct_num,
                len(population),
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

    best = sorted(
        converged,
        key = lambda mol : mol.energy,
    )
    for i in best[0:min(10,len(best))]:
        i.plot()
