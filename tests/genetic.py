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

    seed = None #2345678

    structs = structure.creator.generate_random_structures(
        base,
        2000,
        computer,
        0.15,
        seed,
        filter_list,
    )

    genetic = Genetic(
        structures = structs,
        computer = computer,
        energy_threshold = 1.0,
        geometry_threshold = 0.88,
        children_mutant_ratio = 1.0,
        calculator = calc,
    )

    print("Starting cycles")
    while genetic.loop():
        print(f"Cycle {genetic.cycle_counter}!!")

    best = sorted(
        genetic.population,
        key = lambda mol: mol.energy,
    )
    best_list = list(enumerate(best[0:min(len(best),10)]))

    for i, mol in best_list:
        print(f"Got molecule {i} with energy {mol.energy}")
        if i<len(best_list)-1:
            print(f"\tSimilarity with next is {mol.compare_geometry(best_list[i+1][1])}")

        mol.to_xyz(f"out_{i}.xyz")
