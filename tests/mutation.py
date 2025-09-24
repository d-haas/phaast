from threading import Thread
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

    struct_a = creator.generate_random_structure_hedron(
        base,
        20,
        filter_list = filter,
    )

    mut_a = mut_random(struct_a, 1, 2.0)

    subplot(struct_a)
    subplot(mut_a)



