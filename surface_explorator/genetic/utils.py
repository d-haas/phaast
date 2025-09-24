import random
from typing import Optional, cast
from bisect import insort


from structure import Atom, Structure
from vec import Vector

from utils.custom_iter import distinct_pairs

def plane_mating(struct1 : Structure, struct2 : Structure, rand_gen : random.Random | None = None) -> Structure:
    """
    Make a in-between structure from two other structures

    This method creates a random plane centered in the center
    of mass of each structure and get most of the atoms "above"
    for structure 1 and "below" for structure 2, still preserving
    the stoichiometry
    """

    # Ensure both structures have the same stoichiometry
    assert struct1.is_equal_to(struct2), "Structures are not compatible"

    # Create a new random number generator, if it wasn't given
    rng : random.Random = rand_gen if rand_gen else random.Random()

    # Create a normalized vector in a random direction to represent
    # the normal vector to the plane
    plane_ortho_vec : Vector = Vector(
        *[rng.random()-.5 for _ in range(3)],
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


def imut_random(structure : Structure, n : int = 1, max_displacement : float = 1.0, rng : None | random.Random = None) -> None:
    if not rng:
        rng = random.Random()

    # Generate list of random numbers
    displacement_distribution : list[float] = [rng.random() for _ in range(n)]

    # Get sum of generated numbers
    displacement_distribution_sum : float = sum(displacement_distribution)

    # Divide them by the sum so they sum 1 now
    displacement_distribution = [
        num / displacement_distribution_sum
        for num in displacement_distribution
    ]

    for atom_index, displacement_weight in zip(
        rng.sample(range(len(structure)), n),
        displacement_distribution,
    ):
        displacement = Vector(
            *[
                (rng.random()-0.5)
                for _ in range(3)
            ]
        ).normalized() 

        structure[atom_index].pos+= displacement * displacement_weight * max_displacement

def mut_random(structure : Structure, n : int = 1, max_displacement : float = 0.1, rng : Optional[random.Random] = None) -> Structure:
    new_structure : Structure = structure.copy()

    imut_random(new_structure, n, max_displacement, rng)

    return new_structure

def imut_permute(structure : Structure, num_permutations : int | None = None, rng : random.Random | None = None) -> None:
    """
    Permute atoms in a structure at random
    supposedly generating a new structure
    """

    all_permutations = cast(
        list[tuple[Atom,Atom]],
        list(distinct_pairs(tuple(structure))),
    )
    max_permutations = (len(structure)**2 - len(structure))/2

    # Checking if number of permutations is a valid number
    if not isinstance(num_permutations, int):
        num_permutations = len(structure)-2

    elif num_permutations > max_permutations:
        raise ValueError(
            f"Requested {num_permutations} permutations, but maximum possible is {max_permutations}"
        )

    # Choosing N permutations at "random"
    if rng:
        chosen_permutations = rng.sample(all_permutations, k=num_permutations)
    else:
        chosen_permutations = random.sample(all_permutations, k=num_permutations)

    # Swapping atom positions
    for atom_i, atom_j in chosen_permutations:
        atom_i.pos, atom_j.pos = atom_j.pos, atom_i.pos

def mut_permute(structure : Structure, num_permutations : int | None = None, rng : random.Random | None = None) -> Structure:
    new_structure = structure.copy()

    imut_permute(new_structure, num_permutations, rng)

    return new_structure
