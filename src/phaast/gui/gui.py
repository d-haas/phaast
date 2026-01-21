import tkinter as tk
from tkinter import ttk

from phaast.gui.constants import *
from phaast.gui.menu import MenuBar
from phaast.gui.mol_viewer import MolViewer

from phaast.structure.constants import AtomicNumbers, AtomicRadi

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.setup_window()

        self.setup()

    def run(self):
        self.mainloop()

    def setup_window(self):
        self.title("PHAAST - GUI")
        self.minsize(900,900)
        self.resizable(False, False)
        self.configure(
            background="#1e1e2e",
            menu = MenuBar(self)
        )


    def setup(self):
        self.input_widgets : list[ttk.Button | ttk.Entry] = []
        self.viewer = MolViewer(self)
        self.viewer.animate = 1
        self.viewer.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        for widget in ("TFrame", "TButton", "TMenubutton", "TEntry", "TLabel", "Treeview"):
            self.style.configure(widget, background="#1e1e2e", foreground="#cdd6f4", fieldbackground="#1e1e2e", insertcolor="#cdd6f4")
            self.style.map(widget, background=[("active", "#eff1f5")], foreground=[("active", "#4c4f69")])

        #self.style.configure("phaast.TEntry", background="#1e1e2e", foreground="#cdd6f4")

        upper_frame = ttk.Frame(self)

        for name in ("add", "delete", "replace", "view", "move"):
            button = ttk.Button(
                upper_frame,
                text = f"({name[0].upper()}){name[1:]}",
                command = lambda n=name : setattr(self.viewer, "state", n),
            )
            self.input_widgets.append(button)
            button.pack(side = tk.LEFT, padx = 5)

        self.entry_var = tk.StringVar()
        self.entry_var.trace("w", self.on_entry_change)
        self.label_var = tk.StringVar()

        entry_frame = ttk.Frame(upper_frame)
        label = ttk.Label(entry_frame, textvariable=self.label_var, foreground = "red")
        entry = ttk.Entry(entry_frame, width=5, textvariable = self.entry_var)
        self.input_widgets.append(entry)
        """
        entry = ttk.OptionMenu(
            entry_frame,
            self.entry_var,
            *[
                AtomicSymbols[number]
                for number
                in sorted(list(AtomicSymbols.keys()))
                if number in AtomicRadi
            ]
        )
        """
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.LEFT)
        entry_frame.pack(side = tk.LEFT, padx = 5)

        upper_frame.pack(side = tk.TOP, pady=10)

        ########################
        ### XTB OPTIMIZATION ###
        ########################
        xtb_frame = ttk.Frame(self)
        
        button = ttk.Button(
            xtb_frame,
            text = "Optimize XTB",
            command = lambda : self.viewer.optimize_xtb({k : v.get() for k, v in self.xtb_options.items()}),
        )
        self.input_widgets.append(button)
        button.pack(side=tk.LEFT, padx = 5)

        self.xtb_options : dict[str, tk.IntVar] = {}
        for option, default in (
            ("charge", 0),
            ("etemp", 300),
            ("gfn", 2),
            ("threads", 1),
        ):
            option_frame = ttk.Frame(xtb_frame)
            label = ttk.Label(option_frame, text = option+":")
            self.xtb_options[option] = tk.IntVar(value = default)
            entry = ttk.Entry(option_frame, textvariable = self.xtb_options[option], width=5)
            self.input_widgets.append(entry)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.LEFT)
            option_frame.pack(side=tk.LEFT, padx=5)

        xtb_frame.pack(side = tk.TOP, pady = 10)

        #########################
        ### ORCA OPTIMIZATION ###
        #########################
        orca_frame = ttk.Frame(self)

        button = ttk.Button(
            orca_frame,
            text = "Optimize ORCA",
            command = lambda : self.viewer.optimize_orca({k : v.get() for k, v in self.orca_options.items()}),
        )
        self.input_widgets.append(button)
        button.pack(side=tk.LEFT, padx = 5)

        self.orca_options : dict[str, tk.IntVar | tk.StringVar] = {}
        for option, default in (
            ("functional", "HF"),
            ("basis_set", "STO-3G"),
            ("spin_multiplicity", 0),
            ("charge", 0),
            ("threads", 4),
        ):
            option_frame = ttk.Frame(orca_frame)
            label = ttk.Label(option_frame, text = option.replace("_", " ").capitalize()+":")
            if type(default) == str:
                self.orca_options[option] = tk.StringVar(value = default)
            elif type(default) == int:
                self.orca_options[option] = tk.IntVar(value = default)
            entry = ttk.Entry(option_frame, textvariable = self.orca_options[option], width=10)
            self.input_widgets.append(entry)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.LEFT)
            option_frame.pack(side=tk.LEFT, padx=5)

        orca_frame.pack(side = tk.TOP, pady = 10)

        options_frame = ttk.Frame(self)

        self.quality_var = tk.IntVar(value = 1)
        label = ttk.Label(options_frame, text = "Quality: ")
        quality_scale = ttk.LabeledScale(
            options_frame,
            variable = self.quality_var,
            from_ = 1, to = 8,
        )
        self.quality_var.set(4)
        self.quality_var.trace(
            "w",
            self.on_quality_change,
        )
        label.pack(side = tk.LEFT)
        quality_scale.pack(side = tk.LEFT)

        options_frame.pack(side = tk.TOP)

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

    def on_quality_change(self, *_):
        self.viewer.render_quality = self.quality_var.get()

    def disable_input(self):
        for widget in self.input_widgets:
            widget.configure(state = "disabled")

    def enable_input(self):
        for widget in self.input_widgets:
            widget.configure(state = "normal")

