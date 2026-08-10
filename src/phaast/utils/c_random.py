from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, cast
import cython

srand(time(cython.NULL))

@nogil
@cython.cfunc
@noexcept
def get_rand() -> cython.double:
    cython.declare(
        num = cython.ulong,
        result = cython.double,
    )
    num = rand()

    result = (num * 1.0) / RAND_MAX

    return result

@nogil
@cython.cfunc
@noexcept
def get_randint(a : cython.int, b : cython.int) -> cython.ulong:
    cython.declare(
        num = cython.ulong,
    )
    num = rand()

    return (num % (b - a)) + a

@nogil
@cython.cfunc
@noexcept
def get_rand_uniform(a : cython.double, b : cython.double) -> cython.double:
    return get_rand()*(b - a) + a 
