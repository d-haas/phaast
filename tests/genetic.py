from computer import Computer
from structure import Atom, Structure
import structure.creator
from calculators.xtb import XTB

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

    seed = 2345678
    structs = structure.creator.generate_random_structures(
        base,
        100,
        4,
        0.15,
        seed,
    )

    computer = Computer(
        cpu_count_limit = 0,
        memory_limit = 0,
        calculators = [XTB],
        structure_type = base,
    )

    genetic = Genetic(
        structures = structs,
        computer = computer,
        energy_threshold = 0.02,
        geometry_threshold = 0.3,
        children_mutant_ratio = 0.5,
    )

    while genetic.loop():
        print(f"Cycle {genetic.cycle_counter}!!")

    best = sorted(
        genetic.population,
        key = lambda mol: mol.energy,
    )[0:10]

    for mol in best:
        mol.plot()
    


    
