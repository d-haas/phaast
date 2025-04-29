import random
import numpy as np

from structure import Atom, Structure


def plane_mating(struct1 : Structure, struct2 : Structure, rand_gen : random.Random | None = None) -> Structure:
    rng : random.Random = rand_gen if rand_gen else random.Random()

    plane_ortho_vec = np.linalg.norm(np.array(
        (rng.random()-.5 for _ in range(3)),
    ))

    # Get distances of atoms from the plane and order it
    struct1_dists = []
    cm1 = struct1.cm # Structure1's center of mass
    for atom in struct1:
        dist = atom.pos
