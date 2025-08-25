from typing import Any
from calculators import Calculator
from structure import Molecule, Structure
import subprocess, tempfile, os

class CustomCalculator(Calculator):
    command : str
    name    : str
    args    : dict[str, Any]
    def __init__(
        self,
        name : str,
        command_layout : str,
        output_name : str,
        #input_format : str,
        #output_format : str,
        **kwargs : Any,
    ):
        self.command = command_layout
        self.name = name
        self.output_name = output_name
        self.args = kwargs

    def get_args(self) -> str:
        temp_args : list[str] = []
        for arg, value in self.args.items():
            if len(arg)==1:
                temp_args.append( f"-{arg} {value}")
            else:
                temp_args.append(f"--{arg} {value}")

        return " ".join(temp_args)

    def optimize(self, structure : Structure) -> Molecule | None:
        with structure.to_temp_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                subprocess.run(
                    self.command.replace("%FILE%", input_xyz_file.name).replace("%ARGS%", self.get_args()),
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )

                if os.path.exists(f"{dir}/{self.output_name}"):
                    molecule = Molecule.from_xyz(dir+"/xtbopt.xyz")
                else:
                    molecule = None

        return molecule

    def measure_optimization_memory_usage(self, structure : Structure) -> int:
        with structure.to_temp_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                subprocess.run(
                    [
                        "/usr/bin/time",
                        "-f", "%M",
                        "-o", "memory.out",
                        self.command.replace("%FILE%", input_xyz_file.name).replace("%ARGS%", self.get_args()),
                    ],
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )
                memory = max([
                    int(line) for line
                    in open(dir+"/memory.out").read().splitlines()
                ])

        return memory

    def measure_optimization_time(self, structure : Structure) -> float:
        with structure.to_temp_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                which_xtb = subprocess.run(
                    [
                        "which",
                        "./calculators/xtb/xtb-dist/bin/xtb",
                    ],
                    capture_output = True,
                )
                xtb_path = which_xtb.stdout.strip(b"\n")
                xtb_path = os.path.abspath("./calculators/xtb/xtb-dist/bin/xtb")

                if not xtb_path:
                    raise ValueError(
                        f"Could not locate XTB: {xtb_path}"
                    )

                subprocess.run(
                    [
                        "/usr/bin/time",
                        "-f", "%e",
                        "-o", "time.out",
                        self.command.replace("%FILE%", input_xyz_file.name).replace("%ARGS%", self.get_args()),
                    ],
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )
                seconds = float(open(dir+"/time.out").read())

        return seconds

    def __hash__(self) -> int:
        return hash(self.name)
