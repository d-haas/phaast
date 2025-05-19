from types import GenericAlias, UnionType
from typing import Any, Callable, Literal, ParamSpec, TypeVar, get_origin
from inspect import signature, Parameter
from functools import wraps

def check_union(arg, tp : UnionType) -> bool:
    return any((
        check_type(arg, _tp)
        for _tp in tp.__args__
    ))

def check_list(arg, tp : GenericAlias) -> Literal[True]:
    if isinstance(arg, list):
        item_tp = tp.__args__[0]
        for item in arg:
            if not check_type(item, item_tp):
                raise TypeError(
                    f"List item {item} is not of type {item_tp}"
                )

        return True

    else:
        raise TypeError(
            f"Argument {arg} is not a list"
        )

def check_tuple(arg, tp : GenericAlias) -> Literal[True]:
    if isinstance(arg, tuple):
        tp_args = tp.__args__
        if not len(arg) == len(tp_args):
            if len(tp_args) == 2 and tp_args[1] == Ellipsis:
                tp_args = (tp_args[0])*len(arg)
            else:
                raise TypeError(
                    f"Argument length {len(arg)} is not compatible with type length {len(tp.__args__)}"
                )

        for item, item_tp in zip(arg, tp_args):
            if not check_type(item, item_tp):
                raise TypeError(
                    f"Tuple item {item} is not of type {item_tp}"
                )

        return True

    else:
        raise TypeError(
            f"Argument {arg} is not a tuple"
        )

def check_dict(arg, tp : GenericAlias) -> Literal[True]:
    if isinstance(arg, dict):
        key_tp, item_tp = tp.__args__

        for key, item in arg.items():
            if not check_type(key, key_tp):
                raise TypeError(
                    f"Dict key {key} is not of type {key_tp}"
                )
            if not check_type(item, item_tp):
                raise TypeError(
                    f"Dict item {item} is not of type {item_tp}"
                )

        return True

    else:
        raise TypeError(
            f"Argument {arg} is not a dict"
        )


def check_type(arg : Any, tp):
    origin = get_origin(tp)
    # Match-case was giving typehint errors for some reason :P
    if origin:
        if origin is UnionType:
            return check_union(arg, tp)
        elif origin is list:
            return check_list(arg, tp)
        elif origin is tuple:
            return check_tuple(arg, tp)
        elif origin is dict:
            return check_dict(arg, tp)
        else:
            return None
    else:
        return isinstance(arg, tp)

ARGS = ParamSpec("ARGS")
RETURN = TypeVar("RETURN")
def check_types(func: Callable[ARGS, RETURN]) -> Callable[ARGS, RETURN]:
    sig = signature(func)
    params = sig.parameters
    
    @wraps(func)
    def wrapper(*args, **kwargs) -> RETURN:
        # Create a mapping of parameter names to their passed values

        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        for name, value in bound_args.arguments.items():
            param = params[name]

            # Skip if parameter has no type annotation
            if param.annotation is Parameter.empty:
                continue

            # Check the type
            if not check_type(value, param.annotation):
                raise TypeError(
                    f"Argument '{name}' has incorrect type. ",
                    f"Expected {param.annotation}, got {type(value)}",
                )
        
        return func(*args, **kwargs)
    
    return wrapper
