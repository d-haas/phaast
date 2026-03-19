from typing import TypedDict
from . import typecheck, custom_iter, c_random

type JsonType = dict[str, JsonType] | list[JsonType] | str | int | float | bool | None

class EmptyDict(TypedDict):
    pass

__all__ = [
    "typecheck",
    "custom_iter",
    "c_random",
]
