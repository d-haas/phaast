from typing import Optional, Sequence
from structure import Atom, Base, Structure
import multiprocessing, random
from multiprocessing.dummy import Pool

from structure.constants import *
from structure.creator.dot_universe import DotUniverse
from structure.creator.filter_list import FilterList



#@check_types
def generate_random_structures(
    base: Base,
    N: int,
    p_num: int = 0,
    cell_size: float = 0.1,
    seed: int | None = None,
    filter_list: Optional[FilterList] = None,
) -> Sequence[Structure]:
    """
    Generate N random structures with the atoms in the base
    Use seed as parameter for future reproducibility
    (same seed with same base and N structures will result in the same initial set)
    """
    # Validade thread number used
    if p_num == 0:
        p_num = multiprocessing.cpu_count()
    elif p_num < 0:
        raise ValueError(
            f"Number of processes selected ({p_num}) is not a valid number, using 1 instead"
        )

    # Set new RNG based on a predetermined seed or not
    main_rng: random.Random = random.Random() if seed is None else random.Random(seed)

    # Create a list of seeds from the rng to be used by each structure generation process
    single_seeds: list[int] = main_rng.sample(range(0, 2 * N), N)

    if p_num == 1:
        # Execute sequentially if there's only one process
        structures = [
            generate_random_structure(base, cell_size, single_seeds[0], filter_list)
            for _ in range(N)
        ]
    else:
        # Use poll of N processes to accelerate structure creation
        with Pool(p_num) as p:
            structures = p.starmap(
                generate_random_structure,
                [(base, cell_size, s) for s in single_seeds],
            )

    return structures


def generate_random_structure(
    base: Base,
    cell_size: float = 0.1,
    seed: int | None = None,
    filter_list: Optional[FilterList] = None,
) -> Structure:
    """
    Generate a random structure with atoms in the base
    Use seed as parameter for future reproducibility
    (same seed with the same base will result in the same structure)
    """

    # Get random generator
    rng = random.Random(seed)

    atoms = [Atom(element.z) for element in base.elements]
    rng.shuffle(atoms)

    universe = DotUniverse(
        cell_size,
        max((atom.radius for atom in atoms)),
        filter_list,
    )

    for atom in atoms:
        random_available_position = universe.get_random_available_position(atom.z, rng)
        if random_available_position:
            universe.include_atom(random_available_position, atom)

    return Structure(atoms, charge = base.charge)
