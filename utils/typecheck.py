from types import GenericAlias, UnionType
from typing import Any, Callable, Literal, ParamSpec, Sequence, TypeVar, get_origin
import collections.abc
from inspect import signature, Parameter
from functools import wraps

def check_union(arg, tp : UnionType) -> Literal[True]:
    for arg_tp in tp.__args__:
        try:
            check_type(arg, arg_tp)
            return True
        except:
            pass
    
    raise TypeError(
        f"Argument {arg} doesnt fit in union conditions {tp}"
    )


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
        if not hasattr(key_tp, "__hash__"):
            raise TypeError(
                f"Key type {key_tp} is not hashable, therefore can not be used as a dictionary key"
            )

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

def check_iterable(arg : Any, tp) -> Literal[True]:
    if hasattr(arg, "__iter__"):
        item_tp = tp.__args__[0]
        for item in arg:
            if not check_type(item, item_tp):
                raise TypeError(
                    f"Iterable item {item} is not of type {item_tp}"
                )

        return True

    else:
        raise TypeError(
            f"Argument {arg} is not an Iterable"
        )

def check_callable(arg : Any, tp) -> Literal[True]:
    if hasattr(arg, "__call__"):
        if hasattr(tp, "__args__"):
            tp_args = tp.__args__[:-1]
            arg_args = [
                param.annotation
                for param
                in signature(arg).parameters.values()
            ]
            for tp_type, arg_type in zip(tp_args, arg_args):
                if not (tp_type == arg_type):
                    raise TypeError(
                        f"Argument of type {arg_type} is not compatible with type {tp_type}"
                    )
            return True

        else:
            return True

    else:
        raise TypeError(
            f"Argument {arg} is not callable"
        )

def check_sequence(arg : Any, tp) -> Literal[True]:
    if isinstance(arg, Sequence):
        if hasattr(tp, "__args__"):
            tp_type = tp.__args__[0]
            for item in arg:
                if not check_type(item, tp_type):
                    raise TypeError(
                        f"Sequence item {arg} is not of type {tp_type}"
                    )
            return True
        else:
            return True
    else:
        raise TypeError(
            f"Argument {arg} is not a sequence"
        )

def check_type(arg : Any, tp) -> Literal[True]:
    """
    Check the argument type, at runtime even if its a dynamic
    argument like list[float | str]
    """
    # Match-case was giving typehint errors for some reason :P
    # then well maintain if-else, just keep in mind that its a
    # little slower...
    origin = get_origin(tp)
    if origin:
        if origin is UnionType:
            return check_union(arg, tp)
        elif origin is list:
            return check_list(arg, tp)
        elif origin is tuple:
            return check_tuple(arg, tp)
        elif origin is dict:
            return check_dict(arg, tp)
        elif origin is collections.abc.Iterable:
            return check_iterable(arg, tp)
        elif origin is collections.abc.Callable:
            return check_callable(arg, tp)
        elif (origin is collections.abc.Sequence or
             origin is collections.abc.ByteString or
             origin is collections.abc.MutableSequence):
            return check_sequence(arg, tp)
        else:
            raise TypeError(
                f"Type {tp} doesnt fit typecheck possibilities"
            )
    else:
        if isinstance(arg, tp):
            return True
        else:
            raise TypeError(
                f"Argument {arg} is not of type {tp}"
            )

ARGS = ParamSpec("ARGS")
RETURN = TypeVar("RETURN")
def check_types(func: Callable[ARGS, RETURN]) -> Callable[ARGS, RETURN]:
    sig = signature(func)
    params = sig.parameters
    
    @wraps(func)
    def wrapper(*args, **kwargs) -> RETURN:

        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        for name, value in bound_args.arguments.items():
            param = params[name]

            if param.annotation is Parameter.empty:
                continue

            if not check_type(value, param.annotation):
                raise TypeError(
                    f"Argument '{name}' has incorrect type. ",
                    f"Expected {param.annotation}, got {type(value)}",
                )
        
        return func(*args, **kwargs)
    
    return wrapper
