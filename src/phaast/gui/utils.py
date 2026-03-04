from typing import Any
import tkinter as tk

class TkDict(dict[str, tk.Variable]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key : str) -> Any:
        return super().__getitem__(key).get()

    def __setitem__(self, key : str, value : Any):
        if isinstance(value, tk.Variable):
            super().__setitem__(key, value)
        else:
            super().__getitem__(key).set(value)

    def __getattribute__(self, name : str) -> Any:
        return super().__getitem__(name).get()
