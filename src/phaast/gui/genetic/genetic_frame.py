from __future__ import annotations
import threading
import time
from typing import TYPE_CHECKING

from phaast.surface_explorator.genetic.individual import ChildIndividual, Individual, MutantIndividual, OptimizedIndividual
if TYPE_CHECKING:
    from phaast.gui.genetic.__main__ import MainFrame

import tkinter as tk
from tkinter import ttk

from phaast.surface_explorator.genetic import Genetic
from phaast.gui.scroll_list import ScrollList
from phaast.gui.mol_viewer import MolViewer
from phaast.gui.utils import TkDict

class CommandList(ttk.Frame):

    def __init__(self, master : tk.Misc, struct : None = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.struct = struct

        self.title    = ttk.Label(self, text = "")
        self.ancestor = ttk.Button(self, text = "Ancestor")
        self.parent_a = ttk.Button(self, text = "Parent (Mother)")
        self.parent_b = ttk.Button(self, text = "Parent (Father)")
        self.title.pack(side = tk.TOP, fill = tk.X)

    def update(self):
        if isinstance(self.struct, MutantIndividual):
            self.parent_b.pack_forget()
            self.parent_a.pack_forget()
            self.ancestor.pack(side = tk.BOTTOM, fill = tk.X)
            self.title.config(text = "Mutated from:")
        elif isinstance(self.struct, ChildIndividual):
            self.parent_b.pack(side = tk.BOTTOM, fill = tk.X)
            self.parent_a.pack(side = tk.BOTTOM, fill = tk.X)
            self.ancestor.pack_forget()
            self.title.config(text = "Born from:")
        elif isinstance(self.struct, OptimizedIndividual):
            self.parent_b.pack_forget()
            self.parent_a.pack_forget()
            self.ancestor.pack(side = tk.BOTTOM, fill = tk.X)
            self.title.config(text = "Optimized from:")
        elif isinstance(self.struct, Individual):
            self.parent_b.pack_forget()
            self.parent_a.pack_forget()
            self.ancestor.pack_forget()
            self.title.config(text = "Migrated")
        else:
            self.parent_b.pack_forget()
            self.parent_a.pack_forget()
            self.ancestor.pack_forget()
            self.title.config(text = "")



class InfoList(ttk.Frame):

    def __init__(self, master : tk.Misc, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.fields = {
            "cycle_counter"            : "Cycles",
            "best_energy"              : "Min. energy",
            "total_optimizations"      : "Optimized",
            "total_converged"          : "Converged",
            "total_duplicates_removed" : "Duplicates removed",
            "total_unfeasible_removed" : "Unfeasible removed",
            "total_not_bonded_removed" : "Unbonded removed",
            "total_mutations"          : "Mutations",
            "total_mating"             : "Matings",
            "total_migrated"           : "Migrations",
        }
        self.vars = TkDict()
        for i, (field, name) in enumerate(self.fields.items()):
            temp_var = tk.StringVar(self, value = "0")
            temp_label = ttk.Label(self, text = (name+": ").rjust(20), width = 20)
            temp_value = ttk.Label(self, textvariable = temp_var, width = 5)

            self.vars[field] = temp_var
            
            temp_label.grid(
                column = (i%5) * 2,
                row = i//5,
                sticky = tk.EW,
            )
            temp_value.grid(
                column = ((i%5) * 2) + 1,
                row = i//5,
                sticky = tk.EW,
            )

class GeneticFrame(ttk.Frame):

    root : MainFrame
    algorithm : Genetic

    def __init__(self, master : MainFrame, algorithm : Genetic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.root = master
        self.algorithm = algorithm

        self.selected_generation : int = 0
        self.selected_individual : Individual | None = None

        self.viewer = MolViewer(self)
        self.viewer.animate = 1
        self.generation_list = ScrollList(
            self,
            width = 80,
            selectmode = tk.BROWSE,
            columns = ("generations",),
            display_columns = ("generations",),
            select_func = self.on_select_generation,
        )
        self.generation_list.tree.heading("generations", text = "Generations")
        self.population_list = ScrollList(
            self,
            width = (80, 110),
            selectmode = tk.BROWSE,
            columns = ("population", "energy"),
            display_columns = ("population", "energy"),
            select_func = self.on_select_individual,
        )
        self.population_list.tree.heading("population", text = "Population")
        self.population_list.tree.heading("energy", text = "Energy")
        self.descendant_list = ScrollList(
            self,
            width = (80, 110),
            selectmode = tk.BROWSE,
            columns = ("descendants", "energy"),
            display_columns = ("descendants", "energy"),
        )
        self.descendant_list.tree.heading("descendants", text = "Descendants")
        self.descendant_list.tree.heading("energy", text = "energy")
        self.command_list = CommandList(self)
        self.info_list = InfoList(self)

        self.generation_list.grid(column = 0, row = 0, sticky = tk.NSEW)
        self.population_list.grid(column = 1, row = 0, sticky = tk.NSEW)
        self.command_list.grid(column = 2, row = 0, sticky = tk.NSEW)
        self.viewer.grid(column = 3, row = 0, sticky = tk.NSEW)
        self.descendant_list.grid(column = 4, row = 0, sticky = tk.NSEW)
        self.info_list.grid(column = 0, row = 1, columnspan = 5, sticky = tk.NSEW)

        self.rowconfigure(0, weight = 1)
        self.columnconfigure(3, weight = 1)

        self.genetic_loop_thread = threading.Thread(target = self.genetic_loop)
        self.genetic_loop_thread.start()
        self.loop_thread = threading.Thread(target = self.loop)
        self.loop_thread.start()

        self.refresh()


    def on_select_generation(self, _ : tk.Event):
        selected_item = self.generation_list.get_selected_item()
        if selected_item:
            self.selected_generation = int(self.generation_list.get_item_values(selected_item)[0])

        self.refresh_population()

    def on_select_individual(self, _ : tk.Event):
        selected_item = self.population_list.get_selected_item()
        if selected_item:
            selected_individual_index = int(self.population_list.get_item_values(selected_item)[0])
            self.viewer.structure = self.algorithm.generations[self.selected_generation][selected_individual_index]

        self.refresh_descentants()

    def loop(self):
        self.soft_refresh()
        time.sleep(0.997)

    def genetic_loop(self):
        while self.algorithm.loop():
            self.soft_refresh()

    def soft_refresh(self):
        self.refresh_generations()
        self.refresh_statistics()

    def refresh(self):
        self.refresh_generations()
        self.refresh_population()
        self.refresh_statistics()

    def refresh_generations(self):
        self.generation_list.tree.delete(*self.generation_list.tree.get_children())

        for i in range(len(self.algorithm.generations)):
            self.generation_list.insert_item(str(i))

    def refresh_population(self):
        self.population_list.tree.delete(*self.population_list.tree.get_children())

        for i, individual in enumerate(self.algorithm.generations[self.selected_generation]):
            self.population_list.insert_item((i,individual.energy),)

    def refresh_statistics(self):
        for field in self.info_list.fields:
            self.info_list.vars[field] = str(getattr(self.algorithm, field))

    def refresh_descentants(self):
        if isinstance(self.viewer.structure, Individual):
            self.descendant_list.tree.delete(*self.descendant_list.tree.get_children())

            for i in range(len(self.viewer.structure.get_descendants())):
                self.descendant_list.insert_item(str(i))

