import tkinter as tk

from phaast.gui.menu import MenuBar
from phaast.gui.window import Window, create_new_window

class GUI(tk.Tk):
    menu : MenuBar
    windows : dict[str, Window]

    def __init__(self):
        super().__init__()
        self.menu = MenuBar(self)
        self.windows = {}

        self.last_id : None | str = None
        self.last_wclick : tuple[int, int] = (0, 0)
        self.last_wpos   : tuple[int, int] = (0, 0)
        self.last_wsize  : tuple[int, int] = (0, 0)
        self.last_wcursor : str = "arrow"
        self.last_waction : str = ""

        self.setup()

    def setup(self):
        self.title("PHAAST - GUI")
        self.minsize(600,400)
        self.configure(
            background="#1e1e2e",
            menu = self.menu,
        )

        self.bind("<B1-Motion>", self.on_click_motion)
        self.bind(
            "<ButtonRelease-1>",
            lambda _ : (
                setattr(self, "last_id", None),
                self.configure(cursor = ""),
            ),
        )

    @property
    def selected_window(self):
        if self.last_id:
            return self.windows[self.last_id]
        else:
            return None

    def create_window(self, w = 300, h = 340) -> Window:
        id, window = create_new_window(self, w, h)
        self.windows[id] = window
        window.place(
            anchor = tk.NW,
            width = w,
            height = h,
        )

        return window

    def on_click_motion(self, event : tk.Event):
        if self.last_id:
            window = self.windows[self.last_id]
            x, y = event.x_root, event.y_root
            w, h = self.last_wsize
            dx, dy = (x - self.last_wclick[0], y - self.last_wclick[1])
            pos_x, pos_y = self.last_wpos
            if self.last_waction == "move":
                window.place_configure(
                    x = pos_x + dx,
                    y = pos_y + dy,
                    width = w,
                    height = h,
                )
                window.lift()
            
            else:
                new_x = pos_x
                new_y = pos_y
                new_w = w
                new_h = h
                if "t" in self.last_waction:
                    # Limit window height to a defined minimum
                    if h - dy < window.min_height:
                        dy = h - window.min_height

                    new_y = pos_y + dy
                    new_h = h - dy
                elif "b" in self.last_waction:
                    # Limit window height to a defined minimum
                    if h + dy < window.min_height:
                        dy = window.min_height - h

                    new_h = h + dy

                if "l" in self.last_waction:
                    # Limit window width to a defined minimum
                    if w - dx < window.min_width:
                        dx = w - window.min_width

                    new_x = pos_x + dx
                    new_w = w - dx
                elif "r" in self.last_waction:
                    # Limit window width to a defined minimum
                    if w + dx < window.min_width:
                        dx = window.min_width - w

                    new_w = w + dx

                #print(f"SIZE: ({new_w}, {new_h})")
                window.place_configure(
                    x = new_x,
                    y = new_y,
                    width = new_w,
                    height = new_h,
                )
                window.lift()


    def run(self):
        self.mainloop()
