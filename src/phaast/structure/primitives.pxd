from phaast.vector cimport Vector

cdef class Element:
    cdef readonly unsigned int z

cpdef Atom create_atom(unsigned int atomic_number, Vector pos)
cdef class Atom(Element):
    cdef public Vector pos

cpdef Structure create_structure(object atoms)
cdef class Structure:
    cdef readonly Atom[:] atoms
    cdef public Py_ssize_t length

    cdef Vector get_cm(self)

cpdef Molecule create_molecule(object atoms, double energy)
cdef class Molecule(Structure):
    cdef public double energy

    cpdef bool is_bonded(self, double bonding_tolerance=*)
