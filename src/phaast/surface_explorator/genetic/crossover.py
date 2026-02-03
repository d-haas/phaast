from abc import ABC, abstractmethod
import random
from bisect import insort

from phaast.structure import Atom, Structure
from phaast.vector import Vector

class Crossover(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def __call__(self, struct_a : Structure, struct_b : Structure) -> Structure:
        pass

class PlaneMating(ABC):
    rng : random.Random

    def __init__(self, rng : None | random.Random = None):
        if isinstance(rng, random.Random):
            self.rng = rng
        else:
            self.rng = random.Random()

    def __call__(self, struct1 : Structure, struct2 : Structure) -> Structure:
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
        plane_ortho_vec : Vector = Vector(
            *[self.rng.uniform(-1, 1) for _ in range(3)],
        ).normalized()
        # Invert the vector to create the same plane with opposite
        # normal for the other structure
        inv_plane_ortho_vec : Vector = -plane_ortho_vec

        ##########################################################
        ### Get distances of atoms from the plane and order it ###
        ##########################################################

        # For structure 1
        # Order atoms by distance to the plane, giving positive
        # values if they are above the plane and negative otherwise
        struct1_atom_dist_pairs : list[tuple[Atom, float]] = []
        cm1 = struct1.cm # Structure 1 center of mass
        for atom in struct1:
            dist = (atom.pos-cm1)*plane_ortho_vec
            insort(
                struct1_atom_dist_pairs,
                (atom, dist),
                key = lambda pair : pair[1],
            )

        # And structure 2
        # Same for structure 1 but with above and below inverted
        struct2_atom_dist_pairs : list[tuple[Atom, float]] = []
        cm2 = struct2.cm # Structure 2 center of mass
        for atom in struct2:
            dist = (atom.pos-cm2)*inv_plane_ortho_vec
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

        return Structure(inherited_atoms)


