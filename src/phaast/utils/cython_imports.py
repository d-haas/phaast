import cython
from typing import Any, Callable, cast, TYPE_CHECKING

from cython.cimports.libc.time import time #type: ignore
from cython.cimports.libc.stdlib import rand, srand, RAND_MAX #type: ignore
type Decorator[**P, R] = Callable[[Callable[P, R]], Callable[P, R]]

### Decorators
noexcept = cast(
    Decorator,
    cython.noexcept, #type: ignore
)
nogil = cast(
    Decorator,
    cython.nogil,
)
cfunc = cast(
    Decorator,
    cython.cfunc,
)
ccall = cast(
    Decorator,
    cython.ccall,
)
cclass = cast(
    Decorator,
    cython.cclass,
)

if TYPE_CHECKING:
    time     : Callable[[cython.pointer[Any]], float]
    rand     : Callable[[], cython.ulong]
    srand    : Callable[[float], None]
    RAND_MAX : int



__all__ = [
    "time",
    "rand",
    "srand",
    "RAND_MAX",
    "noexcept",
    "nogil",
    "cfunc",
    "ccall",
    "cclass",
]
