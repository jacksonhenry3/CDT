"""Simple script for evaluating performance of CDT code

Checks:
- order of magnitude performance for moves, inverse moves
"""
import collections
import itertools
import random
import time
import types

import typing

import pandas

from cdtea import space_time, moves
from cdtea.space_time import SpaceTime


def key_identity(x):
    return x


def key_spacetime(x):
    return len(x.nodes)


def make_spacetime(size: int):
    return space_time.generate_flat_spacetime(size, size)


def make_moves(st: SpaceTime, n: int):
    cdt = st.copy()  # work on new spacetime
    for i in range(1000):
        n = cdt.get_random_node()
        f = random.choice(list(n.future))
        p = random.choice(list(n.past))
        moves.increase(cdt, n, f, p)


def time_with_inputs(func: types.FunctionType, kwarg_values: typing.Dict[str, typing.List[typing.Any]], kwarg_key_funcs: typing.Dict[str, typing.List[types.FunctionType]] = None):
    keys = list(sorted(kwarg_values.keys()))

    key_funcs_dict = {k: key_identity for k in keys}
    if kwarg_key_funcs is not None:
        key_funcs_dict.update(kwarg_key_funcs)
    results = {}

    value_lists = [kwarg_values[k] for k in keys]
    key_funcs = [key_funcs_dict[k] for k in keys]

    for perm in itertools.product(*value_lists):
        kw = dict(zip(keys, perm))
        key = tuple(f(p) for f, p in zip(key_funcs, perm))
        start = time.perf_counter()
        func(**kw)
        stop = time.perf_counter()
        print('Completed Permutation: {}, Time: {:.4f}'.format(str(key), stop - start))
        results[key] = (start, stop, stop - start)
    return results


def main():
    sizes = [10, 20, 30, 50, 80, 100, 150, 200, 500, 1000]
    spacetimes = [make_spacetime(s) for s in sizes]

    kwarg_values = {
        'n': [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000],
        'st': spacetimes,
    }

    kwarg_key_funcs = {
        'st': key_spacetime
    }

    res = time_with_inputs(make_moves, kwarg_values, kwarg_key_funcs)
    df = pandas.DataFrame(data=[list(k + v) for k, v in sorted(res.items(), key=lambda p: p[0])],
                          columns=list(sorted(kwarg_values.keys())) + ['Start', 'Stop', 'Time'])
    df.to_csv('performance.csv', index=False)


if __name__ == '__main__':
    main()
