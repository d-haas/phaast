from calculators.xtb import XTB
from computer import Computer
from structure.creator.filter_list import FilterList, FilterMode
from structure import Base
import structure.creator

def run():
    calc = XTB(
        charge = 2,
        threads = 1,
    )

    filter_list = FilterList(
        FilterMode.EXCLUDE,
        ((1,1),),
    )

    computer = Computer()

    computer.add_calculator("xtb", calc)

    population = structure.creator.generate_random_structures_hedron(
        Base("C6H6"),
        10,
        computer,
        20,
        filter_list = filter_list,
    )

    converged = computer.optimize("xtb", population)

    for i in converged:
        i.plot()
