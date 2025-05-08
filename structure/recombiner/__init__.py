from bisect import insort
import random
from vec import Vector

from structure import Atom, Structure

def plane_mating(struct1 : Structure, struct2 : Structure, rand_gen : random.Random | None = None) -> Structure:
    assert struct1.is_equal_to(struct2), "Structures are not compatible"

    rng : random.Random = rand_gen if rand_gen else random.Random()

    plane_ortho_vec : Vector = Vector(
        *[rng.random()-.5 for _ in range(3)],
    ).normalized()
    inv_plane_ortho_vec : Vector = -plane_ortho_vec

    ##########################################################
    ### Get distances of atoms from the plane and order it ###
    ##########################################################

    # For structure 1
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

