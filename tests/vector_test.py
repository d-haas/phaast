import random

import phaast.structure.test_vec

from phaast.vector import Vector


def test_operations():
    ta = tuple(((random.random()-.5)*10 for _ in range(3)))
    tb = tuple(((random.random()-.5)*10 for _ in range(3)))

    va = Vector(*ta)
    vb = Vector(*tb)

    ### MOD ###
    _ = va.mod + vb.mod

    ###########
    ### SUB ###
    ###########
    v_sub = tuple(va-vb)
    t_sub = tuple((ta[i]-tb[i] for i in range(3)))
    assert v_sub == t_sub, f"Vector sub is wrong, should be {t_sub}, it's actually {v_sub}"

def test_sum():
    ta = tuple(((random.random()-.5)*10 for _ in range(3)))
    tb = tuple(((random.random()-.5)*10 for _ in range(3)))

    va = Vector(*ta)
    vb = Vector(*tb)

    ### SUM
    v_sum = tuple(va+vb)
    t_sum = tuple((ta[i]+tb[i] for i in range(3)))
    assert v_sum == t_sum, f"Vector sum is wrong, should be {t_sum}, it's actually {v_sum}"
