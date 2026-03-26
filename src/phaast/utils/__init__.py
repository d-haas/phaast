from typing import Any, TypedDict
from . import typecheck, custom_iter, c_random

type JsonType = dict[str | int, JsonType] | list[JsonType] | str | int | float | bool | None

class EmptyDict(TypedDict):
    pass

class ObjectData(TypedDict):
    import_path : str
    args        : tuple[Any, ...]
    kwargs      : dict[str, Any]

def is_importable(obj : ObjectData | Any) -> bool:
    if isinstance(obj, dict):
        return all(
            (
                "import_path" in obj,
                "args" in obj,
                "kwargs" in obj,
            )
        )

    else:
        return False

def import_object(data : ObjectData) -> object:
    path_modules = data["import_path"].split(".")

    module = __import__(
        ".".join(path_modules[:-1]),
        fromlist = None,
    )

    args = [
        import_object(arg) if is_importable(arg) else arg
        for arg
        in data["args"]
    ]

    kwargs = {
        key : import_object(arg) if is_importable(arg) else arg
        for key, arg
        in data["kwargs"].items()
    }

    return getattr(module, path_modules[-1])(*args, **kwargs)

__all__ = [
    "typecheck",
    "custom_iter",
    "c_random",
]
