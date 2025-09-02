import xml.etree.ElementTree as ET

# Load the XML file
tree = ET.parse("elements.xml")
root = tree.getroot()

# Namespaces (from your XML header)
ns = {"bo": "http://www.blueobelisk.org/dict/terminology"}

# Dictionaries
atomic_number_to_mass = {}
atomic_number_to_covalent_radius = {}

# Loop over each atom entry
for atom in root.findall("{http://www.xml-cml.org/schema}atom"):
    atomic_number = None
    mass = None
    covalent_radius = None

    # Go through all <scalar> children
    for scalar in atom.findall("{http://www.xml-cml.org/schema}scalar"):
        if scalar is None: continue

        dict_ref = scalar.attrib.get("dictRef")
        
        if dict_ref == "bo:atomicNumber":
            atomic_number = int(scalar.text)
        elif dict_ref == "bo:mass":
            try:
                mass = float(scalar.text)
            except ValueError:
                pass
        elif dict_ref == "bo:radiusCovalent":
            try:
                covalent_radius = float(scalar.text)
            except ValueError:
                pass

    # Only add if data exists
    if atomic_number is not None:
        if mass is not None:
            atomic_number_to_mass[atomic_number] = mass
        if covalent_radius is not None:
            atomic_number_to_covalent_radius[atomic_number] = covalent_radius


with open("consts_xml.py", "w") as file:
    for k in sorted(atomic_number_to_covalent_radius.keys()):
        file.write(f"\t{k} : {atomic_number_to_covalent_radius[k]},\n")
    # Example: print first few entries
    for k in sorted(atomic_number_to_mass.keys()):
        file.write(f"\t{k} : {atomic_number_to_mass[k]},\n")

