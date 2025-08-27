from threading import Thread
from calculators.xtb import XTB
from structure import Base, Structure
from structure.creator.filter_list import FilterList, FilterMode
from surface_explorator.genetic import *
import structure.creator as creator

def run():
    def subplot(struct : Structure):
        Thread(target = lambda : struct.plot()).start()

    base = Base("C6H6")
    filter = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
    )

    calculator = XTB(charge = 2)
    
    computer = Computer()

    computer.add_calculator("xtb", calculator)

    structs = creator.generate_random_structures_hedron(
        base,
        15,
        computer,
        20,
        seed = 20,
        filter_list = filter,
    )

    mols = computer.optimize("xtb", structs)

    for mol in mols:
        if mol.is_bonded(bonding_tolerance=0.25):
            subplot(mol)

    input("Press enter to show the non-bonded...")
    for mol in mols:
        if not mol.is_bonded(bonding_tolerance=0.25):
            subplot(mol)
