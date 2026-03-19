import sys
import tkinter as tk 
from tkinter.messagebox import askquestion

from phaast.gui.genetic.genetic_frame import GeneticFrame
from phaast.surface_explorator.genetic import Genetic

class GeneticGUI(tk.Tk):
    genetic_frame : GeneticFrame
    algorithm : Genetic
    def __init__(self, algorithm : Genetic):
        super().__init__()
        self.algorithm = algorithm
        self.window_setup()

    def window_setup(self):
        self.title("P.H.A.A.S.T's Genetic Algorithm")
        self.minsize(1240, 720)
        self.protocol(
            "WM_DELETE_WINDOW",
            self.kill,
        )

    def kill(self):
        if askquestion(
            "Confirmação",
            "Tem certeza que deseja fechar o programa?",
        ) == "yes":
            #self.genetic_frame.kill()
            sys.exit()

    def run(self):
        self.genetic_frame = GeneticFrame(self, self.algorithm)
        self.genetic_frame.pack(fill = tk.BOTH, expand = True)
        self.mainloop()
