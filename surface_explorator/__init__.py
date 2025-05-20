
from abc import ABC, abstractmethod


class SurfaceExplorator(ABC):
    @abstractmethod
    def loop(self) -> None:
        pass

    @abstractmethod
    def save(self, file : str) -> None:
        pass
