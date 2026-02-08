from abc import abstractmethod
from math import tau
import random
from typing import cast

from libc.stdlib cimport rand, srand, RAND_MAX
from libc.time cimport time
from libc.math cimport sqrt
cimport cython
from cython.view cimport array as cvarray
from phaast.vector cimport Vec, Vector
from phaast.structure.primitives cimport Element, Structure

from cython.parallel import prange

from phaast.structure import Base
from phaast.vector import Vector
from phaast.utils.custom_iter import distinct_pairs

srand(time(NULL))

cdef double get_rand() nogil:
    cdef unsigned long num = rand()

    cdef double result = (num * 1.0) / RAND_MAX

    return result

cdef double get_rand_uniform(double a, double b) nogil:
    return get_rand()*(b - a) + a 

cdef class Mutator:
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def __call__(self, struct : Structure) -> Structure:
        pass

cdef class DisplacementMutator(Mutator):
    num : cython.uint
    min_displacement : cython.double
    max_displacement : cython.double

    def __init__(
        self,
        num : cython.uint = 1,
        min_displacement : cython.double = 0.7,
        max_displacement : cython.double = 2.3,
    ):
        self.num = num

        self.min_displacement = min_displacement
        self.max_displacement = max_displacement


    def __call__(self, structure : Structure) -> Structure:
        return self.ccall(structure)

    @cython.boundscheck(False)
    cdef Structure ccall(self, Structure structure):
        cdef Structure new_structure = structure.copy()

        cdef unsigned int i
        cdef double min_displacement = self.min_displacement
        cdef double max_displacement = self.max_displacement
        cdef unsigned int length = len(new_structure)
        cdef Vec[:] rand_vecs = cvarray(shape=(length,), itemsize=sizeof(Vec), format="ddd")
        cdef Vec[:] rand_displacements = cvarray(shape=(length,), itemsize=sizeof(Vec), format="ddd")
        cdef double[:] rand_vec_mods = cvarray(shape=(length,), itemsize=sizeof(double), format="d")
        cdef double[:] rand_distances = cvarray(shape=(length,), itemsize=sizeof(double), format="d")

        # Add random position to it
        for i in prange(length, nogil=True):
            rand_vecs[i].x = get_rand()
            rand_vecs[i].y = get_rand()
            rand_vecs[i].z = get_rand()
            rand_vec_mods[i] = sqrt(rand_vecs[i].x*rand_vecs[i].x + rand_vecs[i].y*rand_vecs[i].y + rand_vecs[i].z*rand_vecs[i].z)
            rand_distances[i] = get_rand_uniform(min_displacement, max_displacement)

            rand_displacements[i].x = rand_distances[i]*rand_vecs[i].x/rand_vec_mods[i]
            rand_displacements[i].y = rand_distances[i]*rand_vecs[i].y/rand_vec_mods[i]
            rand_displacements[i].z = rand_distances[i]*rand_vecs[i].z/rand_vec_mods[i]

        for i in range(length):
            new_structure.atoms[i].pos.x+= rand_displacements[i].x
            new_structure.atoms[i].pos.y+= rand_displacements[i].y
            new_structure.atoms[i].pos.z+= rand_displacements[i].z

        return new_structure


cdef class PermuteMutator(Mutator):
    num : int

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

cdef class TwistMutator(Mutator):
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
