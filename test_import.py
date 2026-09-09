import base64

from phaast.surface_explorator.genetic import Genetic
from phaast.structure import Atom, Molecule
from phaast.surface_explorator.genetic.individual import Individual
from phaast.vector import Vector

C1 = Atom(6, Vector(20, 20, 20))
mol = Molecule.from_xyz_str("""12
Coordinates from ORCA-job E -1000.111
C 20 20 20
C 10 10 10""")
bmol = mol.as_bytes()
same_mol = Molecule.from_bytes(bmol)

BC1 = C1.as_bytes()
NEW_C1 = Atom.from_bytes(BC1)

#print(C1)
#print(NEW_C1)
#print("")
#print(mol)
#print(same_mol)

ind = Individual(mol, 0, mol.energy)
b_ind = ind.as_bytes()
ind_ = Individual.from_bytes(b_ind)
s_ind = base64.b64encode(b_ind).decode("ascii")
b_ind_ = base64.b64decode(s_ind.encode("ascii"))

print(b_ind)
print()
print(s_ind)
print()
print(b_ind_)
print()
print(b_ind==b_ind_)


#a = Genetic.load("phaast_genetic.json")
