import random
from typing import cast

def test_cython_element():
    from phaast.structure.primitives import Element
    from phaast.structure.constants import AtomicMass, AtomicNumber, AtomicRadi, AtomicSymbols

    z : AtomicNumber = cast(
        AtomicNumber,
        random.randint(1,20),
    )
    e = Element(z)

    assert e.radius == AtomicRadi[z]
    assert e.symbol == AtomicSymbols[z]
    assert e.mass == AtomicMass[z]

def test_cython_atom():
    from phaast.vector import Vector
    from phaast.structure.primitives import Atom

    vec = Vector(1, 3.0, 4.1)
    atom = Atom(3, vec)

    assert atom.z == 3, f"Atomic number is incorrect, should be 3 and not {atom.z}"

    assert (atom.pos.x, atom.pos.y, atom.pos.z) == (1.0,3.0,4.1), f"Atomic position should be (1, 3, 4.1), but it's {atom.pos}" 

    atom.pos.x+= 5
    assert atom.pos.x == 6, "Atom position wasn't properly modified"


def test_cython_structure():
    from phaast.vector import Vector
    from phaast.structure.primitives import Atom, Structure

    o_pos = (0, 0, 1.12)
    h1_pos = (0, 0.76, -0.47)
    h2_pos = (0,-0.76, -0.47)

    water = Structure(
        [
            Atom(8, Vector(*o_pos)),
            Atom(1, Vector(*h1_pos)),
            Atom(1, Vector(*h2_pos)),
        ]
    )

    saved_o_pos = None
    saved_h1_pos = None
    saved_h2_pos = None

    for i in range(len(water)):
        if water[i].z == 8:
            saved_o_pos = tuple(water[i].pos)
        elif not saved_h1_pos:
            saved_h1_pos = tuple(water[i].pos)
        else:
            saved_h2_pos = tuple(water[i].pos)

    assert saved_o_pos == o_pos
    assert saved_h1_pos == h1_pos
    assert saved_h2_pos == h2_pos

def test_cython_molecule():
    from phaast.vector import Vector
    from phaast.structure.primitives import Atom, Molecule


    o_pos = (0, 0, 1.12)
    h1_pos = (0, 0.76, -0.47)
    h2_pos = (0,-0.76, -0.47)

    water = Molecule(
        [
            Atom(8, Vector(*o_pos)),
            Atom(1, Vector(*h1_pos)),
            Atom(1, Vector(*h2_pos)),
        ],
        3,
    )

    saved_o_pos = None
    saved_h1_pos = None
    saved_h2_pos = None

    for i in range(len(water)):
        if water[i].z == 8:
            saved_o_pos = tuple(water[i].pos)
        elif not saved_h1_pos:
            saved_h1_pos = tuple(water[i].pos)
        else:
            saved_h2_pos = tuple(water[i].pos)

    assert saved_o_pos == o_pos
    assert saved_h1_pos == h1_pos
    assert saved_h2_pos == h2_pos
    assert water.energy == 3

def test_cython_pickle():
    import pickle
    from phaast.vector import Vector
    from phaast.structure.primitives import Atom, Structure, Molecule

    o_pos = (0, 0, 1.12)
    h1_pos = (0, 0.76, -0.47)
    h2_pos = (0,-0.76, -0.47)

    o_atom = Atom(8, Vector(*o_pos))

    s_water = Structure(
        [
            Atom(8, Vector(*o_pos)),
            Atom(1, Vector(*h1_pos)),
            Atom(1, Vector(*h2_pos)),
        ],
    )

    m_water = Molecule(
        [
            Atom(8, Vector(*o_pos)),
            Atom(1, Vector(*h1_pos)),
            Atom(1, Vector(*h2_pos)),
        ],
        3,
    )

    pickle.dumps(o_atom)

    pickle.dumps(s_water)

    pickle.dumps(m_water)
