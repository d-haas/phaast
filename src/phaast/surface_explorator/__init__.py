
from abc import ABC, abstractmethod


class SurfaceExplorator(ABC):
    @abstractmethod
    def loop(self) -> bool:
        pass

    @abstractmethod
    def save(self, file : str) -> None:
        pass
