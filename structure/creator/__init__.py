from typing import Generator, Iterable
from structure import Atom, Structure
import random

from structure.creator.radi_universe import RadiUniverse
from structure.constants import AtomicRadi
from vec import Vector

def generate_random_structures(base : Iterable[Atom], N : int, seed : int | None = None) -> Generator[Structure]:
    """
    Generate N random structures with the atoms in the base
    Use seed as parameter for future reproducibility
    (same seed with same base and N structures will result in the same initial set)
    """
    main_rng : random.Random = random.Random() if seed is None else random.Random(seed)

    single_seeds : list[int] = main_rng.sample(range(0, 2*N), N) 

    for single_seed in single_seeds:
        yield generate_random_structure(
            [Atom(atom.z, Vector()) for atom in base],
            single_seed,
        )


def generate_random_structure(base : Iterable[Atom], seed : int | None = None) -> Structure:
    """
    Generate a random structure with atoms in the base
    Use seed as parameter for future reproducibility
    (same seed with the same base will result in the same structure)
    """
    rng = random.Random(seed)

    copied_base = [atom.copy() for atom in base]
    rng.shuffle(copied_base)

    universe = RadiUniverse(
        0.1, # Need to be edited later
        int(
            sum(
                [AtomicRadi[atom.z] for atom in copied_base]
            )/0.1
        ),
    )

    for atom in copied_base:
        random_available_position = universe.get_random_available_position(atom.z, rng)
        print(random_available_position)
        if random_available_position:
            universe.include_atom(random_available_position, atom)

    return Structure(copied_base)
