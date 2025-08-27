import random
from typing import Iterable, Optional, cast
from math import ceil, floor
from bisect import insort

from computer import Computer
from structure import Atom, Molecule, Structure
from vec import Vector

from surface_explorator import SurfaceExplorator
from utils.typecheck import check_types
from utils.custom_iter import distinct_pairs

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
    calculator : str
    computer : Computer
    energy_threshold : float
    geometry_threshold : float
    children_mutant_ratio : float
    best_energy : float
    best_energy_loops : int
    cycle_counter : int
    end_criteria_loop_num : int
    mut_rand_permute_ratio : float
    mut_rand_max_displacement : float
    permute_num_permutations : int

    @check_types
    def __init__(
        self,
        structures : Iterable[Structure | Molecule],
        computer : Computer,
        energy_threshold : float,
        geometry_threshold : float,
        calculator : str,
        children_mutant_ratio : float = 1.0,
        end_criteria_loop_num : int = 9,
        mut_rand_permute_ratio : float = 1.0,
        mut_rand_max_displacement : float = 1.0,
        permute_num_permutations : int = 0
    ):
        self.computer = computer
        self.calculator = calculator
        self.population : list[Molecule] = [
            mol for mol
            in self.computer.optimize(self.calculator, list(structures))
            if mol is not None
        ]
        self.population_size = len(self.population)
        self.energy_threshold = energy_threshold
        self.geometry_threshold = geometry_threshold
        self.children_mutant_ratio = children_mutant_ratio
        self.best_energy = min([mol.energy for mol in self.population])
        self.best_energy_loops = 0
        self.end_criteria_loop_num = end_criteria_loop_num
        self.cycle_counter = 0

        ### Mutation parameters ###
        self.mut_rand_permute_ratio = mut_rand_permute_ratio
        self.mut_rand_max_displacement = mut_rand_max_displacement
        self.permute_num_permutations = permute_num_permutations

    def remove_duplicates(self) -> None:
        for i in reversed(range(len(self.population))):
            for j in reversed(range(i+1, len(self.population))):
                # Compare energies
                if abs(self.population[i].energy-self.population[j].energy) <= self.energy_threshold:
                    # Then compare geometries
                    if self.population[i].compare_geometry(self.population[j]) > self.geometry_threshold:
                        del self.population[j]

    def reproduce(self) -> list[Molecule]:
        remaining_population : int = self.population_size - len(self.population)
        remaining_population*= ceil(self.children_mutant_ratio/(self.children_mutant_ratio+1))

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
        remaining_population*= floor(1/(self.children_mutant_ratio+1))

        remaining_random : int = ceil(self.mut_rand_permute_ratio/(self.mut_rand_permute_ratio+1))
        remaining_permute : int = floor(1/(self.mut_rand_permute_ratio+1))

        mutants : list[Structure] = []

        for mutant in random.sample(self.population, remaining_random):
            mutants.append(
                mut_random(
                    mutant,
                    self.mut_rand_max_displacement,
                )
            )

        for mutant in random.sample(self.population, remaining_permute):
            mutants.append(
                mut_permute(
                    mutant,
                    len(mutant)//2 if self.permute_num_permutations>=0 else self.permute_num_permutations,
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
        print(f"After removing duplicates and unfeasible, population now has {len(self.population)} molecules.")

        children : list[Molecule] = self.reproduce()
        mutants : list[Molecule] = self.mutate()
        self.population+= children
        self.population+= mutants

        self.remove_duplicates()

        self.get_best_energy()
        return self.best_energy_loops < self.end_criteria_loop_num

    def save(self, file : str) -> None:
        print(file)
        pass
