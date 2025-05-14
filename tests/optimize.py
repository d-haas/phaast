from structure import Atom, Structure
import structure.optimizer
from vec import Vector
from calculators.xtb import XTB

def run():
    struct = Structure([
        Atom(6, Vector(   0,   0,0)),
        Atom(6, Vector(   1,   0,0)),
        Atom(1, Vector(-0.3,-0.6,0)),
        Atom(1, Vector(-0.3, 0.6,0)),
        Atom(1, Vector( 1.3,-0.6,0)),
        Atom(1, Vector( 1.3, 0.6,0)),
    ])
    optimized = XTB.optimize_structure(struct, 0)

    print(f"Struct is: {struct.to_xyz_str()}")

    print(f"Optimized is: {optimized.to_xyz_str()}")

    print(f"Memory usage was close to: {XTB.measure_memory_usage(struct, 0)}")

    print(f"\nThe difference between them is {struct.compare(optimized)}")


