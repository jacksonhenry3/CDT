# pretty sure all of this importing  is unnsescsary
import numpy as np
from node import node
from space_time import space_time


def make_flat_spacetime(n_space_slices, n_time_slices):
    """generates a uniform flat space time network"""

    fst = space_time(np.full(n_time_slices, n_space_slices), n_time_slices)

    # add all nodes
    for t_index in range(n_time_slices):
        for x_index in range(n_space_slices):
            n = node(fst, x_index, t_index)
            fst.nodes[n.index] = n

    # connect nodes
    for node1 in fst.nodes.values():
        x = node1.space_index
        t = node1.time_index

        # get the indices of space and time adjacent nodes.
        next_space_index = np.mod(x + 1, fst.space_slice_sizes[t])
        prev_space_index = np.mod(x - 1, fst.space_slice_sizes[t])
        next_time_index = np.mod(t + 1, fst.num_time_slices)
        past_time_index = np.mod(t - 1, fst.num_time_slices)

        # connect the left and right nodes
        node1.right = fst.get_node(next_space_index, t)
        node1.left = fst.get_node(prev_space_index, t)

        # connect the future and past nodes
        n = fst.get_node(x, next_time_index)
        node1.future.append(n.index)
        n = fst.get_node(next_space_index, next_time_index)
        node1.future.append(n.index)
        n = fst.get_node(x, past_time_index)
        node1.past.append(n.index)
        n = fst.get_node(prev_space_index, past_time_index)
        node1.past.append(n.index)

    return fst
