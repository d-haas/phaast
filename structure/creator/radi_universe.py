import random
from structure import Atom
from constants import AtomicRadi

import itertools
import numpy as np

class RadiUniverse(list[list[list[int]]]): #Fuck speed, I want readability (list for the win) [but will need the speed later]
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    dot_distance : float
    dot_num : tuple[int, int, int]
    atom_population : list[Atom]

    def __init__(
        self,
        dot_distance : float,
        dot_num : int | tuple[int, int, int],
    ):

        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot_num

        super().__init__([[[0]*universe_size[2]]*universe_size[1]]*universe_size[0])

        self.dot_distance = dot_distance
        self.dot_num = universe_size
        self.atom_population : list[Atom] = []

    def check_available_position(self, cell_pos : tuple[int, int, int], atomic_number : int) -> bool:
        result : bool = False
        pos_vec = np.array(cell_pos, dtype=np.float64)

        for atom in self.atom_population:
            distance_vec = cell_pos - pos_vec
            distance_squared = distance_vec.dot(distance_vec)
            radius_sum : float = AtomicRadi[atom.z] + AtomicRadi[atomic_number]
            if distance_squared < radius_sum:
                # Atom would be "inside the delimited field of bonding"
                return False
            elif distance_squared < radius_sum + self.dot_distance:
                # Atom is in "ideal distance for bonding"
                result = True

        return result

    def get_random_available_position(self, atomic_number : int, rng : None | random.Random = None) -> tuple[int, int, int] | None:
        loop_counter = 1
        result : tuple[int, int, int] | None = None

        iterators : tuple[range, range, range] = (
            range(self.dot_num[0]),
            range(self.dot_num[1]),
            range(self.dot_num[2]),
        )

        for position in itertools.product(*iterators):
            if self.check_available_position(position, atomic_number):
                rand : float = rng.random() if rng else random.random()
                if rand>=1/loop_counter:
                    loop_counter+= 1
                    result = position

        return result



    def include_atom(self, cell_pos : tuple[int, int, int], atom : Atom) -> None:
        atom.pos = np.array(cell_pos, dtype=np.float64)
        self.atom_population.append(atom)

