from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phaast.gui.gui import GUI

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from phaast.structure import Structure

class MenuBar(tk.Menu):
    root : GUI
    def __init__(self, master : GUI):
        super().__init__(master)

        self.root = master

        self.file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Files", menu=self.file)

        self.file.add_command(
            label = "Open xyz",
            command = self.open_xyz,
        )
        self.file.add_command(
            label = "Save xyz",
            command = self.save_xyz,
        )

    def open_xyz(self):
        file = filedialog.askopenfile(
            mode = "r",
            filetypes = (
                ("XYZ", "*.xyz"),
            ),
        )

        if not file: return

        try:
            structure = Structure.from_xyz(file.name)
            structure.center_mass()
        except:
            messagebox.showerror(
                title = "Import error",
                message = "xyz structure is not a valid xyz file",
            )
        else:
            self.root.viewer.structure = structure

    def save_xyz(self):
        file = filedialog.asksaveasfile(
            mode="w",
            defaultextension = "xyz",
        )
        if not file: return

        self.root.viewer.structure.to_xyz(file.name)

        


