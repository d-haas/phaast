from abc import ABC, abstractmethod
from math import tau
import random
from typing import cast

from phaast.structure import Base, Element, Structure
from phaast.vec import Vector

from phaast.utils.custom_iter import distinct_pairs

class Mutator(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def __call__(self, struct : Structure) -> Structure:
        pass

class DisplacementMutator(Mutator):
    num : int
    min_displacement : float
    max_displacement : float
    rng : random.Random

    def __init__(
        self,
        base : Base,
        num : int = 1,
        min_displacement : float = 0.7,
        max_displacement : float = 2.3,
        rng : None | random.Random = None,
    ):
        if len(base) < num:
            raise ValueError(
                "Number of displacements is higher than number of atoms in structure"
            )

        self.num = num

        self.min_displacement = min_displacement
        self.max_displacement = max_displacement

        if isinstance(rng, random.Random):
            self.rng = rng
        else:
            self.rng = random.Random()


    def __call__(self, structure : Structure) -> Structure:
        new_structure : Structure = structure.copy()

        # Divide them by the sum so they sum 1 now

        for atom_index in self.rng.sample(range(len(new_structure)), self.num):
            displacement = Vector(
                *[
                    (self.rng.uniform(-1, 1))
                    for _ in range(3)
                ]
            ).normalized() 

            new_structure[atom_index].pos+= displacement * self.rng.uniform(self.min_displacement, self.max_displacement)

        return new_structure

class PermuteMutator(Mutator):
    num : int
    rng : random.Random

    def __init__(self, base : Base, num : int, rng : None | random.Random):
        all_permutations = cast(
            list[tuple[Element,Element]],
            list(distinct_pairs(tuple(base))),
        )

        valid_permutations = sum([
            1 for perm in all_permutations
            if perm[0] != perm[1]
        ])

        if valid_permutations < num:
            raise ValueError(
                "Number of needed permutations is higher than available"
            )

        self.num = num

        if isinstance(rng, random.Random):
            self.rng = rng
        else:
            self.rng = random.Random()


    def __call__(self, structure : Structure) -> Structure:
        """
        Permute atoms in a structure at random
        supposedly generating a new structure
        """

        new_structure = structure.copy()

        valid_permutations = [
            atoms for atoms
            in distinct_pairs(tuple(new_structure))
            if atoms[0].z != atoms[1].z
        ]

        # Choosing N permutations at "random"
        chosen_permutations = self.rng.sample(valid_permutations, k=self.num)

        # Swapping atom positions
        for atom_i, atom_j in chosen_permutations:
            atom_i.pos, atom_j.pos = atom_j.pos, atom_i.pos

        return new_structure

class TwistMutator(Mutator):
    min_angle : float
    max_angle : float
    rng : random.Random

    def __init__(
        self,
        min_angle : float,
        max_angle : float,
        rng : None | random.Random,
    ):
        if min_angle > tau:
            min_angle%= tau
        if max_angle > tau:
            max_angle%= tau

        self.min_angle = min_angle
        self.max_angle = max_angle

        if isinstance(rng, random.Random):
            self.rng = rng
        else:
            self.rng = random.Random()

    def __call__(self, structure : Structure) -> Structure:

        new_structure : Structure = structure.copy()

        cm : Vector = new_structure.cm

        for atom in new_structure:
            atom.pos-= cm

        rotations : tuple[float, float] = (
            self.rng.uniform(0, tau),
            self.rng.uniform(0, tau),
        )

        for atom in new_structure:
            atom.pos.rotate_x(rotations[0])
            atom.pos.rotate_y(rotations[1])

            if atom.pos.z > 0:
                atom.pos.rotate_z(
                    self.rng.choice((-1,1),)*self.rng.uniform(self.min_angle, self.max_angle)
                )

            atom.pos.rotate_y(-rotations[1])
            atom.pos.rotate_x(-rotations[0])

        return new_structure
