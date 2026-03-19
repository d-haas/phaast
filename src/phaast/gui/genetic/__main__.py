import sys
import tkinter as tk 
from tkinter.messagebox import askquestion

from phaast.gui.genetic.genetic_frame import GeneticFrame
from phaast.gui.genetic.setup_frame import SetupFrame
from phaast.surface_explorator.genetic import Genetic

class MainFrame(tk.Tk):
    setup_frame : SetupFrame
    genetic_frame : GeneticFrame
    def __init__(self):
        super().__init__()
        self.window_setup()
        self.main_setup()


    def window_setup(self):
        self.title("P.H.A.A.S.T's Genetic Algorithm")
        self.minsize(1240, 720)
        self.protocol(
            "WM_DELETE_WINDOW",
            lambda : sys.exit() if askquestion(
                "Confirmação",
                "Tem certeza que deseja fechar o programa?",
            ) == "yes" else None,
        )

    def kill(self):
        if askquestion(
            "Confirmação",
            "Tem certeza que deseja fechar o programa?",
        ) == "yes":
            #self.genetic_frame.kill()
            sys.exit()

    def main_setup(self):
        self.setup_frame = SetupFrame(self)
        self.setup_frame.pack(fill = tk.BOTH, expand = True)

    def goto_genetic(self, genetic : Genetic):
        self.setup_frame.pack_forget()
        self.genetic_frame = GeneticFrame(self, genetic)
        self.genetic_frame.pack(fill = tk.BOTH, expand = True)


    def run(self):
        self.mainloop()

if __name__ == "__main__":
    root = MainFrame()
    root.run()
