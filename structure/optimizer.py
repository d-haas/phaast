from structure import Structure, Molecule
import subprocess
import tempfile


def optimize_structure(structure : Structure, charge : int = 0) -> Molecule:
    with structure.to_xyz() as input_xyz_file:
        with tempfile.TemporaryDirectory(prefix = "phaast_", suffix="_xtb") as dir:
            which_xtb = subprocess.run(
                [
                    "which",
                    "xtb-dist/bin/xtb",
                ],
                capture_output = True,
            )
            xtb_path = which_xtb.stdout.strip(b"\n")

            if not xtb_path:
                raise ValueError(
                    f"Could not locate XTB: {xtb_path}"
                )

            result = subprocess.run(
                [
                    xtb_path,
                    input_xyz_file.name,
                    f"-chrg {'+' if charge>0 else ''}{charge}",
                    "--opt",
                ],
                cwd = dir,
                capture_output = False,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL,
            )

            return Molecule.from_xyz(dir+"/xtbopt.xyz")


