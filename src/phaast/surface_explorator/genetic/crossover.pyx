from abc import abstractmethod
import random
from bisect import insort

from phaast.vector cimport Vector
from phaast.utils.c_random cimport get_rand, get_randint, get_rand_uniform
from phaast.structure.primitives cimport Atom, Structure

cdef class Crossover:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __call__(self, struct_a : Structure, struct_b : Structure) -> Structure:
        pass

    def as_data(self) -> dict:
        pass

cdef class PlaneMating:

    def __init__(self):
        pass

    def __call__(self, struct1 : Structure, struct2 : Structure) -> Structure:
        return self.ccall(struct1, struct2)

    # I chose not to optimize this function further
    cdef Structure ccall(self, Structure struct1, Structure struct2):
        """
        Make a in-between structure from two other structures

        This method creates a random plane centered in the center
        of mass of each structure and get most of the atoms "above"
        for structure 1 and "below" for structure 2, still preserving
        the stoichiometry
        """

        # Ensure both structures have the same stoichiometry
        assert struct1.is_equal_to(struct2), "Structures are not compatible"

        # Create a normalized vector in a random direction to represent
        # the normal vector to the plane
        cdef Vector plane_ortho_vec = Vector(
            get_rand_uniform(-1, 1),
            get_rand_uniform(-1, 1),
            get_rand_uniform(-1, 1),
        ).normalized()
        # Invert the vector to create the same plane with opposite
        # normal for the other structure
        cdef Vector inv_plane_ortho_vec = -1.0 * plane_ortho_vec

        ##########################################################
        ### Get distances of atoms from the plane and order it ###
        ##########################################################

        # For structure 1
        # Order atoms by distance to the plane, giving positive
        # values if they are above the plane and negative otherwise
        struct1_atom_dist_pairs : list[tuple[Atom, float]] = []
        struct1.center_mass()
        for atom in struct1:
            dist = atom.pos*plane_ortho_vec
            insort(
                struct1_atom_dist_pairs,
                (atom, dist),
                key = lambda pair : pair[1],
            )

        # And structure 2
        # Same for structure 1 but with above and below inverted
        struct2_atom_dist_pairs : list[tuple[Atom, float]] = []
        struct2.center_mass()
        for atom in struct2:
            dist = atom.pos*inv_plane_ortho_vec
            insort(
                struct2_atom_dist_pairs,
                (atom, dist),
                key = lambda pair : pair[1],
            )

        # Get dict of number of atoms per element
        atom_count = struct1.element_count()

        # List atoms to be inherited by the "child"
        inherited_atoms : list[Atom] = []

        # Iterate over atoms from both parents alternating
        for pair_1, pair_2 in zip(struct1_atom_dist_pairs, struct2_atom_dist_pairs):
            # For each atom, test if it can be added to the child
            # and add it if possible, subtracting it to the remaining
            # atoms to be added
            for pair in (pair_1, pair_2):
                atom = pair[0]
                if atom_count[atom.z] > 0:
                    inherited_atoms.append(
                        atom.copy()
                    )
                    atom_count[atom.z]-= 1

        new_structure = Structure(inherited_atoms)

        new_structure.center_mass()

        return new_structure


    def as_data(self) -> dict:
        return {
            "name" : "Plane Cross-over",
            "import" : "phaast.surface_explorator.genetic.crossover.PlaneMating",
            "args" : (),
            "kwargs" : {},
        }
