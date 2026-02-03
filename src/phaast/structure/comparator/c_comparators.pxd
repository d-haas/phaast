from phaast.structure.primitives cimport Molecule

cpdef bool energy_difference(Molecule mol1, Molecule mol2, double tolerance)

cpdef bool grigoryan_springborg(Molecule mol1, Molecule mol2, double tolerance)

cpdef bool bonding_length(Molecule mol1, Molecule mol2, double tolerance, double bonding_tolerance)
