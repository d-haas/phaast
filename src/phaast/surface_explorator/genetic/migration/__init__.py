from abc import ABC, abstractmethod

from phaast.structure import Structure
from phaast.structure.constants import *
from phaast.surface_explorator.genetic.migration.hedron_universe import HedronMigrator

#@check_types

class Migrator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def __call__(self) -> Structure:
        pass

HedronMigrator = HedronMigrator
