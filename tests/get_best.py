from structure import Atom, Structure
import structure.creator
from vec import Vector
from calculators.xtb import XTB
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
from multiprocessing.dummy import Pool

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

    structs = structure.creator.generate_random_structures(
        base,
        10,
        4,
        0.15,
        None,
    )

    molecules = sorted(
        [
            XTB.optimize(struct)
            for struct in structs
        ],
        key = lambda mol : mol.energy,
    )

    with Pool(10) as p:
        p.map(
            Structure.plot,
            [
                molecules[i]
                for i in range(10)
            ],
        )

