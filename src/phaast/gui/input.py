from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phaast.gui.viewer import MolViewer

import sys

class InputHandler:
    def __init__(self, parent : MolViewer):
        self.parent = parent

        self.parent.bind("<Motion>", self.on_mouse_move)
        self.parent.bind("<B1-Motion>", self.on_mouse_drag)
        self.parent.bind("<ButtonPress-1>", self.on_mouse_press)
        self.parent.bind("<ButtonRelease-1>", self.on_mouse_release)

        platform = sys.platform
        if platform.startswith("linux"):
            self.parent.bind("<Button-4>", self.on_scroll)
            self.parent.bind("<Button-5>", self.on_scroll)
        elif platform.startswith("win32") or platform.startswith("cygwin"):
            self.parent.bind("<MouseWheel>", self.on_scroll)
        elif platform.startswith("darwin"):
            self.parent.bind("<MouseWheel>", self.on_scroll)
        else:
            print("Invalid operating system, using any available binds")
            self.parent.bind("<Button-4>", self.on_scroll)
            self.parent.bind("<Button-5>", self.on_scroll)
            self.parent.bind("<MouseWheel>", self.on_scroll)

        self.mouse_presses : list[int] = [0, 0]
        self.mouse_holding : int = 0
        self.mouse_being_pressed : int = 0

        self.mouse_last_pos : tuple[float, float] = (0.0, 0.0)
        self.mouse_pos : tuple[float, float] = (0.0, 0.0)
        self.mouse_motion : tuple[float, float] = (0, 0)

        self.last_mouse_scroll : tuple[float, float] = (0, 0)
        self.mouse_scroll : tuple[float, float] = (0, 0)
        self.scrolled : tuple[float, float] = (0, 0)

        self.mouse_last_click_pos : tuple[float, float] = self.mouse_pos
        self.mouse_clicked : bool = False
        self.mouse_last_release_pos : tuple[float, float] = self.mouse_pos
        self.mouse_released : bool = False

        self.click_cooldown : bool = False


    def scroll_handler(self, _, xoffset, yoffset):
        self.mouse_scroll = (
            self.mouse_scroll[0]+xoffset,
            self.mouse_scroll[1]+yoffset,
        )

    @property
    def mouse_pressed(self) -> int:
        return self.mouse_presses[-1]

    def update_pos(self, event):
        self.mouse_last_pos = self.mouse_pos
        self.mouse_pos = (event.x, event.y)
        self.mouse_motion = (
            self.mouse_pos[0] - self.mouse_last_pos[0],
            self.mouse_pos[1] - self.mouse_last_pos[1],
        )

    def on_mouse_move(self, event):
        self.update_pos(event)
        self.parent.on_move()

    def on_mouse_drag(self, event):
        self.update_pos(event)
        self.parent.on_drag()

    def on_mouse_press(self, event):
        self.mouse_being_pressed = 1
        self.mouse_last_click_pos = (event.x, event.y)
        self.click_cooldown = True
        self.parent.after(997, lambda : setattr(self, "click_cooldown", False))
        self.parent.on_press()

    def on_mouse_release(self, event):
        self.mouse_being_pressed = 0
        self.mouse_last_release_pos = (event.x, event.y)
        click_motion = tuple(
            (
                self.mouse_last_release_pos[i] - self.mouse_last_click_pos[i]
                for i in range(2)
            )
        )

        if self.click_cooldown and sum(click_motion) <= 2:
            if self.parent.hovered:
                self.parent.on_single_click()

        self.parent.on_release()

    def on_scroll(self, event):
        if event.num == 4 or event.delta < 0:
            self.parent.on_scroll( 1)
        if event.num == 5 or event.delta > 0:
            self.parent.on_scroll(-1)

    @property
    def single_clicked(self):
        return self.mouse_released and self.mouse_last_click_pos == self.mouse_last_release_pos
