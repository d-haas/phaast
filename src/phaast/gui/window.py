from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phaast.gui.gui import GUI

import tkinter as tk

import uuid


WINDOW_BORDER = 3
class Window(tk.Frame):
    controls : WindowControls
    child    : SubWindow
    gui      : GUI
    id       : str
    w        : int
    h        : int

    def __init__(self, master : GUI, id : str, w : int, h : int):
        super().__init__(
            master,
            background="#6c7086",
        )


        self.gui = master
        self.id = id
        self.min_width = w
        self.min_height = h
        self.pack_propagate()

        self.controls = WindowControls(self)
        self.controls.pack(
            side = tk.TOP,
            padx = 2,
            pady = (2, 1),
            anchor=tk.W,
            #fill = tk.X,
            expand = False,
        )

        self.child = SubWindow(self)
        self.child.pack(
            side = tk.TOP,
            pady = (1, WINDOW_BORDER),
            padx = WINDOW_BORDER,
            fill = tk.BOTH,
            expand = True
        )

        self.bind("<Motion>", self.move)
        self.bind("<Enter>", lambda _ : setattr(self.gui, "last_w", self.id))
        self.bind("<Leave>", lambda _ : self.gui.configure(cursor = ""))
        self.bind("<Button-1>", self.click)

    @property
    def l(self):
        return self.winfo_x()

    @property
    def r(self):
        return self.l + self.winfo_width()

    @property
    def t(self):
        return self.winfo_y()

    @property
    def b(self):
        return self.t + self.winfo_height()

    def kill(self):
        chosen_id : str | None = None
        for id, window in self.gui.windows.items():
            if window is self:
                chosen_id = id

        if chosen_id:
            del self.gui.windows[chosen_id]

        self.destroy()

    def move(self, event : tk.Event):
        l_corner = event.x <= WINDOW_BORDER
        r_corner = event.x >= self.winfo_width() - WINDOW_BORDER

        t_corner = event.y <= WINDOW_BORDER
        b_corner = event.y >= self.winfo_height() - WINDOW_BORDER

        h_action = "l" if l_corner else "r" if r_corner else ""
        v_action = "t" if t_corner else "b" if b_corner else ""
        action = h_action + v_action
        if not action: action = "move"

        match action:
            case "lt":
                cursor = "top_left_corner"
            case "lb":
                cursor = "bottom_left_corner"
            case "rt":
                cursor = "top_right_corner"
            case "rb":
                cursor = "bottom_right_corner"
            case "l" | "r":
                cursor = "sb_h_double_arrow"
            case "t" | "b":
                cursor = "sb_v_double_arrow"
            case _:
                cursor = ""

        self.gui.configure(cursor = cursor)

    def click(self, event : tk.Event):
        self.gui.last_id     = self.id
        self.gui.last_wclick = (event.x_root, event.y_root)
        self.gui.last_wpos   = (self.winfo_x(), self.winfo_y())
        self.gui.last_wsize  = (self.winfo_width(), self.winfo_height())

        l_corner = event.x <= WINDOW_BORDER
        r_corner = event.x >= self.winfo_width() - WINDOW_BORDER

        t_corner = event.y <= WINDOW_BORDER
        b_corner = event.y >= self.winfo_height() - WINDOW_BORDER

        h_action = "l" if l_corner else "r" if r_corner else ""
        v_action = "t" if t_corner else "b" if b_corner else ""
        action = h_action + v_action
        if not action:
            action = "move"

        match action:
            case "lt":
                cursor = "top_left_corner"
            case "lb":
                cursor = "bottom_left_corner"
            case "rt":
                cursor = "top_right_corner"
            case "rb":
                cursor = "bottom_right_corner"
            case "l" | "r":
                cursor = "sb_h_double_arrow"
            case "t" | "b":
                cursor = "sb_v_double_arrow"
            case _:
                cursor = "fleur"

        self.gui.last_wcursor = cursor
        self.gui.configure(cursor = cursor)
        self.gui.last_waction = action

class WindowControls(tk.Frame):
    def __init__(self, master : Window):
        super().__init__(
            master,
            background="#6c7086",
        )

        self.close_button = tk.Button(
            self,
            text = "⬤",
            command = lambda : master.kill(),
            foreground = "#f38ba8",
            background="#6c7086",
            activebackground="#6c7086",
            borderwidth = 0,
            relief = tk.FLAT,
            highlightthickness=0,
        )
        self.maximize_button = tk.Button(
            self,
            text = "⬤",
            command = lambda : print("Maximize!!"),
            foreground = "#a6e3a1",
            background="#6c7086",
            activebackground="#6c7086",
            borderwidth = 0,
            relief = tk.FLAT,
            highlightthickness=0,
        )
        self.minimize_button = tk.Button(
            self,
            text = "⬤",
            command = lambda : print("Minimize!!"),
            foreground = "#f9e2af",
            background="#6c7086",
            activebackground="#6c7086",
            borderwidth = 0,
            relief = tk.FLAT,
            highlightthickness=0,
        )

        self.custom_bar = tk.Frame(
            self,
            background="#6c7086",
        )

        self.close_button.pack(    side = tk.LEFT, padx = (0, 2) )
        self.maximize_button.pack( side = tk.LEFT, padx = (2, 2) )
        self.minimize_button.pack( side = tk.LEFT, padx = (2, 0) )

        self.custom_bar.pack( side = tk.RIGHT )

class SubWindow(tk.Frame):
    def __init__(self, master : Window):
        super().__init__(
            master,
            background="#6c7086",
        )

def create_new_window(master : GUI, w, h) -> tuple[str, Window]:
    id = uuid.uuid4().hex
    return id, Window(master, id, w, h)
