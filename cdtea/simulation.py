"""Module for simulation utilities

"""
import random
import types

import typing

from cdtea import physics, moves
from cdtea.space_time import SpaceTime


class SimulationError(ValueError):
    """Base Error class for simulation related errors"""


def simulate(st: SpaceTime, iters: int, cos_const: float = physics.STEADY_GROWTH_COSMOLOGICAL_CONSTANT, sampling_interval: int = None,
             sampling_funcs: typing.Dict[str, types.FunctionType] = None):
    """Simulate a probabilistic walk in the space of spacetimes

    Args:
        st:
            SpaceTime, the spacetime object
        iters:
            int, num iterations
        cos_const:
            float, default Ln(2)
        sampling_interval:
            int, default None, if specified use this interval for sampling. Every n iterations, call each sampling function and store
            the returned value in a dict
        sampling_funcs:
            dict[str -> function], default None. If specified, each function in the dict will be called at each sampling interval. These
            functions may only take one argument, the SpaceTime instance, and return a scalar.

    Returns:
        Dict, if sampling functions specified, else None
    """
    if (sampling_interval is not None and sampling_funcs is None) or (sampling_interval is None and sampling_funcs is not None):
        raise SimulationError('Must specify neither or both of sampling_interval and sampling_funcs')
    sampling = sampling_interval is not None
    samples = {k: [] for k in sampling_funcs} if sampling else None

    for i in range(iters):
        num_nodes = len(st.nodes)
        chosen_node = st.get_random_node()
        _future = list(chosen_node.future)
        _past = list(chosen_node.past)
        num_future_neighbors = len(_future)
        num_past_neighbors = len(_past)
        chosen_future = random.choice(_future)
        chosen_past = random.choice(_past)

        # Compute Probabilities
        prob_increase = physics.increase_probability(num_nodes, num_future_neighbors, num_past_neighbors, cos_const=cos_const)
        prob_decrease = physics.decrease_probability(num_future_neighbors, num_past_neighbors, cos_const=cos_const)

        # Perform either randomly according to Metropolis algorithm
        if random.random() < prob_increase:
            print('increasing')
            moves.increase(st, chosen_node, chosen_future, chosen_past)

        if random.random() < prob_decrease:
            print('decreasing')
            moves.decrease(st, chosen_node)

        # Optionally sample
        if sampling and (i % sampling_interval == 0):
            print('sampling')
            for k in sampling_funcs:
                samples[k].append(sampling_funcs[k](st))

    if sampling:
        return samples
