from typing import Optional, Sequence
from computer import Computer
from structure import Atom, Base, Structure
import random
import sys

if sys._is_gil_enabled():
    from multiprocessing import Pool
else:
    from multiprocessing.dummy import Pool

from structure.constants import *
from structure.creator.dot_universe import DotUniverse
from structure.creator.filter_list import FilterList
from structure.creator.hedron_universe import HedronNumber, HedronUniverse

#@check_types
def generate_random_structures_mesh(
    base: Base,
    N: int,
    computer : Computer,
    cell_size: float = 0.1,
    seed: int | None = None,
    filter_list: Optional[FilterList] = None,
) -> Sequence[Structure]:
    """
    Generate N random structures with the atoms in the base
    Use seed as parameter for future reproducibility
    (same seed with same base and N structures will result in the same initial set)
    """

    # Set new RNG based on a predetermined seed or not
    main_rng: random.Random = random.Random() if seed is None else random.Random(seed)

    # Create a list of seeds from the rng to be used by each structure generation process
    single_seeds: list[int] = main_rng.sample(range(0, 2 * N), N)

    # Use poll of N processes to accelerate structure creation
    with Pool(computer.cpu_count_limit) as p:
        structures = p.starmap(
            generate_random_structure,
            [(base, cell_size, s, filter_list) for s in single_seeds],
        )

    return structures


def generate_random_structure_mesh(
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

    # Create list of atoms based on stoichiometry
    atoms = [Atom(element.z) for element in base.elements]
    # Randomly shuffle it
    rng.shuffle(atoms)

    # Create dot universe
    universe = DotUniverse(
        cell_size,
        max((atom.radius for atom in atoms)),
        filter_list,
    )

    while atoms:
        # Get first atom and remove it from the list
        atom = atoms.pop(0)

        # Get random position to put the atom
        random_available_position = universe.get_random_available_position(atom.z, rng)
        
        # Put it in the universe if there are positions available
        if random_available_position:
            universe.include_atom(random_available_position, atom)
        # Else, put it in the end of the list
        else:
            atoms.append(atom)
            

    # Return structure of atoms in the universe
    return Structure(atoms)

def generate_random_structure_hedron(
    base: Base,
    n_vertices: HedronNumber = 4,
    seed: int | None = None,
    filter_list: Optional[FilterList] = None,
) -> Structure:

    # Get random generator
    rng = random.Random(seed)

    atoms = [Atom(element.z) for element in base.elements]
    rng.shuffle(atoms)

    universe = HedronUniverse(
        n_vertices = n_vertices,
        filter_list = filter_list,
    )

    while atoms:
        atom = atoms.pop(0)
        random_available_position = universe.get_random_available_position(atom.z, rng)
        if random_available_position is not None:
            random_available_position, hedron_scale = random_available_position
            universe.include_atom(random_available_position, atom, hedron_scale)
        else:
            atoms.append(atom)
            
    return Structure([element[0] for element in universe.atom_population])

def generate_random_structures_hedron(
    base: Base,
    N: int,
    computer : Computer,
    n_vertices: HedronNumber = 4,
    seed: int | None = None,
    filter_list: Optional[FilterList] = None,
) -> Sequence[Structure]:

    main_rng: random.Random = random.Random() if seed is None else random.Random(seed)

    # Create a list of seeds from the rng to be used by each structure generation process
    single_seeds: list[int] = main_rng.sample(range(0, 2 * N), N)

    # Use poll of N processes to accelerate structure creation
    with Pool(computer.cpu_count_limit) as p:
        structures = p.starmap(
            generate_random_structure_hedron,
            [(base, n_vertices, s, filter_list) for s in single_seeds],
        )

    return structures

generate_random_structure = generate_random_structure_mesh
generate_random_structures = generate_random_structures_mesh
