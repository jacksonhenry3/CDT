"""Module for computing physical quantities of interest

References:
    [1] J. Ambjorn, A. Goerlich, J. Jurkiewicz, and R. Loll, Nonperturbative Quantum Gravity, Physics Reports 519, 127 (2012).
    [2] N. S. Israel and J. F. Lindner, Quantum Gravity on a Laptop: 1+1 Dimensional Causal Dynamical Triangulation Simulation, Results in Physics 2, 164 (2012).
"""

import numpy

STEADY_GROWTH_COSMOLOGICAL_CONSTANT = numpy.log(2)


def increase_probability(num_nodes: int, num_future_init: int, num_past_init: int, cos_const: float = STEADY_GROWTH_COSMOLOGICAL_CONSTANT) -> float:
    """Compute the probability of accepting an increase move, this (arbitrary) form of the probability is
    borrowed from [2].

    Args:
        num_nodes:
            int, total number of nodes in the CDT prior to the move
        num_future_init:
            int, number of future edges the randomly chosen node had prior to the move
        num_past_init:
            int, number of past edges the randomly chosen node had prior to the move
        cos_const:
            float, cosmological constant

    Returns:
        float, probability of performing the increase move
    """
    volume_factor = (num_nodes / (num_nodes + 1))
    curvature_factor = num_future_init * num_past_init / (num_future_init + num_past_init + 2)
    boltzmann_factor = numpy.exp(-cos_const)
    return volume_factor * curvature_factor * boltzmann_factor


def decrease_probability(num_future_init: int, num_past_init: int, cos_const: float = STEADY_GROWTH_COSMOLOGICAL_CONSTANT) -> float:
    """Compute the probability of accepting a decrease move, this (arbitrary) form of the probability is
    borrowed from [2].

    Args:
        num_future_init:
            int, number of future edges the randomly chosen node had prior to the move
        num_past_init:
            int, number of past edges the randomly chosen node had prior to the move
        cos_const:
            float, cosmological constant

    Returns:
        float, probability of performing the decrease move
    """
    volume_factor = 1
    curvature_factor = 1 / (num_future_init + num_past_init + 2)
    boltzmann_factor = numpy.exp(cos_const)
    return volume_factor * curvature_factor * boltzmann_factor
