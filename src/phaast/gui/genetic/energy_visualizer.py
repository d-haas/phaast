from __future__ import annotations

import threading
import time
import tkinter as tk

from phaast.surface_explorator.genetic import Genetic

HUD_PAD_DOWN  = 23
HUD_PAD_LEFT  = 91
HUD_PAD_RIGHT = 5
HUD_PAD_UP    = 7

LINE_COLORS = [
    "#f38ba8",
    "#fab387",
    "#f9e2af",
    "#a6e3a1",
    "#89dceb",
    "#89b4fa",
    "#cba6f7",
]

class Plotter(tk.Canvas):
    def __init__(self, master : EnergyVisualizer):
        super().__init__(
            master,
            background = "#1e1e2e",
        )
        self.root = master
        self.bind("<Configure>", self.on_resize)

        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()

    def on_resize(self, event : tk.Event):
        #ws, hs = event.width/self.width, event.height/self.height

        self.width = event.width
        self.height = event.height
        self.config(width=event.width, height=event.height)
        self.root.draw_all()

        #self.scale("all",0,0,ws,hs)

class EnergyVisualizer(tk.Frame):
    def __init__(self, master : tk.Misc, algorithm : Genetic):
        super().__init__(master)

        self.algorithm = algorithm

        self.canvas = Plotter(
            self,
        )
        self.canvas.pack(fill = tk.BOTH, expand = True)

        self.last_values = []
        self.last_size = (self.width, self.height)

        self.kill = False
        self.update_loop = threading.Thread(target = self.visualizer_loop)
        self.update_loop.start()

    @property
    def width(self):
        return self.canvas.width

    @property
    def height(self):
        return self.canvas.height

    def visualizer_loop(self):
        while not self.kill:
            if self.algorithm.best_energy_history != self.last_values:
                self.draw_all()
                self.last_values = self.algorithm.best_energy_history

            for _ in range(10):
                time.sleep(0.0997)
                if self.kill:
                    break

    def draw_all(self, _ : tk.Event | None = None):
        self.canvas.delete(tk.ALL)
        self.back_hud()
        self.plot()
        self.front_hud()

    def back_hud(self):
        gen_spacing = (self.width - HUD_PAD_LEFT - HUD_PAD_RIGHT)/len(self.algorithm.best_energy_history)
        for i in range(len(self.algorithm.best_energy_history)):
            self.canvas.create_line(
                HUD_PAD_LEFT + i*gen_spacing,
                self.height - HUD_PAD_DOWN,
                HUD_PAD_LEFT + i*gen_spacing,
                HUD_PAD_UP,
                fill = "#313244",
                width = 2,
            )

    def front_hud(self):
        self.canvas.create_line(
            HUD_PAD_LEFT, HUD_PAD_UP,
            HUD_PAD_LEFT, self.height - HUD_PAD_DOWN,
            fill = "#cdd6f4",
            width = 2,
        )

        self.canvas.create_line(
            HUD_PAD_LEFT              , self.height - HUD_PAD_DOWN,
            self.width - HUD_PAD_RIGHT, self.height - HUD_PAD_DOWN,
            fill = "#cdd6f4",
            width = 2,
        )

        self.canvas.create_text(
            HUD_PAD_LEFT, HUD_PAD_UP,
            text = max([pop[-1] for pop in self.algorithm.best_energy_history]),
            anchor = tk.E,
            fill = "#cdd6f4",
        )

        self.canvas.create_text(
            HUD_PAD_LEFT, self.height - HUD_PAD_DOWN,
            text = min([pop[ 0] for pop in self.algorithm.best_energy_history]),
            anchor = tk.E,
            fill = "#cdd6f4",
        )

        gen_spacing = (self.width - HUD_PAD_LEFT - HUD_PAD_RIGHT)/len(self.algorithm.best_energy_history)
        for i in range(len(self.algorithm.best_energy_history)):
            self.canvas.create_text(
                HUD_PAD_LEFT + i*gen_spacing,
                self.height - HUD_PAD_DOWN,
                text = i,
                anchor = tk.N,
                fill = "#cdd6f4",
            )

    def plot(self):
        max_energy = max([pop[-1] for pop in self.algorithm.best_energy_history])
        min_energy = min([pop[ 0] for pop in self.algorithm.best_energy_history])
        gen_spacing = (self.width - HUD_PAD_LEFT - HUD_PAD_RIGHT)/len(self.algorithm.best_energy_history)
        min_height = self.height - HUD_PAD_DOWN
        max_height = HUD_PAD_UP

        for i in range(len(self.algorithm.best_energy_history)-1):
            for j in range(len(self.algorithm.best_energy_history[i])):
                self.canvas.create_line(
                    HUD_PAD_LEFT +  i    * gen_spacing,
                    min_height + (max_height - min_height)*(self.algorithm.best_energy_history[i  ][j] - min_energy)/(max_energy - min_energy),
                    HUD_PAD_LEFT + (i+1) * gen_spacing,
                    min_height + (max_height - min_height)*(self.algorithm.best_energy_history[i+1][j] - min_energy)/(max_energy - min_energy),
                    fill = LINE_COLORS[j % len(LINE_COLORS)],
                    width = 2,
                )

    def destroy(self):
        self.kill = True
        super().destroy()
