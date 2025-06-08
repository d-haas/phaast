from structure import Atom, Base, Structure
import structure.creator
from calculators.xtb import XTB
from multiprocessing.dummy import Pool

def run():
    computer = Computer()

    base = Base(
        "C6H6",
        charge = 2,
    )

    structs = structure.creator.generate_random_structures(
        base,
        10,
        4,
        0.15,
        None,
    )

    molecules = [
        XTB.optimize(struct)
        for struct in structs
    ]
    molecules = [mol for mol in molecules if mol]

    with Pool() as p:
        p.map(
            Structure.plot,
            [
                molecules[i]
                for i in range(10)
            ],
        )

