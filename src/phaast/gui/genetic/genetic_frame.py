from __future__ import annotations
import enum
from math import nan
import threading
import time
from typing import NamedTuple

import tkinter as tk
from tkinter import ttk

from phaast.structure import Structure
from phaast.surface_explorator.genetic.individual import ChildIndividual, Individual, MutantIndividual, OptimizedIndividual
from phaast.surface_explorator.genetic import Genetic
from phaast.gui.scroll_list import ScrollNumberList
from phaast.gui.mol_viewer import MolViewer
from phaast.gui.utils import TkDict

class SortingType(enum.Enum):
    ID = 0
    ENERGY = 1

class SortingOrder(enum.Enum):
    NORMAL = 0
    REVERSE = 1

class Sorting(NamedTuple):
    type  : SortingType
    order : SortingOrder

class CommandList(ttk.Frame):

    def __init__(self, master : GeneticFrame, struct : None | Individual = None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.parent = master

        self.struct = struct

        self.title    = ttk.Label(self, text = "")
        self.ancestor = ttk.Button(
            self,
            text = "Ancestor",
            command = self.change_to_ancestor,
        )
        self.parent_a = ttk.Button(
            self,
            text = "Parent (Mother)",
            command = self.change_to_parent_a,
        )
        self.parent_b = ttk.Button(
            self,
            text = "Parent (Father)",
            command = self.change_to_parent_b,
        )
        self.title.pack(side = tk.LEFT, fill = tk.X)

    def refresh(self):
        if isinstance(self.parent.viewer.structure, MutantIndividual):
            self.parent_a.pack_forget()
            self.parent_b.pack_forget()
            self.ancestor.pack(side = tk.LEFT, fill = tk.X)
            self.title.config(text = "Mutated from:")
        elif isinstance(self.parent.viewer.structure, ChildIndividual):
            self.parent_a.pack(side = tk.LEFT, fill = tk.X)
            self.parent_b.pack(side = tk.LEFT, fill = tk.X)
            self.ancestor.pack_forget()
            self.title.config(text = "Born from:")
        elif isinstance(self.parent.viewer.structure, OptimizedIndividual):
            self.parent_a.pack_forget()
            self.parent_b.pack_forget()
            self.ancestor.pack(side = tk.LEFT, fill = tk.X)
            self.title.config(text = "Optimized from:")
        elif isinstance(self.parent.viewer.structure, Individual):
            self.parent_a.pack_forget()
            self.parent_b.pack_forget()
            self.ancestor.pack_forget()
            self.title.config(text = "Migrated")
        else:
            self.parent_a.pack_forget()
            self.parent_b.pack_forget()
            self.ancestor.pack_forget()
            self.title.config(text = "")

    def change_to_ancestor(self):
        if isinstance(self.parent.viewer.structure, (MutantIndividual, OptimizedIndividual)):
            self.parent.change_individual(
                self.parent.algorithm.population_ids[self.parent.viewer.structure.ancestor]
            )

    def change_to_parent_a(self):
        if isinstance(self.parent.viewer.structure, ChildIndividual):
            self.parent.change_individual(
                self.parent.algorithm.population_ids[self.parent.viewer.structure.parents[0]]
            )

    def change_to_parent_b(self):
        if isinstance(self.parent.viewer.structure, ChildIndividual):
            self.parent.change_individual(
                self.parent.algorithm.population_ids[self.parent.viewer.structure.parents[1]]
            )


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

    root : tk.Misc
    algorithm : Genetic

    def __init__(self, master : tk.Misc, algorithm : Genetic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.root = master
        self.algorithm = algorithm

        self.selected_generation : int = 0
        self.selected_individual : Individual | None = None

        self.viewer = MolViewer(self)
        self.viewer.animate = 1
        self.generation_list = ScrollNumberList(
            self,
            width = (83,),
            selectmode = tk.BROWSE,
            columns = ("generations",),
            display_columns = ("generations",),
            select_func = self.on_select_generation,
        )
        self.generation_list.heading("generations", text = "Generations")
        self.population_list = ScrollNumberList(
            self,
            width = (83, 137),
            selectmode = tk.BROWSE,
            columns = ("population", "energy"),
            display_columns = ("population", "energy"),
            select_func = self.on_select_individual,
        )
        self.population_list.heading("population", text = "Population")
        self.population_list.heading("energy", text = "Energy")
        self.descendant_list = ScrollNumberList(
            self,
            width = (83, 137),
            selectmode = tk.BROWSE,
            columns = ("descendants", "energy"),
            display_columns = ("descendants", "energy"),
            select_func = self.on_select_descendant,
        )
        self.descendant_list.heading("descendants", text = "Descendants")
        self.descendant_list.heading("energy", text = "Energy")
        self.command_list = CommandList(self)
        self.info_list = InfoList(self)

        self.generation_list.grid(column = 0, row = 0, sticky = tk.NSEW, rowspan = 2)
        self.population_list.grid(column = 1, row = 0, sticky = tk.NSEW, rowspan = 2)
        self.command_list.grid(column = 2, row = 0, sticky = tk.NSEW)
        self.viewer.grid(column = 2, row = 1, sticky = tk.NSEW)
        self.descendant_list.grid(column = 3, row = 0, sticky = tk.NSEW, rowspan = 2)
        self.info_list.grid(column = 0, row = 2, columnspan = 4, sticky = tk.NSEW)

        self.rowconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)

        self.genetic_loop_thread = threading.Thread(target = self.genetic_loop)
        self.genetic_loop_thread.start()
        self.loop_thread = threading.Thread(target = self.loop)
        self.loop_thread.start()

        self.history : list[Structure] = []
        self.future : list[Structure] = []
        self.root.bind("<Control-z>", self.reverse_history)
        self.root.bind("<Control-y>", self.forward_history)

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
            self.change_individual(self.algorithm.generations[self.selected_generation][selected_individual_index])

    def on_select_descendant(self, _ : tk.Event):
        selected_item = self.descendant_list.get_selected_item()
        if selected_item and isinstance(self.viewer.structure, Individual):
            selected_descendant_index = int(self.descendant_list.get_item_values(selected_item)[0])
            self.change_individual(self.viewer.structure.get_descendants()[selected_descendant_index])

    def change_individual(self, individual : Individual):
        self.add_to_history(self.viewer.structure)
        self.viewer.structure = individual
        self.refresh_descentants()
        self.command_list.refresh()

    def add_to_history(self, struct : Structure):
        self.history.append(struct)
        self.future.clear()

    def reverse_history(self, _ : tk.Event):
        if self.history:
            self.future.append(self.viewer.structure)
            self.viewer.structure = self.history.pop(-1)
            self.refresh_descentants()
            self.command_list.refresh()

    def forward_history(self, _ : tk.Event):
        if self.future:
            self.history.append(self.viewer.structure)
            self.viewer.structure = self.future.pop(-1)
            self.refresh_descentants()
            self.command_list.refresh()

    def loop(self):
        self.refresh_statistics()
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
            self.population_list.insert_item((i, individual.energy),)

    def refresh_statistics(self):
        for field in self.info_list.fields:
            self.info_list.vars[field] = str(getattr(self.algorithm, field))

    def refresh_descentants(self):
        if isinstance(self.viewer.structure, Individual):
            self.descendant_list.tree.delete(*self.descendant_list.tree.get_children())

            for i, individual in enumerate(self.viewer.structure.get_descendants()):
                energy = individual.energy if isinstance(individual, OptimizedIndividual) else nan
                self.descendant_list.insert_item((i, energy),)

