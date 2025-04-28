import random
import more_itertools
from typing import Optional, Iterator, cast

from structure import Structure, Atom

def imut_random(structure : Structure, max_displacement : float = 0.1, rng : None | random.Random = None) -> None:
    for atom in structure:
        if rng:
            displacement = [
                (rng.random()-0.5)*2*max_displacement
                for _ in range(3)
            ]
        else:
            displacement = [
                (random.random()-0.5)*2*max_displacement
                for _ in range(3)
            ]

        atom.pos+= displacement

def mut_random(structure : Structure, max_displacement : float = 0.1, rng : Optional[random.Random] = None) -> Structure:
    new_structure : Structure = structure.copy()

    imut_random(new_structure, max_displacement, rng)

    return new_structure

def imut_permute(structure : Structure, num_permutations : int | None = None, rng : random.Random | None = None) -> None:
    """
    Permute atoms in a structure at random
    supposedly generating a new structure
    """

    all_permutations = cast(
        list[tuple[Atom,Atom]],
        list(more_itertools.distinct_permutations(structure, 2)),
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
