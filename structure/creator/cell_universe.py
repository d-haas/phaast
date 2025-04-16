
from typing import Iterable

import vector


class RadiUniverse(list[list[list[bool]]]): #Fuck speed, I want readability (list for the win) [but will need the speed later]
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    def __init__(
        self,
        dot_distance : float,
        dot_num : int | tuple[int, int, int],
    ):

        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot_num

        super().__init__([
            [
                [
                    False
                    for _ in range(universe_size[2])
                ]
                for _ in range(universe_size[1])
            ] 
            for _ in range(universe_size[0])
        ])

        self.dot_distance = dot_distance
        self.dot_num = universe_size

    def apply_spheres(self, pos : Iterable[vector.VectorObject3D], radius : float) -> None:
