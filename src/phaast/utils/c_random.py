# cython: freethreading_compatible = True
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    time : Callable[[Any], cython.long] = lambda _: 0
    RANDMAX : cython.long = 0
    rand : Callable[[], cython.long] = lambda : 0
    srand : Callable[[cython.long], None] = lambda _: None

import cython
from cython.cimports.libc.time import time #type: ignore
from cython.cimports.libc.stdlib import srand, rand, RAND_MAX #type: ignore


srand(time(cython.NULL))

@cython.nogil
@cython.cfunc
@cython.exceptval(check=False)
def get_rand() -> cython.double:
    cython.declare(
        num = cython.ulong,
        result = cython.double,
    )
    num = rand()

    result = (num * 1.0) / RAND_MAX

    return result

@cython.nogil
@cython.cfunc
@cython.exceptval(check=False)
def get_randint(a : cython.int, b : cython.int) -> cython.ulong:
    cython.declare(
        num = cython.ulong,
    )
    num = rand()

    return (num % (b - a)) + a

@cython.nogil
@cython.cfunc
@cython.exceptval(check=False)
def get_rand_uniform(a : cython.double, b : cython.double) -> cython.double:
    return get_rand()*(b - a) + a 
