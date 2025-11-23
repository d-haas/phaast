from abc import ABC, abstractmethod
from structure import Structure

from structure.constants import *
from surface_explorator.genetic.migration.hedron_universe import HedronMigrator

#@check_types

class Migrator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def __call__(self) -> Structure:
        pass

HedronMigrator = HedronMigrator
