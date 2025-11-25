from typing import Callable

from computer import Computer
from structure import Molecule
from surface_explorator.genetic.individual import Individual

import sys
if sys._is_gil_enabled():
    from multiprocessing import Pool
else:
    from multiprocessing.dummy import Pool

def is_pop_index_duplicate(
    population : list[Individual],
    i : int,
    energy_threshold : float,
    geometry_threshold : float,
    comparison_algorithm : Callable[[Molecule, Molecule], float],
) -> bool:

    for j in range(i+1, len(population)):
        # Compare energies
        if abs(population[i].energy-population[j].energy) <= energy_threshold:
            # Then compare geometries
            if comparison_algorithm(population[i], population[j]) > geometry_threshold:
                return True

    return False

def remove_duplicates(
    computer : Computer,
    population : list[Individual],
    energy_threshold : float,
    geometry_threshold : float,
    comparison_algorithm : Callable[[Molecule, Molecule], float],
) -> list[Individual]:
    with Pool(computer.cpu_count_limit) as pool:
        remove_mask : list[bool]  = pool.starmap(
            is_pop_index_duplicate,
            [
                (
                    population,
                    i,
                    energy_threshold,
                    geometry_threshold,
                    comparison_algorithm,
                )
                for i in range(len(population))
            ],
        )

    return [
        ind for ind, is_duplicate
        in zip(population, remove_mask)
        if not is_duplicate
    ]
