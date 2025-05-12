from structure import Atom, Structure
import structure.optimizer
from vec import Vector

def run():
    struct = Structure([
        Atom(6, Vector(   0,   0,0)),
        Atom(6, Vector(   1,   0,0)),
        Atom(1, Vector(-0.3,-0.6,0)),
        Atom(1, Vector(-0.3, 0.6,0)),
        Atom(1, Vector( 1.3,-0.6,0)),
        Atom(1, Vector( 1.3, 0.6,0)),
    ])
    optimized = structure.optimizer.optimize_structure(struct, 0)

    print(f"Struct is: {struct.to_xyz_str()}")

    print(f"Optimized is: {optimized.to_xyz_str()}")


