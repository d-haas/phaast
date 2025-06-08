import time, sys
from tabulate import tabulate #type: ignore
from structure import Base
import structure.creator
import itertools

def run():
    base = Base("C4H6")
    Structures_numbers : tuple[int, ...] = (128,)
    Processes_numbers : tuple[int, ...] = (8,)
    Cell_sizes : tuple[float, ...] = (0.2, 0.15)


    time_data : list[tuple[int, int, float, float, float]] = []

    print(f"Have we got GIL? {'Yes' if sys._is_gil_enabled() else 'No'}!!")
    for p_num, struct_num, cell_size in itertools.product(Processes_numbers, Structures_numbers, Cell_sizes):

        start = time.perf_counter_ns()

        _ = structure.creator.generate_random_structures(
            base,
            struct_num,
            p_num,
            cell_size,
            2345678,
        )

        end = time.perf_counter_ns()
        total_s = (end - start)/1e9
        per_struct_ms = ((end - start)/1e6)/struct_num
        time_data.append(
            (
                p_num,
                struct_num,
                cell_size,
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
                "Threads",
                "Structures",
                "Cell size (Å)",
                "Total time (s)",
                "Time per structure (ms)",
            ],
        )
    )

