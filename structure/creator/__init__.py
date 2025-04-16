from typing import Generator, Iterable
from structure import Atom, Structure
import random
import numpy as np

from structure.creator.cell_universe import RadiUniverse


def generate_random_structures(base : Iterable[Atom], N : int, seed : int | None = None) -> Generator[Structure]:
    """
    Generate N random structures with the atoms in the base
    Use seed as parameter for future reproducibility
    (same seed with same base and N structures will result in the same initial set)
    """
    main_rng : random.Random = random.Random() if seed is None else random.Random(seed)

    single_seeds : list[int] = main_rng.sample(range(0, 2*N), N) 

    for single_seed in single_seeds:
        yield generate_random_structure(base, single_seed)


def generate_random_structure(base : Iterable[Atom], seed : int) -> Structure:
    """
    Generate a random structure with atoms in the base
    Use seed as parameter for future reproducibility
    (same seed with the same base will result in the same structure)
    """
    rng = random.Random(seed)
    shuffled_base = rng.shuffle([atom for atom in base])
    universe = RadiUniverse(0.1, sum(()))

    for atom in shuffled_base:
        pass

