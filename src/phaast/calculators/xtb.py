import os, subprocess, tempfile
from typing import Literal, Optional, TypeAlias
from phaast.calculators import Calculator
from phaast.structure import Molecule, Structure

OptimizationLevel : TypeAlias = Literal[
    "crude", "sloppy", "loose", "lax",
    "normal",
    "tight", "vtight", "extreme",
]

class XTB(Calculator):
    opt_level : OptimizationLevel
    charge : Optional[int]
    etemp : Optional[int]
    gfn : Optional[int]
    cycles : Optional[int]
    iterations : Optional[int]
    threads : int
    xtb_path : str
    def __init__(
        self,
        opt_level : OptimizationLevel = "normal",
        charge : Optional[int] = 0,
        etemp : Optional[int] = 300,
        gfn : Optional[int] = 2,
        cycles : Optional[int] = None,
        iterations : Optional[int] = None,
        threads : int = 1,
        xtb_path : str = "xtb",
    ):
        self.opt_level = opt_level
        self.charge = charge
        self.etemp = etemp
        self.gfn = gfn
        self.cycles = cycles
        self.iterations = iterations
        self.threads = threads
        self.xtb_path = xtb_path

    def __hash__(self) -> int:
        return hash("XTB")

    def get_args(self) -> list[str]:
        args : list[str] = []

        if self.charge:
            args+= ["--chrg", str(self.charge)]
        if self.etemp:
            args+= ["--etemp", str(self.etemp)]
        if self.gfn:
            args+= ["--gfn", str(self.gfn)]
        if self.cycles:
            args+= ["--cycles", str(self.cycles)]
        if self.iterations:
            args+= ["--iterations", str(self.iterations)]

        return args

    def optimize(self, structure : Structure) -> Molecule | None:
        if not len(structure):
            raise ValueError(
                "Structure is empty, is this some kind of joke?",
            )

        with structure.to_temp_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                xtb_path = os.path.abspath(self.xtb_path)

                if not xtb_path:
                    raise ValueError(
                        f"Could not locate XTB: {xtb_path}"
                    )

                subprocess.run(
                    [
                        xtb_path,
                        input_xyz_file.name,
                        "--opt", str(self.opt_level),
                        "-P", str(self.threads),
                    ] + self.get_args(),
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )

                if os.path.exists(dir+"/xtbopt.xyz"):
                    molecule = Molecule.from_xyz(dir+"/xtbopt.xyz")
                else:
                    molecule = None

        return molecule

    def measure_optimization_memory_usage(self, structure : Structure) -> int:
        with structure.to_temp_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                xtb_path = os.path.abspath(self.xtb_path)

                if not xtb_path:
                    raise ValueError(
                        f"Could not locate XTB: {xtb_path}"
                    )

                subprocess.run(
                    [
                        "/usr/bin/time",
                        "-f", "%M",
                        "-o", "memory.out",
                        xtb_path,
                        input_xyz_file.name,
                        "--opt",
                        "-P", str(self.threads),
                        "-s",
                    ] + self.get_args(),
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )
                memory = int(open(dir+"/memory.out").read().splitlines()[-1])

        return memory

    def measure_optimization_time(self, structure : Structure) -> float:
        with structure.to_temp_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                xtb_path = os.path.abspath(self.xtb_path)

                if not xtb_path:
                    raise ValueError(
                        f"Could not locate XTB: {xtb_path}"
                    )

                subprocess.run(
                    [
                        "/usr/bin/time",
                        "-f", "%e",
                        "-o", "time.out",
                        xtb_path,
                        input_xyz_file.name,
                        "--opt",
                        "-P", str(self.threads),
                        "-s",
                    ] + self.get_args(),
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )
                seconds = float(open(dir+"/time.out").read())

        return seconds
