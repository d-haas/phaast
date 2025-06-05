from computer import Computer
from structure import Atom, Structure
import structure.creator
from calculators.xtb import XTB

from structure.creator.filter_list import FilterList, FilterMode
from surface_explorator.genetic import Genetic

def run():
    base = Structure(
        [
            Atom(6),
            Atom(6),
            Atom(6),
            Atom(6),
            Atom(6),
            Atom(6),
            Atom(1),
            Atom(1),
            Atom(1),
            Atom(1),
            Atom(1),
            Atom(1),
        ],
        charge = 2,
    )

    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
    )

    seed = None #2345678
    structs = structure.creator.generate_random_structures(
        base,
        1000,
        4,
        0.15,
        seed,
        filter_list,
    )

    computer = Computer(
        cpu_count_limit = 8,
        memory_limit = 0,
        calculators = [XTB],
        structure_type = base,
    )

    genetic = Genetic(
        structures = structs,
        computer = computer,
        energy_threshold = 1.0,
        geometry_threshold = 0.87,
        children_mutant_ratio = 1.0,
    )

    while genetic.loop():
        print(f"Cycle {genetic.cycle_counter}!!")

    best = sorted(
        genetic.population,
        key = lambda mol: mol.energy,
    )

    for mol in best[0:min(len(best),10)]:
        mol.plot()
    


    
