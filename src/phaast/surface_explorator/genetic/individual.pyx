# cython: freethreading_compatible = True
from typing import Iterable

cimport cython

from libc.math cimport NAN
from phaast.structure.primitives cimport Atom, Structure, Molecule

import struct

cdef class Individual(Molecule):
    descendants : list[cython.uint]
    id : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom], id : cython.uint, double energy = NAN, tuple descendants = ()):
        super().__init__(atoms_or_mol, energy)

        self.descendants : list[cython.uint] = list(descendants)
        self.id = id

    @property
    def is_optimized(self):
        return self.energy == self.energy

    def add_descendant(self, ind_id : cython.uint):
        self.descendants.append(ind_id)

    def get_descendants(self):
        return self.descendants

    def get_id(self):
        return self.id

    def as_bytes_no_type(self):
        prefix = struct.pack("Q", self.id)
        desc = struct.pack(
            "Q"*(len(self.descendants)+1),
            len(self.descendants),
            *self.descendants,
        )
        return prefix + desc + super().as_bytes()

    def as_bytes(self) -> bytes:
        prefix = struct.pack("c", b"d")

        return prefix + self.as_bytes_no_type()

    @classmethod
    def from_bytes(cls, data : bytes) -> Individual:
        tp, = struct.unpack_from("c", data)
        current_pointer = struct.calcsize("c")
        ancestors = None
        print("Tp is:")
        print(tp)

        if tp == b"m" or tp == b"o":
            ancestors, = struct.unpack_from("Q", data, current_pointer)
            current_pointer+= struct.calc_size("Q")
        elif tp == b"c":
            ancestors = struct.unpack_from("QQ", data, current_pointer)
            current_pointer+= struct.calc_size("QQ")

        descendants_num, = struct.unpack_from("Q", data, current_pointer)
        current_pointer+= struct.calcsize("Q")
        descendants_format = "Q"*descendants_num
        descendants = struct.unpack_from(descendants_format, data, 2)
        current_pointer+= struct.calcsize(descendants_format)

        id, = struct.unpack_from(
            "Q",
            data,
            current_pointer
        )
        current_pointer = struct.calcsize("Q")

        structure = Molecule.from_bytes(data[current_pointer:])

        if tp == b"d":
            return Individual(
                structure,
                id = id,
                descendants = descendants,
            )
        elif tp == b"m":
            return MutantIndividual(
                structure,
                ancestors,
                id = id,
                descendants = descendants,
            )
        elif tp == b"c":
            return ChildIndividual(
                structure,
                ancestors,
                id = id,
                descendants = descendants,
            )
        elif tp == b"o":
            return OptimizedIndividual(
                structure,
                ancestors,
                id = id,
                energy = structure.energy,
                descendants = descendants,
            )
        else:
            return None



    def as_data(self):
        return super().as_data() | {
            "type"              : "default",
            "id"                : self.id,
            "descendants"       : self.descendants,
        }

    @classmethod
    def from_data(cls, data):
        if data["type"] == "default":
            ind = Individual(
                Structure.from_data(data),
                id = data["id"],
                descendants = tuple(data["descendants"]),
            )
        elif data["type"] == "child":
            ind = ChildIndividual(
                Structure.from_data(data),
                parents = (data["parent_a"], data["parent_b"]),
                id = data["id"],
                descendants = tuple(data["descendants"]),
            )
        elif data["type"] == "mutant":
            ind = MutantIndividual(
                Structure.from_data(data),
                ancestor = data["ancestor"],
                id = data["id"],
                descendants = tuple(data["descendants"]),
            )
        elif data["type"] == "optimized":
            ind = OptimizedIndividual(
                Structure.from_data(data),
                ancestor = data["ancestor"],
                id = data["id"],
                energy = data["energy"],
                descendants = tuple(data["descendants"]),
            )
        else:
            raise TypeError(f"No type {data['type']} in data")

        return ind


    def __reduce__(self):
        return (self.__class__, (tuple(self), self.id, self.energy, tuple(self.descendants) ))

cdef class ChildIndividual(Individual):

    parent_a : cython.uint
    parent_b : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom], parents : tuple[cython.uint, cython.uint], id : cython.uint, tuple descendants = ()):
        super().__init__(
            atoms_or_mol, id,
            descendants = descendants,
        )

        self.parent_a = parents[0]
        self.parent_b = parents[1]

    @property
    def parents(self) -> tuple[cython.uint, cython.uint]:
        return (self.parent_a, self.parent_b)

    def as_bytes(self) -> bytes:
        prefix = struct.pack("cQQ", b"c", self.parent_a, self.parent_b)

        return prefix + super().as_bytes_no_type()

    def as_data(self):
        return super().as_data() | {
            "type"     : "child",
            "parent_a" : self.parent_a,
            "parent_b" : self.parent_b,
        }

    def __reduce__(self):
        return (self.__class__, ( tuple(self), (self.parent_a, self.parent_b), self.id, tuple(self.descendants) ))

cdef class MutantIndividual(Individual):

    ancestor : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : cython.uint, id : cython.uint, tuple descendants = ()):
        super().__init__(
            atoms_or_mol, id,
            descendants = descendants,
        )

        self.ancestor = ancestor

    def as_bytes(self) -> bytes:
        prefix = struct.pack("cQ", b"m", self.ancestor)

        return prefix + super().as_bytes_no_type()

    def as_data(self):
        return super().as_data() | {
            "type"     : "mutant",
            "ancestor" : self.ancestor,
        }

    def __reduce__(self):
        return (self.__class__, (tuple(self), self.ancestor, self.id, tuple(self.descendants) ))

cdef class OptimizedIndividual(Individual):

    ancestor : cython.uint

    def __init__(self, atoms_or_mol : Iterable[Atom], ancestor : cython.uint, id : cython.uint, energy : float, tuple descendants = ()):
        super().__init__(
            atoms_or_mol, id, energy,
            descendants = descendants,
        )

        self.ancestor = ancestor

    def as_bytes(self) -> bytes:
        prefix = struct.pack("cQ", b"o", self.ancestor)

        return prefix + super().as_bytes_no_type()

    def as_data(self):
        return super().as_data() | {
            "type"     : "optimized",
            "ancestor" : self.ancestor,
        }

    def __reduce__(self):
        return (self.__class__, ( tuple(self), self.ancestor, self.id, self.energy, tuple(self.descendants) ))
