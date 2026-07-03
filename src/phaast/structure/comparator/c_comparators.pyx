# cython: freethreading_compatible = True
from libc.math cimport fabs, sqrt
from phaast.vector cimport Vector, Vec
from phaast.structure.primitives cimport Atom, Molecule, CMolecule, CAtom
from cython.parallel import prange
from cython.view cimport array as cvarray
from libc.stdlib cimport malloc, free, qsort
import time

import bisect, itertools

cdef int MAX_ATOMIC_NUMBER = 99999 # Just a huge number to cap a few things

cpdef bool energy_difference(Molecule mol1, Molecule mol2, double tolerance):
    return fabs(mol1.energy - mol2.energy) < tolerance

cdef int atomic_pair_to_hash(int i, int j):
    if i > j:
        return (MAX_ATOMIC_NUMBER * i) + j
    else:
        return (MAX_ATOMIC_NUMBER * j) + i

cpdef bool grigoryan_springborg_old(Molecule mol1, Molecule mol2, double tolerance):
    """
    Compare different structures using the
    Grigoryan-Springborg algorithm
    DOI: 10.1140/epjd/e2005-00141-6
    Equation (1)
    """
    cdef int i, j
    cdef int atoms_num = len(mol1) # Number of atoms in structure

    #Check if number of atoms is the same in both structures
    assert mol1.is_equal_to(mol2), "Both structure should have the same number of atoms"

    cdef CAtom[:] atoms1 = cvarray(shape=(mol1.length,), itemsize=sizeof(CAtom), format="Iddd") 
    cdef CAtom[:] atoms2 = cvarray(shape=(mol2.length,), itemsize=sizeof(CAtom), format="Iddd") 

    cdef Atom atom_ptr
    for i in range(atoms_num):
        atom_ptr = mol1.atoms[i]
        atoms1[i].z = atom_ptr.z
        atoms1[i].pos.x = atom_ptr.pos.x
        atoms1[i].pos.y = atom_ptr.pos.y
        atoms1[i].pos.z = atom_ptr.pos.z

        atom_ptr = mol2.atoms[i]
        atoms2[i].z = atom_ptr.z
        atoms2[i].pos.x = atom_ptr.pos.x
        atoms2[i].pos.y = atom_ptr.pos.y
        atoms2[i].pos.z = atom_ptr.pos.z

    """
    Sum distances between atoms of each structure and
    store it in a ordered list for each structure for
    each combination of two elements

    Thanks Amanda
    """
    # I was gonna try to optimize this with fancy parallel for-loops,
    # tho it might be wise to keep it this way for now.

    #cdef tuple dict_key
    cdef int dict_key
    cdef Vec vi, vj
    cdef double diff

    cdef dict self_dists = {}
    for i in range(atoms_num):
        for j in range(i+1, atoms_num):
            dict_key = atomic_pair_to_hash(atoms1[i].z, atoms1[j].z)
            if dict_key not in self_dists:
                self_dists[dict_key] = []

            vi = atoms1[i].pos
            vj = atoms1[j].pos
            diff = ((vi.x-vj.x)**2) + ((vi.y-vj.y)**2) + ((vi.z-vj.z)**2)
            self_dists[dict_key].append(diff)

    for key in self_dists:
        self_dists[key].sort()


    cdef dict other_dists = {}
    for i in range(atoms_num):
        for j in range(i+1, atoms_num):
            dict_key = atomic_pair_to_hash(atoms2[i].z, atoms2[j].z)
            if dict_key not in other_dists:
                other_dists[dict_key] = []

            vi = atoms2[i].pos
            vj = atoms2[j].pos
            diff = ((vi.x-vj.x)**2) + ((vi.y-vj.y)**2) + ((vi.z-vj.z)**2)
            other_dists[dict_key].append(diff)

    for key in other_dists:
        other_dists[key].sort()

    # Get difference between each distance in each molecule (squared)
    cdef double sum_distances_squared_diff = 0
    for dict_key in self_dists:
        for i in range(len(self_dists[dict_key])):
            sum_distances_squared_diff+= (self_dists[dict_key][i] - other_dists[dict_key][i])**2

    # Calculate final value of Grigoryan-Springborg algorithm
    cdef double q = sqrt( ( 2/(atoms_num*(atoms_num-1)) ) * sum_distances_squared_diff )
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

