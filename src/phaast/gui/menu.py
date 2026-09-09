from __future__ import annotations
from typing import TYPE_CHECKING

from phaast.gui.genetic.energy_visualizer import EnergyVisualizer
from phaast.gui.genetic.genetic_frame import GeneticFrame
from phaast.gui.genetic.setup_frame import SetupFrame
from phaast.gui.viewer_window import ViewerWindow
from phaast.surface_explorator.genetic import Genetic
if TYPE_CHECKING:
    from phaast.gui.gui import GUI

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from phaast.structure import Structure
from phaast.gui.viewer import MolViewer

class MenuBar(tk.Menu):
    root : GUI
    def __init__(self, master : GUI):
        super().__init__(
            master,
            foreground = "#cdd6f4",
            background = "#6c7086",
        )

        self.root = master

        self.file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Files", menu=self.file)

        self.file.add_command(
            label = "New Genetic Algorithm",
            command = self.new_genetic,
        )
        self.file.add_command(
            label = "Open Genetic Algorithm",
            command = self.open_genetic,
        )
        self.file.add_command(
            label = "New xyz",
            command = self.new_xyz,
        )
        self.file.add_command(
            label = "Open xyz",
            command = self.open_xyz,
        )

    def create_genetic(self, algorithm : Genetic):
        window = self.root.create_window(w = 720, h = 460)

        genetic_frame = GeneticFrame(
            window.child,
            algorithm = algorithm,
            gui = self.root,
        )

        play_button = tk.Button(
            window.controls.custom_bar,
            text = "▶ Run",
            foreground = "#cdd6f4",
            background="#6c7086",
            activebackground="#6c7086",
            borderwidth = 0,
            relief = tk.FLAT,
            highlightthickness=0,
        )

        play_button.configure(
            command = lambda : (
                setattr(genetic_frame, "is_running", not getattr(genetic_frame, "is_running")),
                play_button.configure(
                    text = "⏸ Pause" if getattr(genetic_frame, "is_running") else "▶ Run",
                ),
            ),
        )

        energy_button = tk.Button(
            window.controls.custom_bar,
            text = "E",
            foreground = "#cdd6f4",
            background="#6c7086",
            activebackground="#6c7086",
            borderwidth = 0,
            relief = tk.FLAT,
            highlightthickness=0,
            command = lambda algorithm=algorithm : self.create_energy_visualizer(algorithm),
        )

        genetic_frame.pack(fill = tk.BOTH, expand = True)
        play_button.pack(side=tk.LEFT)
        energy_button.pack(side=tk.LEFT)


    def new_genetic(self):
        window = self.root.create_window(
            w = 700, h = 430,
        )

        main_frame = tk.Frame(
            window.child,
            background = "#1e1e2e",
        )

        setup_frame = SetupFrame(main_frame)

        create_button = tk.Button(
            main_frame,
            text = "Start genetic algorithm",
            foreground = "#cdd6f4",
            background = "#6c7086",
            activeforeground = "#cdd6f4",
            activebackground = "#6c7086",
            command = lambda : self.create_genetic(setup_frame.get_algorithm()),
        )

        setup_frame.pack(fill = tk.BOTH, expand = True)
        create_button.pack()

        main_frame.pack(fill = tk.BOTH, expand = True)

    def open_genetic(self):
        file = filedialog.askopenfile(
            mode = "r",
            filetypes = (
                ("JSON", "*.json"),
            ),
        )

        if not file: return

        algorithm = Genetic.load(file.name)

        self.create_genetic(algorithm)

    def create_energy_visualizer(self, algorithm : Genetic):
        window = self.root.create_window()

        energy_visualizer = EnergyVisualizer(window.child, algorithm)

        energy_visualizer.pack(fill = tk.BOTH, expand = True)

    def open_viewer(self):
        window = self.root.create_window()

        viewer = MolViewer(window.child)
        viewer.animate = 1
        viewer.pack(
            fill = tk.BOTH,
            expand = True,
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
            window = self.root.create_window(w = 590, h = 340)

            viewer = ViewerWindow(window.child, self.root)
            viewer.structure = structure
            viewer.pack(
                fill = tk.BOTH,
                expand = True,
            )

    def new_xyz(self):
        window = self.root.create_window(w = 590, h = 340)

        viewer = ViewerWindow(window.child, self.root)
        viewer.pack(
            fill = tk.BOTH,
            expand = True,
        )
        


