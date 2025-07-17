import time, sys
from tabulate import tabulate #type: ignore
from calculators.xtb import XTB
from computer import Computer
from structure.creator.filter_list import FilterList, FilterMode
from structure import Base
import structure.creator
import itertools

def run():
    base = Base("C6H6")
    Structures_numbers : tuple[int, ...] = (64,)
    Processes_numbers : tuple[int, ...] = (8,)

    calc = XTB(
        charge = 2,
        threads = 4,
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


    time_data : list[tuple[str, int, int, float, float]] = []

    print(f"Have we got GIL? {'Yes' if sys._is_gil_enabled() else 'No'}!!")
    for p_num, struct_num in itertools.product(Processes_numbers, Structures_numbers):

        start = time.perf_counter_ns()

        population = structure.creator.generate_random_structures_hedron(
            base,
            struct_num,
            computer,
            2345678,
        )

        computer.optimize(calc, population)

        end = time.perf_counter_ns()
        total_s = (end - start)/1e9
        per_struct_ms = ((end - start)/1e6)/struct_num
        time_data.append(
            (
                "Hedron",
                p_num,
                struct_num,
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
                "Cell size (Å)",
                "Total time (s)",
                "Time per structure (ms)",
            ],
        )
    )