cpdef bool charge_difference(Molecule mol1, Molecule mol2, double tolerance):

    cdef int atoms_num = len(mol1) # Number of atoms in structure

    #Check if number of atoms is the same in both structures
    assert mol1.is_equal_to(mol2), "Both structure should have the same number of atoms"

    charges1 = {}
    for atom in mol1:
        if atom.z in charges1:
            charges1[atom.z].append(atom.p_charge)
        else:
            charges1[atom.z] = [atom.p_charge]

    charges2 = {}
    for atom in mol2:
        if atom.z in charges2:
            charges2[atom.z].append(atom.p_charge)
        else:
            charges2[atom.z] = [atom.p_charge]

    cdef double sum_distances_squared_diff = 0
    for z in charges1:
        sum_distances_squared_diff+= sum([
            ( c1 - c2 )**2
            for c1, c2
            in zip(charges1[z], charges2[z])
        ])


    cdef double q = sqrt( sum_distances_squared_diff/atoms_num )
    cdef double s = 1 / ( 1 + q )

    return s > tolerance

cdef struct AtomDist:
    int hash
    double dist

cdef int gs_node_compare(const void* a, const void* b) nogil noexcept:
    cdef AtomDist da = (<AtomDist*>a)[0]
    cdef AtomDist db = (<AtomDist*>b)[0]

    if   da.hash < db.hash: return -1
    elif da.hash > db.hash: return  1

    if   da.dist < db.dist: return -1
    elif da.dist > db.dist: return  1

    return 0

cpdef bool grigoryan_springborg(Molecule mol1, Molecule mol2, double tolerance):
    """
    Compare different structures using the
    Grigoryan-Springborg algorithm
    DOI: 10.1140/epjd/e2005-00141-6
    Equation (1)
    """
    cdef int i, j
    cdef int atoms_num = len(mol1) # Number of atoms in structure

    #Check if number and type of atoms are the same in both structures
    #assert mol1.is_equal_to(mol2), "Both structure should have the same number of atoms"

    cdef CAtom[:] atoms1 = cvarray(shape=(mol1.length,), itemsize=sizeof(CAtom), format="Iddd") 
    cdef CAtom[:] atoms2 = cvarray(shape=(mol2.length,), itemsize=sizeof(CAtom), format="Iddd") 
    cdef Atom atom_ptr

    for i in range(atoms_num):
        atom_ptr = mol1.atoms[i]
        atoms1[i].z = atom_ptr.z
        atoms1[i].pos.x = atom_ptr.pos.x
        atoms1[i].pos.y = atom_ptr.pos.y
        atoms1[i].pos.z = atom_ptr.pos.z

        atom_ptr = mol2.atoms[i]
        atoms2[i].z = atom_ptr.z
        atoms2[i].pos.x = atom_ptr.pos.x
        atoms2[i].pos.y = atom_ptr.pos.y
        atoms2[i].pos.z = atom_ptr.pos.z

    """
    Sum distances between atoms of each structure and
    store it in a ordered list for each structure for
    each combination of two elements

    Thanks Amanda
    """

    cdef Vec vi, vj
    cdef double diff
    cdef int insert_loop_counter

    cdef AtomDist[:] self_dists = cvarray(shape=((atoms_num*(atoms_num-1))//2,), itemsize=sizeof(AtomDist), format="id")
    insert_loop_counter = 0
    for i in range(atoms_num):
        for j in range(i+1, atoms_num):
            vi = atoms1[i].pos
            vj = atoms1[j].pos
            diff = ((vi.x-vj.x)**2) + ((vi.y-vj.y)**2) + ((vi.z-vj.z)**2)
            self_dists[insert_loop_counter].hash = atomic_pair_to_hash(atoms1[i].z, atoms1[j].z)
            self_dists[insert_loop_counter].dist = diff
            insert_loop_counter+= 1


    cdef AtomDist[:] other_dists = cvarray(shape=((atoms_num*(atoms_num-1))//2,), itemsize=sizeof(AtomDist), format="id")
    insert_loop_counter = 0
    for i in range(atoms_num):
        for j in range(i+1, atoms_num):
            vi = atoms2[i].pos
            vj = atoms2[j].pos
            diff = ((vi.x-vj.x)**2) + ((vi.y-vj.y)**2) + ((vi.z-vj.z)**2)
            other_dists[insert_loop_counter].hash = atomic_pair_to_hash(atoms2[i].z, atoms2[j].z)
            other_dists[insert_loop_counter].dist = diff
            insert_loop_counter+= 1


    qsort(&self_dists[0], self_dists.shape[0], sizeof(AtomDist), &gs_node_compare)
    qsort(&other_dists[0], other_dists.shape[0], sizeof(AtomDist), &gs_node_compare)

    # Get difference between each distance in each molecule (squared)
    cdef double sum_distances_squared_diff = 0
    for i in range((atoms_num*(atoms_num-1))//2):
        sum_distances_squared_diff+= (self_dists[i].dist - other_dists[i].dist)**2

    # Calculate final value of Grigoryan-Springborg algorithm
    cdef double q = sqrt( ( 2/(atoms_num*(atoms_num-1)) ) * sum_distances_squared_diff )
    cdef double s = 1 / ( 1 + q )

    return s > tolerance
