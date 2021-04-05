"""This module contains observables on a given SpaceTime. Here, observable is defined
to be a function of the SpaceTime, that typically returns a scalar, though there are
some exceptions, like volume profiles.
"""

import numpy
from cdtea import space_time


def volume_profile(st: space_time.SpaceTime) -> numpy.ndarray:
    """Compute the volume profile

    Args:
        st:
            SpaceTime,

    Returns:
        Array[int]
    """
    layers = st.get_layers()
    volumes = [len(nodes) for layer_num, nodes in sorted(layers.items(), key=lambda x: x[0])]
    return numpy.array(volumes)
