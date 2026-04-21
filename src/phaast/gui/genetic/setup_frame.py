from __future__ import annotations
from typing import Any, TYPE_CHECKING

import tkinter as tk

from phaast.structure.comparator import ComparisonSequence, EnergyDifference, GrigoryanSpringborg
from phaast.surface_explorator.genetic.crossover import PlaneMating
from phaast.surface_explorator.genetic.migration.hedron_universe import HedronMigrator
from phaast.surface_explorator.genetic.mutation import DisplacementMutator, PermuteMutator, TwistMutator

from phaast.calculators.xtb import XTB
from phaast.computer import Computer
from phaast.structure import Base
from phaast.surface_explorator.genetic.migration.filter_list import FilterList, FilterMode
from phaast.surface_explorator.genetic import Genetic
from phaast.gui.utils import TkDict


class SetupFrame(tk.Frame):

    fields : TkDict

    def __init__(self, master : tk.Misc, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        base_values : dict[str, dict[str, tuple[str, type, Any]]] = {
            "Main" : {
                "stoichiometry"                : ("Stoichiometry"     , str  , ""),
                "output_prefix"                : ("Output prefix"     , str  , "OUTPUT_"),
                "return_number"                : ("Return number"     , int  , 10),
                "population_size"              : ("Population size"   , int  , 10000),
                "charge"                       : ("Charge"            , int  , 0),
                "threads"                      : ("Threads"           , int  , 0),
                "xtb_threads"                  : ("Threads (XTB)"     , int  , 4),
                "xtb_path"                     : ("XTB path"          , str  , "xtb"),
                "energy_threshold"             : ("Energy threshold"  , float, 1e-4),
                "geometry_threshold"           : ("Geometry threshold", float, 0.91),
                "end_loop_number"              : ("Loops on minimum"  , int  , 11), 
                "comparison_bonding_tolerance" : ("Bonding tolerance" , float, 0.29),
                "remove_unbonded"              : ("Remove unbonded"   , tuple, ("final", "always", "never")),
            },
            "Operators weights" : {
                "mut_disp_w"  : ("Mutation displacement", float, 3.0),
                "mut_perm_w"  : ("Mutation permutation" , float, 2.0),
                "mut_twist_w" : ("Mutation twist"       , float, 1.0),
                "crov_w"      : ("Crossing-over"        , float, 1.0),
                "migr_w"      : ("Migration"            , float, 1.0),
            },
            "Operators values" : {
                "mut_disp_min" : ("Minimum displacement distance", float, 1.3),
                "mut_disp_max" : ("Maximum displacement distance", float, 1.3),
                "mut_disp_num" : ("Displacement atom number"     , int  , 0),
                "mut_perm_num" : ("Permutation number"           , int  , 0),
                "mut_twist_min_angle" : ("Minimum twist angle"   , float, 90.0),
                "mut_twist_max_angle" : ("Maximum twist angle"   , float, 270.0),
            },
        }

        self.fields = TkDict()

        self.columnconfigure((0, 1), weight = 1)
        for frame_num, (category, fields) in enumerate(base_values.items()):

            temp_frame = tk.LabelFrame(
                self,
                text = category,
                background = "#1e1e2e",
                foreground = "#cdd6f4",
            )

            for i, (var, (name, tp, default)) in enumerate(fields.items()):
                temp_label = tk.Label(
                    temp_frame,
                    text = name,
                    background = "#1e1e2e",
                    foreground = "#cdd6f4",
                )

                if tp == str:
                    temp_var = tk.StringVar(self, value = default)
                elif tp == int:
                    temp_var = tk.IntVar(self, value = default)
                elif tp == float:
                    temp_var = tk.DoubleVar(self, value = default)
                elif tp == tuple:
                    temp_var = tk.StringVar(self, value = default[0])
                else:
                    raise ValueError("Something's wrong with base values")

                self.fields[var] = temp_var

                if tp == tuple:
                    if TYPE_CHECKING:
                        assert isinstance(temp_var, tk.StringVar)

                    temp_entry = tk.OptionMenu(
                        temp_frame,
                        temp_var,
                        *default,
                    )
                    temp_entry.configure(
                        background = "#11111b",
                        foreground = "#cdd6f4",
                    )
                else:
                    temp_entry = tk.Entry(
                        temp_frame,
                        textvariable = temp_var,
                        background = "#11111b",
                        foreground = "#cdd6f4",
                        highlightbackground = "#313244",
                        highlightcolor = "#585b70",
                    )

                temp_label.grid(sticky = tk.W, row = i, column = 0)
                temp_entry.grid(sticky = tk.E, row = i, column = 1)

            temp_frame.grid(
                sticky = tk.NSEW,
                column = 0 if frame_num == 0 else 1,
                row = 0 if frame_num < 2 else 1,
                rowspan = 2 if frame_num == 0 else 1,
                # side = tk.LEFT, anchor = tk.N
            )

    def get_algorithm(self) -> Genetic:


        base = Base(self.fields.stoichiometry)

        calc = XTB(
            charge = self.fields.charge,
            threads = self.fields.xtb_threads,
            xtb_path = self.fields.xtb_path,
        )

        computer = Computer(
            cpu_count_limit = self.fields.threads,
        )

        computer.add_calculator("xtb", calc)

        filter_list = FilterList(FilterMode.EXCLUDE, ((1,1),))

        migrator = [
            (
                self.fields.migr_w,
                HedronMigrator(base, 20, filter_list),
            ),
        ]

        mutators = [
            (
                self.fields.mut_disp_w,
                DisplacementMutator(
                    self.fields.mut_disp_num,
                    self.fields.mut_disp_min,
                    self.fields.mut_disp_max,
                ),
            ),
            (
                self.fields.mut_perm_w,
                PermuteMutator(
                    self.fields.mut_perm_num,
                )
            ),
            (
                self.fields.mut_twist_w,
                TwistMutator(
                    self.fields.mut_twist_min_angle,
                    self.fields.mut_twist_max_angle,
                )
            ),
        ]

        crossover = [
            (
                self.fields.crov_w,
                PlaneMating(),
            ),
        ]

        grigoryan_springborg = GrigoryanSpringborg(self.fields.geometry_threshold)


        comparison_algorithm = ComparisonSequence(
            EnergyDifference(self.fields.energy_threshold),
            grigoryan_springborg,
        )

        assert self.fields.remove_unbonded in ("always", "final", "never"), "Wrong remove_unbonded option"
        if self.fields.remove_unbonded == "always":
            do_remove_unbonded = True
        else:
            do_remove_unbonded = False

        loading_label = tk.Label(self, text = "Generating population...")
        loading_label.grid(
            column = 0,
            row = 2,
            columnspan = 2,
        )

        self.update()

        genetic = Genetic(
            population_size = self.fields.population_size,
            computer = computer,
            calculator = "xtb",

            mutations = mutators,
            crossovers = crossover, #type: ignore
            migrators = migrator, #type: ignore

            comparison_algorithm = comparison_algorithm,

            do_remove_unbonded = do_remove_unbonded,

            end_loop_number = self.fields.end_loop_number,
        )
        
        loading_label.grid_forget()

        return genetic
