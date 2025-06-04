import subprocess
import tempfile
from calculators import Calculator
from structure import Molecule, Structure


class XTB(Calculator):
    @staticmethod
    def optimize(structure : Structure) -> Molecule:
        with structure.to_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                which_xtb = subprocess.run(
                    [
                        "which",
                        "./calculators/xtb/xtb-dist/bin/xtb",
                    ],
                    capture_output = True,
                )
                xtb_path = which_xtb.stdout.strip(b"\n")

                if not xtb_path:
                    raise ValueError(
                        f"Could not locate XTB: {xtb_path}"
                    )

                subprocess.run(
                    [
                        xtb_path,
                        input_xyz_file.name,
                        f"--chrg {'+' if structure.charge>0 else ''}{structure.charge}",
                        "--opt",
                    ],
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )

                return Molecule.from_xyz(dir+"/xtbopt.xyz", structure.__charge)

    @staticmethod
    def measure_optimization_memory_usage(structure : Structure) -> int:
        with structure.to_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                which_xtb = subprocess.run(
                    [
                        "which",
                        "./calculators/xtb/xtb-dist/bin/xtb",
                    ],
                    capture_output = True,
                )
                xtb_path = which_xtb.stdout.strip(b"\n")

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
                        "--chrg", f"{'+' if structure.charge>0 else ''}{structure.charge}",
                        "--opt",
                        "-s",
                    ],
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )
                memory = int(open(dir+"/memory.out").read().splitlines()[-1])

        return memory

    @staticmethod
    def measure_optimization_time(structure : Structure) -> float:
        with structure.to_xyz() as input_xyz_file:
            with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
                which_xtb = subprocess.run(
                    [
                        "which",
                        "./calculators/xtb/xtb-dist/bin/xtb",
                    ],
                    capture_output = True,
                )
                xtb_path = which_xtb.stdout.strip(b"\n")

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
                        "--chrg", f"{'+' if structure.charge>0 else ''}{structure.charge}",
                        "--opt",
                        "-s",
                    ],
                    cwd = dir,
                    capture_output = False,
                    stdout = subprocess.DEVNULL,
                    stderr = subprocess.DEVNULL,
                )
                seconds = float(open(dir+"/time.out").read())

        return seconds
