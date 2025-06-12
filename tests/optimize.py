from structure import Atom, Structure
from vec import Vector
from calculators.xtb import XTB

def run():
    struct = Structure(
        [
            Atom(6, Vector( 0.0, 0.0,0)),
            Atom(6, Vector( 1.0, 0.0,0)),
            Atom(1, Vector(-0.3,-0.6,0)),
            Atom(1, Vector(-0.3, 0.6,0)),
            Atom(1, Vector( 1.3,-0.6,0)),
            Atom(1, Vector( 1.3, 0.6,0)),
        ],
    )
    optimized = None
    calc = XTB(charge = 2)
    while not optimized:
        optimized = calc.optimize(struct)

    print(f"Struct is: {struct.to_xyz_str()}")

    print(f"Optimized is: {optimized.to_xyz_str()}")

    print(f"Memory usage was close to: {calc.measure_optimization_memory_usage(struct)}")

    print(f"\nThe difference between them is {struct.compare_geometry(optimized)}")


