import itertools
import time

from tabulate import tabulate
from computer import Computer
from structure import Base
from calculators.xtb import XTB

from surface_explorator.genetic import Genetic

def run():
    base = Base(
        "C6H6",
    )

    calc = XTB(
        charge = 2,
        threads = 1,
        xtb_path = "/home/main/Coding/Python/Phaast/calculators/xtb/xtb-dist/bin/xtb",
    )

    computer = Computer(
        cpu_count_limit = 0,
        #memory_limit = 0,
        #calculators = [calc],
        #structure_type = base,
    )

    computer.add_calculator("xtb", calc)

    """
    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
    )
    """

    #seed = 2345678

    #struct_nums = (5000, 10000, 15000, 20000)
    #geometry_thresholds = (0.5, 0.6, 0.7, 0.8, 0.9)
    #children_mutant_ratios = (0.0, 0.5, 1.0, 2.0, 100000.0)
    struct_nums = (10000, 15000, 20000)
    cpu_nums = (4, 8, 16)
    geometry_threshold = 0.9

    table_columns : list[str] = [
        "Struct num",
        "Cpu num",
        "Creation time (s)",
        "Duplicate removal time (s)",
    ]

    table_rows : list[tuple[float,...]] = []

    for struct_num, cpu_num in itertools.product(
        struct_nums,
        cpu_nums,
    ):
        computer.cpu_count_limit = cpu_num

        start = time.monotonic_ns()
        genetic = Genetic(
            base = base,
            population_size = struct_num,
            computer = computer,
            energy_threshold = 1.0,
            geometry_threshold = geometry_threshold,
            calculator = "xtb",
        )
        end = time.monotonic_ns()
        creation_time = (end - start)/1e9

        start = time.monotonic_ns()
        genetic.remove_duplicates()
        end = time.monotonic_ns()
        duplicate_removal_time = (end - start)/1e9



        table_rows.append(
            (
                struct_num,
                cpu_num,
                creation_time,
                duplicate_removal_time,
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
