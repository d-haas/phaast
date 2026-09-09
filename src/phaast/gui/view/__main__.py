from __future__ import annotations
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from phaast.structure.primitives import Atom, Structure
from phaast.gui.viewer import MolViewer
from phaast.gui.viewer_window import ViewerControls

class ViewerMenu(tk.Menu):
    def __init__(self, master : tk.Misc, viewer : ViewerWindow):
        super().__init__(
            master,
            foreground = "#cdd6f4",
            background = "#6c7086",
        )
        self.viewer = viewer

        self.root = master

        self.file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Files", menu=self.file)

        self.file.add_command(
            label = "New xyz",
            command = self.new_xyz,
        )
        self.file.add_command(
            label = "Open xyz",
            command = self.open_xyz,
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
            self.viewer.structure = structure

    def new_xyz(self):
        structure = Structure([Atom(1)])
        self.viewer.structure = structure

class ViewerWindow(tk.Frame):
    def __init__(self, master : tk.Misc):
        super().__init__(
            master,
        )
        self.viewer = MolViewer(self)
        self.viewer.animate = 1

        self.controls = ViewerControls(self, self.viewer)

        self.viewer.pack(fill = tk.BOTH, expand = True)
        self.controls.pack(fill = tk.X)

    @property
    def structure(self) -> Structure:
        return self.viewer.structure

    @structure.setter
    def structure(self, structure : Structure):
        self.viewer.structure = structure

def main():
    os.environ["PYOPENGL_PLATFORM"] = "glut"
    root = tk.Tk()
    root.title("PHAAST - VIEWER")
    root.minsize(600,400)
    root.configure(
        background="#1e1e2e",
    )

    viewer = ViewerWindow(root)
    viewer.pack(
        fill = tk.BOTH,
        expand = True,
    )

    root.config(menu = ViewerMenu(root, viewer))
    root.mainloop()

if __name__ == "__main__":
    main()
