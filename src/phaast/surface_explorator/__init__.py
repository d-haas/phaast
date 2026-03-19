
from abc import ABC, abstractmethod
from typing import Self


class SurfaceExplorator(ABC):
    @abstractmethod
    def loop(self) -> bool: ...

    @abstractmethod
    def save(self, file_path : str) -> None: ...

    @classmethod
    @abstractmethod
    def load(cls, file_path : str) -> Self: ...
