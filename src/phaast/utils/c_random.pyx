# cython: freethreading_compatible = True
from libc.time cimport time
from libc.stdlib cimport rand, srand, RAND_MAX

srand(time(NULL))

cdef double get_rand() noexcept nogil:
    cdef unsigned long num = rand()

    cdef double result = (num * 1.0) / RAND_MAX

    return result

cdef unsigned long get_randint(int a, int b) noexcept nogil:
    cdef unsigned long num = rand()

    return (num % (b - a)) + a

cdef double get_rand_uniform(double a, double b) noexcept nogil:
    return get_rand()*(b - a) + a 
