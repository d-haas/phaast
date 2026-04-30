from phaast.vector cimport Vector

cdef class Element:
    cdef public unsigned int z

cpdef Atom create_atom(unsigned int atomic_number, Vector pos)
cdef class Atom(Element):
    cdef public Vector pos
    cdef public double p_charge

cpdef Structure create_structure(object atoms)
cdef class Structure:
    cdef public Atom[:] atoms
    cdef public Py_ssize_t length

    cdef Vector get_cm(self)

cpdef Molecule create_molecule(object atoms, double energy)
cdef class Molecule(Structure):
    cdef public double energy

    cpdef bool is_bonded(self, double bonding_tolerance=*)
