import os, subprocess, tempfile, shutil
import threading
import time
from typing import Generator, Literal, TypeAlias
from phaast.calculators import Calculator
from phaast.structure import Molecule, Structure

OptimizationLevel : TypeAlias = Literal[
    "crude", "sloppy", "loose", "lax",
    "normal",
    "tight", "vtight", "extreme",
]

Functional : TypeAlias = Literal[
# Gradient corrected
"HFS", "LDA", "LSD", "VWN", "VWN5", "VWN3", "PWLDA", "BP86", "BP", "BLYP", "OLYP", "GLYP", "XLYP", "PW91", "mPWPW", "mPWLYP", "PBE", "RPBE", "REVPBE", "RPW86PBE", "PWP",

# Hybrid
"B1LYP", "B3LYP", "B3LYP/G", "O3LYP", "X3LYP", "B1P", "B3P", "B3PW", "PW1PW", "mPW1PW", "mPW1LYP", "PBE0", "REVPBE0", "REVPBE38", "BHANDHLYP",

# Meta-GGA and hybrid meta-GGA
"TPSS", "TPSSh", "TPSS0", "M06L", "M06", "M062X", "PW6B95", "B97M-V", "B97M-D3BJ", "B97M-D4", "SCANfunc", "r2SCAN", "r2SCANh", "r2SCAN0", "r2SCAN50",
]

BasisSet : TypeAlias = Literal[
# Pople-style
"STO-3G", "3-21G", "3-21GSP", "4-22GSP", "6-31G", "m6-31G", "6-311G",

# def2
"def2-SVP", "def2-SV(P)", "def2-TZVP", "def2-TZVP(-f)", "def2-TZVPP", "def2-QZVP", "def2-QZVPP",

# def
"def-TZVP", "ma-def-TZVP",

#
"SV", "SV(P)", "SVP", "TZV", "TZV(P)", "TZVP", "TZVPP", "QZVP", "QZVPP",
]

class Orca(Calculator):
    functional : Functional
    basis_set : BasisSet
    charge : int
    spin_multiplicity : int
    threads : int
    orca_path : str
    def __init__(
        self,
        functional : Functional,
        basis_set : BasisSet,
        spin_multiplicity : int,
        charge : int = 0,
        threads : int = 1,
        orca_path : str = "orca",
    ):
        self.functional = functional
        self.basis_set = basis_set
        self.charge = charge
        self.spin_multiplicity = spin_multiplicity
        self.threads = threads
        self.orca_path = orca_path

    def __hash__(self) -> int:
        return hash("ORCA")

    def optimize(self, structure : Structure) -> Molecule | None:
        if not len(structure):
            raise ValueError(
                "Structure is empty, is this some kind of joke?",
            )

        with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_orca") as dir:
            with tempfile.NamedTemporaryFile(mode = "w+", prefix="phaast_inp_", dir=dir) as input_file:

                input_file.write(
                    "\n".join(
                        [
                            f"!{self.functional} {self.basis_set} OPT",
                            f"%PAL NPROCS {self.threads} END",
                            f"* xyz {self.charge} {self.spin_multiplicity}"
                        ]
                        +
                        structure.to_xyz_str().splitlines()[2:]
                        + ["*"]
                    )
                )
                # For some GD reason, the files needs to be read
                # before xtb uses it (TF????)
                input_file.read()

                orca_path = shutil.which(self.orca_path)

                if not orca_path:
                    raise ValueError(
                        f"Could not locate Orca: {orca_path}"
                    )

                subprocess.run(
                    [
                        orca_path,
                        input_file.name,
                    ],
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )

                output_path = input_file.name+".xyz"
                if os.path.exists(output_path):
                    molecule = Molecule.from_xyz(output_path)
                else:
                    molecule = None

        return molecule

    def optimize_trj(self, structure : Structure) -> Generator[Molecule, Molecule, Literal[True]]:
        if not len(structure):
            raise ValueError(
                "Structure is empty, is this some kind of joke?",
            )

        with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_orca") as dir:
            with tempfile.NamedTemporaryFile(mode = "w+", prefix="phaast_inp_", dir=dir) as input_file:

                input_str = "\n".join(
                    [
                        f"!{self.functional} {self.basis_set} OPT",
                        f"%pal nprocs {self.threads} end",
                        f"* xyz {self.charge} {self.spin_multiplicity}"
                    ]
                    +
                    structure.to_xyz_str().splitlines()[2:]
                    + ["*"]
                )
                input_file.write(input_str)
                # For some GD reason, the files needs to be read
                # before orca uses it (TF????)
                input_file.read()

                print()
                print(input_str)
                print()

                orca_path = shutil.which(self.orca_path)

                if not orca_path:
                    raise ValueError(
                        f"Could not locate Orca: {orca_path}"
                    )

                thread = threading.Thread(
                    target = subprocess.run,
                    args = ([orca_path, input_file.name,],),
                    kwargs = {
                        "cwd" : dir,
                        "capture_output" : False,
                        "stdout" : subprocess.DEVNULL,
                        "stderr" : subprocess.DEVNULL,
                    }

                )
                thread.start()
                line_number = 0
                while thread.is_alive():
                    output_path = input_file.name+"_trj.xyz"
                    if os.path.exists(output_path):
                        with open(output_path) as file:
                            file_string = file.read()
                            file_lines = file_string.splitlines()
                            if len(file_lines) > line_number:
                                line_number = len(file_lines)
                                try:
                                    lines_str = "\n".join(file_lines[-(len(structure)+2):])
                                    print("====LINES====")
                                    print(lines_str)
                                    print("=============")
                                    molecule = Molecule.from_xyz_str(lines_str)
                                    yield molecule
                                finally:
                                    pass

                    time.sleep(0.1)

                output_path = input_file.name+".xyz"
                if os.path.exists(output_path):
                    yield Molecule.from_xyz(output_path)

        return True
