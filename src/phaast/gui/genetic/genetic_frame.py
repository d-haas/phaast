from __future__ import annotations
import enum
import threading
import time
from typing import TYPE_CHECKING, Callable, Iterable, NamedTuple, cast

import tkinter as tk

from phaast.structure import Structure
from phaast.structure.primitives import Atom
from phaast.surface_explorator.genetic.individual import ChildIndividual, Individual, MutantIndividual, OptimizedIndividual
from phaast.surface_explorator.genetic import Genetic
from phaast.gui.viewer import MolViewer
from phaast.gui.utils import TkDict
from phaast.vector import Vector

class SortingType(enum.Enum):
    ID = 0
    ENERGY = 1

class SortingOrder(enum.Enum):
    NORMAL = 0
    REVERSE = 1

class Sorting(NamedTuple):
    type  : SortingType
    order : SortingOrder

class CommandList(tk.Frame):

    def __init__(self, master : GeneticFrame, struct : None | Individual = None, *args, **kwargs):
        super().__init__(
            master,
            background = "#1e1e2e",
            *args,
            **kwargs,
        )
        self.parent = master

        self.struct = struct

        self.title    = tk.Label(
            self,
            text = "",
            background = "#1e1e2e",
            foreground = "#cdd6f4",
        )
        self.ancestor = tk.Button(
            self,
            text = "Ancestor",
            command = self.change_to_ancestor,
            background = "#1e1e2e",
            foreground = "#cdd6f4",
        )
        self.parent_a = tk.Button(
            self,
            text = "Parent (Mother)",
            command = self.change_to_parent_a,
            background = "#1e1e2e",
            foreground = "#cdd6f4",
        )
        self.parent_b = tk.Button(
            self,
            text = "Parent (Father)",
            command = self.change_to_parent_b,
            background = "#1e1e2e",
            foreground = "#cdd6f4",
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


INFO_COL_NUM = 4
class InfoList(tk.Frame):

    def __init__(self, master : tk.Misc, *args, **kwargs):
        super().__init__(
            master,
            background = "#1e1e2e",
            *args,
            **kwargs,
        )

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
            temp_label = tk.Label(
                self,
                text = (name+": ").rjust(20),
                width = 20,
                background = "#1e1e2e",
                foreground = "#cdd6f4",
            )
            temp_value = tk.Label(
                self,
                textvariable = temp_var,
                width = 5,
                background = "#1e1e2e",
                foreground = "#cdd6f4",
            )

            self.vars[field] = temp_var
            
            temp_label.grid(
                column = (i%INFO_COL_NUM) * 2,
                row = i//INFO_COL_NUM,
                sticky = tk.EW,
            )
            temp_value.grid(
                column = ((i%INFO_COL_NUM) * 2) + 1,
                row = i//INFO_COL_NUM,
                sticky = tk.EW,
            )

class IndividualList(tk.LabelFrame):
    def __init__(
        self,
        master : tk.Misc,
        algorithm : Genetic,
        select_func : Callable[[tk.Event], None],
        *args,
        **kwargs,
    ):
        super().__init__(
            master,
            background = "#1e1e2e",
            foreground = "#cdd6f4",
            *args,
            **kwargs,
        )
        self.list = tk.Listbox(
            self,
            width = 25,
            border = 0,
            selectmode = tk.BROWSE,
            background = "#1e1e2e",
            foreground = "#cdd6f4",
            highlightthickness = 0,
        )
        self.algorithm = algorithm
        self.list.bind("<<ListboxSelect>>", select_func)

        self.list.pack(fill = tk.BOTH, expand = True)

    def append(
        self,
        inds : Individual | Iterable[Individual | OptimizedIndividual] | OptimizedIndividual,
    ):
        if isinstance(inds, (list, tuple)):
            if TYPE_CHECKING:
                inds = cast(tuple[OptimizedIndividual, ...], inds)

            self.list.insert(
                tk.END,
                *[
                    f"{str(ind.id).ljust(7)} : {ind.energy}"  
                    for ind in inds
                ],
            )
        else:
            if TYPE_CHECKING:
                inds = cast(OptimizedIndividual, inds)

            self.list.insert(
                tk.END,
                f"{str(inds.id).ljust(7)} : {inds.energy}"  
            )

    def get(self, first : str | int, last : str | int | None = None) -> list[tuple[int, float]]:
        items = self.list.get(first, last)
        if isinstance(items, str): items = (items,)
        inds = []
        for item in items:
            line = str(item).split(":")
            inds.append(
                (
                    int( line[0] ),
                    float( line[1] ),
                )
            )

        return inds

    def get_ind(self, item : tuple[int, float]) -> Individual:
        return self.algorithm.population_ids[item[0]]

    def get_inds(self, items : list[tuple[int, float]]) -> list[Individual]:
        return [
            self.algorithm.population_ids[item[0]]
            for item in items
        ]

    def selected_ind(self) -> Individual | None:
        selected = self.list.curselection()
        if selected:
            return self.get_ind(
                self.get(selected[0])[0]
            )
        else:
            return None

class GenerationList(tk.LabelFrame):
    def __init__(
        self,
        master : tk.Misc,
        algorithm : Genetic,
        select_func : Callable[[tk.Event], None],
        *args,
        **kwargs,
    ):
        super().__init__(
            master,
            background = "#1e1e2e",
            foreground = "#cdd6f4",
            *args,
            **kwargs,
        )
        self.list = tk.Listbox(
            self,
            width = 4,
            border = 0,
            selectmode = tk.BROWSE,
            background = "#1e1e2e",
            foreground = "#cdd6f4",
            highlightthickness = 0,
        )
        self.algorithm = algorithm
        self.list.bind("<<ListboxSelect>>", select_func)

        self.list.pack(fill = tk.BOTH, expand = True)

    def refresh(self):
        selected = self.list.curselection()
        self.list.delete(0, tk.END)
        self.list.insert(
            tk.END,
            *range(
                len(
                    self.algorithm.generations
                ),
            ),
        )
        if selected:
            self.list.selection_set(selected[0])

    def selected(self) -> int | None:
        selection = self.list.curselection()
        if selection:
            return int(self.list.get(selection[0]))
        else:
            return None

class PopulationList(IndividualList):
    def __init__(self, master : tk.Misc, algorithm : Genetic, *args, **kwargs):
        super().__init__(master, algorithm, *args, **kwargs)

    def refresh(self, generation : int):
        self.list.delete(0, tk.END)
        self.append(
            sorted(
                self.algorithm.generations[generation],
                key = lambda ind : (ind.energy, ind.id),
            ),
        )

class DescendantList(IndividualList):
    def __init__(self, master : tk.Misc, algorithm : Genetic, *args, **kwargs):
        super().__init__(master, algorithm, *args, **kwargs)

    def refresh(self, ind : Individual):
        self.list.delete(0, tk.END)
        self.append(
            [
                self.algorithm.population_ids[id]
                for id in ind.descendants
            ],
        )

class GeneticFrame(tk.Frame):

    algorithm : Genetic
    is_running : bool
    has_ended : bool

    def __init__(self, master : tk.Misc, algorithm : Genetic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.algorithm = algorithm
        self.is_running = False
        self.has_ended = False

        self.selected_generation : int = 0
        self.selected_individual : Individual = Individual(
            [Atom(1, Vector(0, 0, 0))],
            0,
        )

        self.viewer = MolViewer(self)
        self.viewer.animate = 1
        self.generation_list = GenerationList(
            self,
            algorithm = self.algorithm,
            select_func = self.on_select_generation,
            text = "Generations",
        )

        self.population_list = PopulationList(
            self,
            algorithm = self.algorithm,
            text = "Population",
            select_func = self.on_select_individual,
        )
        self.descendant_list = DescendantList(
            self,
            algorithm = self.algorithm,
            text = "Descentants",
            select_func = self.on_select_descendant,
        )

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

        self.kill = False
        self.genetic_loop_thread = threading.Thread(target = self.genetic_loop)
        self.genetic_loop_thread.start()
        self.loop_thread = threading.Thread(target = self.loop)
        self.loop_thread.start()

        self.history : list[Structure] = []
        self.future : list[Structure] = []
        self.bind("<Control-z>", self.reverse_history)
        self.bind("<Control-y>", self.forward_history)

        self.refresh()


    def on_select_generation(self, _ : tk.Event):
        selected_item = self.generation_list.selected()
        if selected_item:
            self.selected_generation = selected_item
            self.population_list.refresh(self.selected_generation)

    def on_select_individual(self, _ : tk.Event):
        selected_ind = self.population_list.selected_ind()
        if selected_ind:
            self.change_individual(selected_ind)

    def on_select_descendant(self, _ : tk.Event):
        selected_ind = self.descendant_list.selected_ind()
        if selected_ind and isinstance(self.viewer.structure, Individual):
            self.change_individual(selected_ind)

    def change_individual(self, individual : Individual):
        self.add_to_history(self.viewer.structure)
        self.viewer.structure = individual
        self.selected_individual = individual
        self.descendant_list.refresh(self.selected_individual)
        self.command_list.refresh()

    def add_to_history(self, struct : Structure):
        self.history.append(struct)
        self.future.clear()

    def reverse_history(self, _ : tk.Event):
        if self.history:
            self.future.append(self.viewer.structure)
            self.viewer.structure = self.history.pop(-1)
            self.descendant_list.refresh(self.selected_individual)
            self.command_list.refresh()

    def forward_history(self, _ : tk.Event):
        if self.future:
            self.history.append(self.viewer.structure)
            self.viewer.structure = self.future.pop(-1)
            self.descendant_list.refresh(self.selected_individual)
            self.command_list.refresh()

    def loop(self):
        while not self.kill:
            self.refresh_statistics()

            for _ in range(10):
                time.sleep(0.0997)
                if self.kill:
                    break

    def genetic_loop(self):
        while not self.kill:
            if self.is_running and (not self.has_ended):
                result = self.algorithm.loop()
                self.soft_refresh()
                if not result:
                    self.has_ended = True
            else:
                for _ in range(10):
                    time.sleep(0.0997)
                    if self.kill:
                        break

    def soft_refresh(self):
        self.generation_list.refresh()
        self.refresh_statistics()

    def refresh(self):
        self.generation_list.refresh()
        self.population_list.refresh(self.selected_generation)
        self.refresh_statistics()

    def refresh_statistics(self):
        for field in self.info_list.fields:
            self.info_list.vars[field] = str(getattr(self.algorithm, field))

    def destroy(self):
        self.kill = True
        super().destroy()
