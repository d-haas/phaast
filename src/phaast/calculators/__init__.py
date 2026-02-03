from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phaast.structure import Molecule, Structure

from abc import ABC, abstractmethod



class Calculator(ABC):
    @abstractmethod
    def optimize(self, structure : Structure) -> Molecule | None:...

    @abstractmethod
    def __hash__(self) -> int:...
