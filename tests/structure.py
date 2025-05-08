from structure import Structure, Atom
import structure.creator

def run():
    carbon = Atom(6)
    hydrogen = Atom(1)

    base = Structure(
        [
            carbon.copy()
            for _
            in range(4)
        ] + [
            hydrogen.copy()
            for _
            in range(10)
        ],
    )

    print(repr(structure.creator.generate_random_structure(base)))
