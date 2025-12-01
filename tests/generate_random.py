import random
from phaast.calculators.xtb import XTB
from phaast.computer import Computer
from phaast.structure import Base
from phaast.surface_explorator.genetic import GeneticComputer
from phaast.surface_explorator.genetic.individual import Individual
from phaast.surface_explorator.genetic.migration.filter_list import FilterList, FilterMode
from phaast.surface_explorator.genetic.migration.hedron_universe import HedronMigrator

comp = Computer(8)
comp_gen = GeneticComputer(comp)

comp_gen.add_calculator(
    "xtb",
    XTB(xtb_path="/opt/xtb-dist/bin/xtb"),
)

migrator = HedronMigrator(
    Base("C6H6"),
    20,
    FilterList(FilterMode.EXCLUDE, ()),
    random.Random(),
)


pop = comp_gen.optimize("xtb", comp_gen.migrate(10, migrator))

for mol in pop:
    print(type(Individual(mol)))
