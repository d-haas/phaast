import itertools
from computer import Computer
from structure import Base
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
        memory_limit = 0,
        calculators = [calc],
        structure_type = base,
    )

    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
    )

    seed = None #2345678

    struct_nums = (5000, 10000, 15000, 20000)
    geometry_thresholds = (0.5, 0.6, 0.7, 0.8, 0.9)
    children_mutant_ratios = (0.0, 0.5, 1.0, 2.0, 100000.0)


    for struct_num, geometry_threshold, children_mutant_ratio in itertools.product(
        struct_nums,
        geometry_thresholds,
        children_mutant_ratios
    ):
        structs = structure.creator.generate_random_structures_hedron(
            base,
            struct_num,
            computer,
            seed,
            filter_list,
        )

        genetic = Genetic(
            structures = structs,
            computer = computer,
            energy_threshold = 1.0,
            geometry_threshold = geometry_threshold,
            children_mutant_ratio = children_mutant_ratio,
            calculator = calc,
        )

        best = sorted(
            genetic.population,
            key = lambda mol: mol.energy,
        )

        best_list = list(
            enumerate(
                best[0 : min(len(best), 50)],
            ),
        )

        for i, mol in best_list:
            mol.to_xyz(f"out_STRUCT{struct_num}_GEOMETRY{geometry_threshold}_CMRATIO{children_mutant_ratio} - {i}.xyz")
