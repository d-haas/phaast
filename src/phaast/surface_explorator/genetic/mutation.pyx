# cython: freethreading_compatible = True
from abc import abstractmethod
from math import tau
import random
from typing import cast

from libc.math cimport sqrt
cimport cython
from cython.view cimport array as cvarray
from phaast.vector cimport Vec, Vector
from phaast.structure.primitives cimport Element, Structure
from phaast.utils.c_random cimport get_rand, get_randint, get_rand_uniform

from cython.parallel import prange

from phaast.structure import Base
from phaast.vector import Vector
from phaast.utils.custom_iter import distinct_pairs


cdef class Mutator:
    #@abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    #@abstractmethod
    def __call__(self, struct : Structure) -> Structure:
        pass

    def as_date(self) -> dict:
        pass

cdef class DisplacementMutator(Mutator):
    num : cython.uint
    min_displacement : cython.double
    max_displacement : cython.double

    def __init__(
        self,
        num : cython.uint = 1,
        min_displacement : cython.double = 0.7,
        max_displacement : cython.double = 3.0,
    ):
        self.num = num
        self.min_displacement = min_displacement
        self.max_displacement = max_displacement


    def __call__(self, structure : Structure) -> Structure:
        return self.ccall(Structure(structure))

    @cython.boundscheck(False)
    cdef Structure ccall(self, Structure structure):
        cdef Structure new_structure = structure.copy()

        cdef unsigned int i
        cdef double min_displacement = self.min_displacement
        cdef double max_displacement = self.max_displacement
        cdef unsigned int num
        if self.num > 0:
            num = self.num
        else:
            num = len(new_structure)

        cdef unsigned int length = random.randint(1, num) #len(new_structure)
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

        for i, atom_id  in enumerate(
            random.sample(
                range(len(new_structure)),
                k = length,
            )
        ): #range(length):
            new_structure.atoms[atom_id].pos.x+= rand_displacements[i].x
            new_structure.atoms[atom_id].pos.y+= rand_displacements[i].y
            new_structure.atoms[atom_id].pos.z+= rand_displacements[i].z

        new_structure.center_mass()

        return new_structure

    def as_data(self) -> dict:
        return {
            "name"             : "Displacement Mutation",
            "num_displacement" : self.num,
            "min_displacement" : self.min_displacement,
            "max_displacement" : self.max_displacement,
            "import_path"      : "phaast.surface_explorator.genetic.mutation.DisplacementMutator",
            "args"             : (self.num, self.min_displacement, self.max_displacement),
            "kwargs"           : {},
        }


cdef class PermuteMutator(Mutator):
    num : int

    def __init__(self, num : int):
        self.num = num

    def __call__(self, structure : Structure) -> Structure:
        return self.ccall(Structure(structure))

    @cython.boundscheck(False)
    cdef Structure ccall(self, Structure structure):
        """
        Permute atoms in a structure at random
        supposedly generating a new structure
        """

        cdef Structure new_structure = structure.copy()
        cdef int length = len(structure)
        cdef int num = self.num

        cdef int valid_permutations
        cdef int i, j, _

        for _ in range(num):
            valid_permutations = 0
            i = get_randint(0, length-1)
            for j in range(length):
                if new_structure[i] != new_structure[j]:
                    valid_permutations+= 1

            for j in range(length):
                if new_structure[i] != new_structure[j]:
                    valid_permutations-= 1
                    if valid_permutations == 0:
                        new_structure[i].pos, new_structure[j].pos = new_structure[j].pos, new_structure[i].pos

        new_structure.center_mass()

        return new_structure

    def as_data(self) -> dict:
        return {
            "name"             : "Permutation Mutation",
            "num_permutations" : self.num,
            "import_path"      : "phaast.surface_explorator.genetic.mutation.PermuteMutator",
            "args"             : (self.num,),
            "kwargs"           : {},
        }

cdef class TwistMutator(Mutator):
    min_angle : float
    max_angle : float

    def __init__(
        self,
        min_angle : float,
        max_angle : float,
    ):
        if min_angle > tau:
            min_angle%= tau
        if max_angle > tau:
            max_angle%= tau

        self.min_angle = min_angle
        self.max_angle = max_angle


    def __call__(self, structure : Structure) -> Structure:
        return self.ccall(Structure(structure))

    @cython.boundscheck(False)
    cdef Structure ccall(self, Structure structure):

        cdef Structure new_structure = structure.copy()
        cdef double min_angle = self.min_angle
        cdef double max_angle = self.max_angle

        new_structure.center_mass()

        rotations : tuple[float, float] = (
            get_rand_uniform(0, tau),
            get_rand_uniform(0, tau),
        )

        cdef double rotation_angle = get_rand_uniform(min_angle, max_angle)

        for atom in new_structure:
            atom.pos.rotate_x(rotations[0])
            atom.pos.rotate_y(rotations[1])

            if atom.pos.z > 0:
                atom.pos.rotate_z(rotation_angle)

            atom.pos.rotate_y(-rotations[1])
            atom.pos.rotate_x(-rotations[0])

        new_structure.center_mass()

        return new_structure

    def as_data(self) -> dict:
        return {
            "name"      : "Twist Mutation",
            "min_angle" : self.min_angle,
            "max_angle" : self.max_angle,
            "import_path" : "phaast.surface_explorator.genetic.mutation.TwistMutator",
            "args"        : (self.min_angle, self.max_angle,),
            "kwargs"      : {},
        }
