import random
import sys
from typing import Callable, Optional, Sequence, cast
from math import floor
from bisect import insort

if sys._is_gil_enabled():
    from multiprocessing import Pool
else:
    from multiprocessing.dummy import Pool

from computer import Computer
from structure import Atom, Base, Molecule, Structure
from structure.creator import generate_random_structures_hedron
from vec import Vector

from surface_explorator import SurfaceExplorator
from utils.typecheck import check_types
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


def imut_random(structure : Structure, max_displacement : float = 1.0, rng : None | random.Random = None) -> None:
    if rng:
        displacement = Vector(
            *[
                (rng.random()-0.5)
                for _ in range(3)
            ]
        ).normalized() * max_displacement
        atom = rng.choice(structure)
    else:
        displacement = Vector(
            *[
                (random.random()-0.5)
                for _ in range(3)
            ]
        ).normalized() * max_displacement
        atom = random.choice(structure)

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

class Genetic(SurfaceExplorator):
    population_size : int
    population : list[Molecule]
    end_loop_number : int

    calculator : str
    computer : Computer
    structure_generator : Callable[[Base, int, Computer], Sequence[Structure]]
    base : Base

    energy_threshold : float
    geometry_threshold : float

    generation_children_mutant_proportion : tuple[float, float, float]
    children_mutant_proportion : tuple[float, float]
    mut_displacement_permutation_proportion : tuple[float, float]

    mut_displacement_number : int
    mut_displacement_max : float
    mut_permutation_num : int

    cycle_counter : int
    best_energy : float
    best_energy_loops : int

    def __init__(
        self,
        base : Base,
        population_size : int,
        computer : Computer,
        energy_threshold : float,
        geometry_threshold : float,
        calculator : str,

        structure_generator : Callable[[Base, int, Computer], Sequence[Structure]] = lambda base, n, comp : generate_random_structures_hedron(base, n, comp, 20),

        generation_children_mutant_proportion : tuple[float, float, float] = (1.0, 1.0, 1.0),
        mut_displacement_permutation_proportion : tuple[float, float] = (1.0, 1.0),

        mut_displacement_number : int = 1,
        mut_displacement_max : float = 1.0,
        mut_permutation_num : int = 0,

        end_loop_number : int = 9,
    ):
        self.computer = computer
        self.calculator = calculator
        if population_size < 100:
            raise ValueError(
                "Population size is too small",
            )
        self.base = base
        self.structure_generator = structure_generator
        self.population_size = population_size
        self.population : list[Molecule] = self.computer.optimize(
            self.calculator,
            self.structure_generator(
                self.base,
                self.population_size,
                self.computer,
            ),
        )

        self.population_size = len(self.population)

        self.energy_threshold = energy_threshold
        self.geometry_threshold = geometry_threshold

        self.generation_children_mutant_proportion = generation_children_mutant_proportion

        ### Mutation parameters ###
        self.mut_displacement_permutation_proportion = mut_displacement_permutation_proportion

        self.mut_displacement_number = mut_displacement_number
        self.mut_displacement_max = mut_displacement_max
        self.mut_permutation_num = mut_permutation_num

        # Generation parameters
        self.end_loop_number = end_loop_number
        self.cycle_counter = 0
        self.best_energy = min([mol.energy for mol in self.population])
        self.best_energy_loops = 0


    def is_pop_index_duplicate(self, i : int) -> bool:
        for j in range(i+1, len(self.population)):
            # Compare energies
            if abs(self.population[i].energy-self.population[j].energy) <= self.energy_threshold:
                # Then compare geometries
                if self.population[i].compare_geometry(self.population[j]) > self.geometry_threshold:
                    return True

        return False

    def remove_duplicates(self) -> None:
        with Pool(self.computer.cpu_count_limit) as pool:
            remove_mask : list[bool]  = pool.map(
                self.is_pop_index_duplicate,
                range(len(self.population)),
            )

        self.population = [
            mol for mol, is_duplicate
            in zip(self.population, remove_mask)
            if not is_duplicate
        ]


    def generate(self) -> list[Molecule]:
        remaining_population : int = self.population_size - len(self.population)
        remaining_population = floor(remaining_population * self.generation_children_mutant_proportion[0]/sum(self.generation_children_mutant_proportion))

        generated : list[Molecule] = self.computer.optimize(
            self.calculator,
            self.structure_generator(
                self.base,
                remaining_population,
                self.computer,
            ),
        )

        return generated

    def reproduce(self) -> list[Molecule]:
        remaining_population : int = self.population_size - len(self.population)
        remaining_population = floor(remaining_population * self.generation_children_mutant_proportion[1]/sum(self.generation_children_mutant_proportion))

        children : list[Structure] = []

        parents = [
            (mother, father)
            for mother, father
            in distinct_pairs(self.population)
        ]
        for mother, father in random.sample(parents, remaining_population):
            children.append(
                plane_mating(mother, father)
            )

        return [mol for mol in self.computer.optimize(self.calculator, children) if mol is not None]

    def mutate(self) -> list[Molecule]:
        remaining_population : int = self.population_size - len(self.population)
        remaining_population = floor(remaining_population * self.generation_children_mutant_proportion[2]/sum(self.generation_children_mutant_proportion))

        remaining_displacement : int = floor(remaining_population * self.mut_displacement_permutation_proportion[0]/sum(self.mut_displacement_permutation_proportion))
        remaining_permute : int = floor(remaining_population * self.mut_displacement_permutation_proportion[1]/sum(self.mut_displacement_permutation_proportion))

        mutants : list[Structure] = []

        for mutant in random.sample(self.population, remaining_displacement):
            mutants.append(
                mut_random(
                    mutant,
                    self.mut_displacement_max,
                )
            )

        for mutant in random.sample(self.population, remaining_permute):
            mutants.append(
                mut_permute(
                    mutant,
                    len(mutant)//2 if self.mut_permutation_num>=0 else self.mut_permutation_num,
                )
            )

        return [mol for mol in self.computer.optimize(self.calculator, mutants) if mol is not None]

    def remove_unfeasible(self) -> None:
        min_energy : float = min([mol.energy for mol in self.population])
        max_energy : float = max([mol.energy for mol in self.population])
        median_energy : float = (min_energy + max_energy)/2

        for i in reversed(range(len(self.population))):
            if self.population[i].energy > median_energy:
                del self.population[i]


    def get_best_energy(self) -> None:
        new_best_energy : float = min([mol.energy for mol in self.population])
        if new_best_energy < self.best_energy:
            self.best_energy = new_best_energy
            self.best_energy_loops = 0
        else:
            self.best_energy_loops+= 1

    def remove_top_half_energies(self) -> None:
        min_energy : float = min((mol.energy for mol in self.population))
        max_energy : float = max((mol.energy for mol in self.population))
        median_energy : float = (min_energy + max_energy)/2
        for i in reversed(range(len(self.population))):
            if self.population[i].energy > median_energy:
                del self.population[i]


    def loop(self) -> bool:
        self.cycle_counter+= 1

        self.remove_duplicates()
        self.remove_unfeasible()

        children : list[Molecule] = self.reproduce()
        mutants : list[Molecule] = self.mutate()
        generated : list[Molecule] = self.generate()

        self.population+= children
        self.population+= mutants
        self.population+= generated

        self.remove_duplicates()

        self.get_best_energy()
        return self.best_energy_loops < self.end_loop_number

    def save(self, file : str) -> None:
        print(file)
        pass
