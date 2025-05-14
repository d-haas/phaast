
from abc import ABC, abstractmethod


class SurfaceExplorator(ABC):
    @abstractmethod
    def loop(self):
        pass

    @abstractmethod
    def save(self, file : str):
        pass
