from enum import Enum
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Literal, Optional, Tuple

class CheckArg(Enum):
    TRUE = True
    FALSE = False
    NONE = None
    CHANGE = "change"

class ScrollList(ttk.Frame):
    def __init__(
        self,
        master : tk.Misc | None = None,
        title : str = "",
        width : tuple[int, ...] | int | None = None,
        selectmode : Literal["extended", "browse", "none"] = "extended",
        select_func : Callable[[tk.Event], None] | None = None,
        check_function : Optional[Callable[[tuple[Any, ...]|Literal[""], CheckArg], bool]] = None,
        *args,
        **kwargs
    ):
        super().__init__(master)
        self.scrollbar = ttk.Scrollbar(self)
        columns = kwargs["columns"] if "columns" in kwargs else ("",)
        display_columns = kwargs["display_columns"] if "display_columns" in kwargs else kwargs["columns"] if "columns" in kwargs  else ("",)
        if check_function:
            columns+= ("check",)
            display_columns+= ("check",)

        self.tree = ttk.Treeview(
            self,
            *args,
            columns = columns,
            displaycolumns = display_columns,
            show = kwargs["show"] if "show" in kwargs else "headings",
            selectmode = selectmode,
        )

        if isinstance(width, int):
            self.tree.column(self.tree["columns"][0], stretch=tk.YES, width=width)
        elif isinstance(width, tuple):
            for i, v in enumerate(width):
                self.tree.column(self.tree["columns"][i], stretch=tk.YES, width=v)

        if title:
            self.tree.heading(self.tree["columns"][0], text = title)

        self.ignore_selection : bool = False
        self.tree.bind("<<TreeviewSelect>>", self.selection_func)
        self.tree.bind("<Button-1>", self.checking_func)
        if selectmode == "extended":
            self.tree.bind("<B1-Motion>", self.on_drag)

        self.select_func = select_func

        self.check_function = check_function

        self.tree.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        self.scrollbar.pack(side = tk.LEFT, fill = tk.Y)

        self.tree.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tree.yview)

        self.last_selection_index : int = 0


    def insert_item(self, value : list | tuple | str = "", **kwargs) -> str:
        if isinstance(value, (list, tuple)):
            row = tuple(value)
        else:
            row = (value,)

        if self.check_function:
            row+= ("✓" if self.check_function(row, CheckArg.NONE) else "x",)

        return self.tree.insert(
            "", tk.END, text="",
            values = row,
            **kwargs,
        )

    def delete_items(self, *items) -> None:
        self.tree.delete(*items)

    def get_selected_item(self) -> str | None:
        selected_items = self.tree.selection()
        if selected_items:
            return selected_items[0]
        else:
            return None

    def get_selected_items(self) -> Tuple[str, ...]:
        return self.tree.selection()

    def get_item_values(self, item : str | int) -> Tuple[Any, ...] | Literal[""]:
        return self.tree.item(item, 'values')

    def clear_selection(self) -> None:
        self.ignore_selection = True
        self.tree.selection_clear()
        self.tree.update()
        self.ignore_selection = False

    def set_selection(self, items : List[str]|Tuple[str,...]|List[int]|Tuple[int]) -> None:
        self.ignore_selection = True

        all_items = self.tree.get_children()

        self.tree.selection_set(items)
        if items:
            self.tree.see(items[0])
            self.last_selection_index = min([all_items.index(item) for item in items])

        self.tree.update()
        self.tree.update_idletasks()

        self.ignore_selection = False

    def selection_func(self, event : tk.Event) -> None:
        if not self.ignore_selection and self.select_func:
            self.select_func(event)

    def checking_func(self, event : tk.Event) -> None:
        if self.check_function:
            clicked_column = self.tree.identify_column(event.x)
            clicked_element = self.tree.identify_element(event.x, event.y)
            if clicked_element == "text" and clicked_column == f"#{len(self.tree['columns'])}":
                clicked_row = self.tree.identify_row(event.y)
                self.check_function(self.get_item_values(clicked_row), CheckArg.CHANGE)

    def on_drag(self, event):
        # Identify the item currently under the mouse
        current_item = self.tree.identify_row(event.y)
        self.tree.selection_add(current_item)
        

    def select_next(self) -> None:
        item = self.get_selected_item()

        all_items = self.tree.get_children()

        if item:
            new_index = self.last_selection_index+1
            new_index = min(len(all_items)-1, new_index)
            self.set_selection((all_items[new_index],),)

        elif all_items:
            self.set_selection((all_items[0],),)


    def select_prev(self) -> None:
        item = self.get_selected_item()

        all_items = self.tree.get_children()

        if item:
            new_index = self.last_selection_index-1
            new_index = max(0, new_index)
            self.set_selection((all_items[new_index],),)

        elif all_items:
            self.set_selection((all_items[0],),)

class ScrollNumberList(ScrollList):
    def __init__(
        self,
        master : tk.Misc | None = None,
        title : str = "",
        width : tuple[int, ...] | int | None = None,
        selectmode : Literal["extended", "browse", "none"] = "extended",
        select_func : Callable[[tk.Event], None] | None = None,
        check_function : Optional[Callable[[tuple[Any, ...]|Literal[""], CheckArg], bool]] = None,
        *args,
        **kwargs
    ):
        super().__init__(master, title, width, selectmode, select_func, check_function, *args, **kwargs)

    def heading(self, column, *args, **kwargs):
        self.tree.heading(column, *args, **kwargs, command = lambda : self.sort_by_column(column))

    def sort_by_column(self, column):
        items = self.tree.get_children()
        rows = [self.get_item_values(item) for item in items]
        self.delete_items(*items)
        column_id : int = self.tree["columns"].index(column)


        rows.sort(key = lambda row : float(row[column_id]))

        for row in rows:
            self.insert_item(row)
