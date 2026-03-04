from libc.math cimport fabs
from phaast.vector cimport Vector
from phaast.structure.primitives cimport Molecule
from cython.parallel import prange

import bisect, itertools

cpdef bool energy_difference(Molecule mol1, Molecule mol2, double tolerance):
    return fabs(mol1.energy - mol2.energy) < tolerance

cpdef bool grigoryan_springborg(Molecule mol1, Molecule mol2, double tolerance):
    """
    Compare different structures using the
    Grigoryan-Springborg algorithm
    DOI: 10.1140/epjd/e2005-00141-6
    Equation (1)
    """
    cdef int atoms_num = len(mol1) # Number of atoms in structure

    #Check if number of atoms is the same in both structures
    assert mol1.is_equal_to(mol2), "Both structure should have the same number of atoms"

    """
    Sum distances between atoms of each structure and
    store it in a ordered list for each structure for
    each combination of two elements

    Thanks Amanda
    """

    # I was gonna try to optimize this with fancy parallel for-loops,
    # tho it might be wise to keep it this way for now.

    cdef tuple dict_key
    cdef Vector diff

    cdef dict self_dists = {} # : dict[tuple[AtomicNumber, AtomicNumber], list[float]]
    for atom_i, atom_j in itertools.combinations(mol1, 2):
        dict_key = (atom_i.z, atom_j.z) if atom_j.z>atom_i.z else (atom_j.z, atom_i.z)
        if not dict_key in self_dists:
            self_dists[dict_key] = []
        diff = atom_i.pos - atom_j.pos
        bisect.insort(
            self_dists[dict_key],
            diff.cmod_sqr(),
        )


    cdef dict other_dists = {} # : dict[tuple[AtomicNumber, AtomicNumber], list[float]]
    for atom_i, atom_j in itertools.combinations(mol2, 2):
        dict_key = (atom_i.z, atom_j.z) if atom_j.z>atom_i.z else (atom_j.z, atom_i.z)
        if not dict_key in other_dists:
            other_dists[dict_key] = []
        diff = atom_i.pos - atom_j.pos
        bisect.insort(
            other_dists[dict_key],
            diff.mod_sqr,
        )

    # Get difference between each distance in each molecule (squared)
    cdef double sum_distances_squared_diff = 0
    for dict_key in self_dists:
        sum_distances_squared_diff+= sum([
            (i - j)**2
            for i, j
            in zip(self_dists[dict_key], other_dists[dict_key])
        ])

    # Calculate final value of Grigoryan-Springborg algorithm
    cdef double q = ( ( 2/(atoms_num*(atoms_num-1)) ) * sum_distances_squared_diff )**.5
    cdef double s = 1 / ( 1 + q )

    return s > tolerance

cpdef bool bonding_length(Molecule mol1, Molecule mol2, double tolerance, double bonding_tolerance):
    cdef dict mol1_bondings = mol1.get_bondings_lenghts(bonding_tolerance)
    cdef dict mol2_bondings = mol2.get_bondings_lenghts(bonding_tolerance)

    # Compare if both molecules have the same types of bondings
    if mol1_bondings.keys() != mol2_bondings.keys(): return False
    # At this point both molecules share the same bonding types

    for bonding in mol1_bondings:
        if len(mol1_bondings[bonding]) != len(mol2_bondings[bonding]):
            return False
    # At this point both molecules have the same number of bondings per type

    # Compare difference between distances for each bonding type and add to a general variable
    cdef double square_distances_difference_sum = 0
    for bonding in mol1_bondings:
        square_distances_difference_sum+= sum(
            [
                abs(i-j) for i, j
                in zip(
                    sorted(mol1_bondings[bonding]),
                    sorted(mol2_bondings[bonding]),
                )
            ]
        )

    # Use said variable (with positive value) to obtain a number between 1 and 0
    return 1 / (1 + square_distances_difference_sum) > tolerance
