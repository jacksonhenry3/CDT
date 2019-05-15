import numpy as np
from node import node
from space_time import space_time


def make_flat_spacetime(n_space_slices, n_time_slices):
    """docstring"""

    fst = space_time(np.full(n_time_slices, n_space_slices), n_time_slices)

    # add all nodes

    for t_index in range(n_time_slices):
        for x_index in range(n_space_slices):
            n = node(fst, x_index, t_index)
            fst.nodes[n.index] = n

    # connect spatial nodes

    for node1 in fst.nodes.values():
        x = node1.space_index
        t = node1.time_index
        next_space_index = np.mod(x + 1, fst.space_slice_sizes[t])
        prev_space_index = np.mod(x - 1, fst.space_slice_sizes[t])
        next_time_index = np.mod(t + 1, fst.num_time_slices)
        past_time_index = np.mod(t - 1, fst.num_time_slices)

        node1.right = fst.get_node(next_space_index, t)
        node1.left = fst.get_node(prev_space_index, t)

        n = fst.get_node(x, next_time_index)
        node1.future[n.index] = n
        n = fst.get_node(next_space_index, next_time_index)
        node1.future[n.index] = n
        n = fst.get_node(x, past_time_index)
        node1.past[n.index] = n
        n = fst.get_node(prev_space_index, past_time_index)
        node1.past[n.index] = n

    return fst
