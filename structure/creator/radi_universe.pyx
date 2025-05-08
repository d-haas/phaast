import cython
from cython cimport boundscheck, wraparound
from cython.parallel cimport prange
from libc.string cimport memset
from libc.stdlib cimport malloc, free

import random

from structure.constants import AtomicRadi

from structure cimport Atom

from vec cimport Vector

import itertools

cdef struct CAtom:
    unsigned int z
    double rx, ry, rz

cdef class RadiUniverse:
    """
    A base class to define the cell-separated universe
    used to place and model each element of the population
    """
    cdef public double dot_distance
    cdef public unsigned int[3] dot_num
    cdef CAtom *atom_population
    cdef public unsigned int atom_number
    cdef public unsigned int placed_atoms

    def __init__(
        self,
        dot_distance : cython.double,
        dot_num : int | tuple[int, int, int],
        atom_number : int,
    ):

        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot_num

        self.dot_distance = dot_distance
        self.dot_num = universe_size

        self.atom_population = <CAtom*>malloc(atom_number * sizeof(CAtom))

        if self.atom_population is NULL:
            raise MemoryError("Failed to allocate memory for atom population")

        self.atom_number = atom_number
        self.placed_atoms = 0

    def __dealloc__(self):
        # Free all allocated atoms

        cdef unsigned int i

        if self.atom_population is not NULL:
            free(self.atom_population)
    """

Error compiling Cython file:
------------------------------------------------------------
...
    A base class to define the cell-separated universe
    used to place and model each element of the population
    cdef public double dot_distance
    cdef public unsigned int[3] dot_num
    cdef Atom* atom_population
             ^
------------------------------------------------------------

structure/creator/radi_universe.pyx:24:13: Pointer base type cannot be a Python object

Error compiling Cython file:
------------------------------------------------------------
...
        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot
_num

        self.dot_distance = dot_distance
        self.dot_num = universe_size

        self.atom_population = <Atom*>malloc(atom_number * sizeof(Atom))
                                    ^
------------------------------------------------------------

structure/creator/radi_universe.pyx:40:36: Pointer base type cannot be a Python object

Error compiling Cython file:
------------------------------------------------------------
...
        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot
_num

        self.dot_distance = dot_distance
        self.dot_num = universe_size

        self.atom_population = <Atom*>malloc(atom_number * sizeof(Atom))
                                      ^
------------------------------------------------------------

structure/creator/radi_universe.pyx:40:38: undeclared name not builtin: malloc

Error compiling Cython file:
------------------------------------------------------------
...
        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot
_num

        self.dot_distance = dot_distance
        self.dot_num = universe_size

        self.atom_population = <Atom*>malloc(atom_number * sizeof(Atom))
                               ^
------------------------------------------------------------

structure/creator/radi_universe.pyx:40:31: Casting temporary Python object to non-numeri
c non-Python type

Error compiling Cython file:
------------------------------------------------------------
...
        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot
_num

        self.dot_distance = dot_distance
        self.dot_num = universe_size

        self.atom_population = <Atom*>malloc(atom_number * sizeof(Atom))
                               ^
------------------------------------------------------------

structure/creator/radi_universe.pyx:40:31: Python objects cannot be cast to pointers of 
primitive types

Error compiling Cython file:
------------------------------------------------------------
...
        universe_size = (dot_num, dot_num, dot_num) if isinstance(dot_num, int) else dot
_num

        self.dot_distance = dot_distance
        self.dot_num = universe_size

        self.atom_population = <Atom*>malloc(atom_number * sizeof(Atom))
                               ^
------------------------------------------------------------

structure/creator/radi_universe.pyx:40:31: Storing unsafe C derivative of temporary Pyth
on reference
    """

    cdef int check_available_position(self, cell_pos_x, cell_pos_y, cell_pos_z, unsigned int atomic_number):
        cdef int result
        cdef Vector pos_vec = Vector.create(
            cell_pos_x,
            cell_pos_y,
            cell_pos_z,
        ).cmul(self.dot_distance)

        if self.atom_population:
            for atom in self.atom_population:
                dist_vec= atom.pos - pos_vec
                dist_squared = dist_vec.squared_mod
                radius_sum_squared : float = (AtomicRadi[atom.z] + AtomicRadi[atomic_number])**2
                if dist_squared < radius_sum_squared:
                    # Atom would be "inside the delimited field of bonding"
                    return 0
                elif dist_squared < radius_sum_squared + self.dot_distance:
                    # Atom is in "ideal distance for bonding"
                    result = 1
        else:
            return 1

        return result

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def get_available_positions(self, atomic_number : int) -> list[int]:
        cdef int[:] positions = <int*>malloc(total_positions * sizeof(int))
        cdef unsigned int pos
        cdef atoms 

        for pos in prange(self.dot_num[0]*self.dot_num[1]*self.dot_num[2], nogil=True):
            i = (pos // self.dot_num[1]) // self.dot_num[2]
            j = (pos %  self.dot_num[0]) // self.dot_num[2]
            k = (pos %  self.dot_num[0]) %  self.dot_num[1]

            if check_available_position(i, j, k, atomic_number):
                positions[pos] = 1


    @cython.boundscheck(False)
    @cython.wraparound(False)
    def get_random_available_position(self, atomic_number : int, rand_gen : None | random.Random = None) -> tuple[int, int, int] | None:
        cdef double loop_counter = 1
        cdef int[3] result = (-1,-1,-1)
        cdef int chosen_pos = -1
        cdef double rand = 0
        cdef int i, j, k
        cdef int[:] positions
        rng = rand_gen if rand_gen else random.Random()

        if self.atom_population:
            positions = <int*>malloc(total_positions * sizeof(int))
            for i, pos in enumerate(positions):
                if pos:
                    rand = rng.random() if rng else random.random()
                    if rand<=(1/loop_counter):
                        loop_counter+= 1.0
                        chosen_pos = i

            if chosen_pos >= 0:
                return (
                    (chosen_pos // self.dot_num[1]) // self.dot_num[2],
                    (chosen_pos %  self.dot_num[0]) // self.dot_num[2],
                    (chosen_pos %  self.dot_num[0]) %  self.dot_num[1],
                )
            else:
                return None
        else:
            return (
                self.dot_num[0]//2,
                self.dot_num[1]//2,
                self.dot_num[2]//2,
            )




    """
    def include_atom(self, cell_pos : tuple[int, int, int], atom : Atom) -> None:
        atom.pos = Vector(*cell_pos) * self.dot_distance
        if self.atom_number:
        self.atom_population.append(atom)
