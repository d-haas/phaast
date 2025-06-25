from calculators.custom import CustomCalculator
from computer import Computer
from structure import Base
import structure.creator
from calculators.xtb import XTB

from structure.creator.filter_list import FilterList, FilterMode
from surface_explorator.genetic import Genetic

def run():

    orca_input = """!PBE0 def2-TZVP OPT
* xyz 2 1
%XYZ%
*"""

    orca_output = """%LEN%
%W% %W% %W% %W% %W% %ENERGY%
%XYZ%"""

    orca = CustomCalculator(
        "Golfinho",
        "orca %ARGS% %FILE%",
        output_name = "output.xyz",

    )

