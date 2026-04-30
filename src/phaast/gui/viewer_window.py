from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phaast.gui.gui import GUI

import tkinter as tk
from tkinter import filedialog

from phaast.gui.viewer import MolViewer
from phaast.structure.constants import AtomicNumbers, AtomicRadi
from phaast.structure.primitives import Structure


class ViewerOptions(tk.Menu):
    def __init__(self, viewer : MolViewer, window_manager : GUI):
        super().__init__(
            viewer,
            tearoff = 0,
            background = "#11111b",
            foreground = "#cdd6f4",
        )

        self.root = window_manager
        self.viewer = viewer

        self.add_command(
            label   = "Open in new window",
            command = self.new_window_xyz,
        )
        self.add_command(
            label   = "Save",
            command = self.save_xyz,
        )

        viewer.bind(
            "<Button-3>",
            lambda event : (
                self.tk_popup(event.x_root, event.y_root),
                self.grab_release(),
            ),
        )

    def new_window_xyz(self):
        structure = Structure(self.viewer.structure).copy()
        structure.center_mass()

        window = self.root.create_window(w = 590, h = 340)

        new_viewer = ViewerWindow(window.child, self.root)
        new_viewer.structure = structure
        new_viewer.pack(
            fill = tk.BOTH,
            expand = True,
        )

    def save_xyz(self):
        file = filedialog.asksaveasfile(
            mode="w",
            defaultextension = ".xyz",
        )
        if not file: return

        self.viewer.structure.to_xyz(file.name)

class ViewerControls(tk.Frame):
    def __init__(self, master : tk.Misc, viewer : MolViewer):
        super().__init__(
            master,
            background = "#1e1e2e",
        )
        self.viewer = viewer

        upper_frame = tk.Frame(
            self,
            background = "#1e1e2e",
        )

        for name in ("add", "delete", "replace", "view", "move"):
            button = tk.Button(
                upper_frame,
                text = f"({name[0].upper()}){name[1:]}",
                command = lambda n=name : setattr(self.viewer, "state", n),
                foreground = "#cdd6f4",
                background="#6c7086",
                activebackground="#6c7086",
            )
            button.pack(side = tk.LEFT, padx = 5)

        self.entry_var = tk.StringVar()
        self.entry_var.trace("w", self.on_entry_change)
        self.label_var = tk.StringVar()

        entry_frame = tk.Frame(upper_frame)
        label = tk.Label(
            entry_frame,
            textvariable=self.label_var,
            foreground = "#f38ba8",
        )
        entry = tk.Entry(
            entry_frame,
            width=3,
            textvariable = self.entry_var,
        )

        opt_button = tk.Button(
            upper_frame,
            text = "(O)ptimize",
            foreground = "#cdd6f4",
            background="#6c7086",
            activebackground="#6c7086",
            command = lambda : print("Optimization Logic")
        )
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.LEFT)
        entry_frame.pack(side = tk.LEFT, padx = 5)

        opt_button.pack(side = tk.RIGHT)

        upper_frame.pack(side = tk.TOP, pady=10)

    def on_entry_change(self, *_):
        string_var = self.entry_var.get()
        if string_var.isdigit():
            var_int = int(self.entry_var.get())
            if var_int in AtomicRadi:
                self.viewer.chosen_z = var_int

                self.label_var.set(" ")
            else:
                self.label_var.set("*")

        elif string_var and len(string_var) <= 2 and string_var in AtomicNumbers and AtomicNumbers[string_var] in AtomicRadi:
            self.viewer.chosen_z = AtomicNumbers[string_var]

            self.label_var.set(" ")

        else:
            self.label_var.set("*")

class ViewerWindow(tk.Frame):
    def __init__(self, master : tk.Misc, gui : GUI):
        super().__init__(
            master,
        )
        self.viewer = MolViewer(self)
        self.viewer.animate = 1
        self.menu = ViewerOptions(self.viewer, gui)

        self.controls = ViewerControls(self, self.viewer)

        self.viewer.pack(fill = tk.BOTH, expand = True)
        self.controls.pack(fill = tk.X)

    @property
    def structure(self) -> Structure:
        return self.viewer.structure

    @structure.setter
    def structure(self, structure : Structure):
        self.viewer.structure = structure
