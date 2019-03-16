"""consider removing node spatial index and node time index, i believe they are only needed for falt space time intiailization"""

import numpy as np
from numpy import cos, sin
import matplotlib.pyplot as plt
from matplotlib import collections as mc


class node(object):
    """docstring for node."""

    def __init__(self, space_time, space_index, time_index):
        self.future = []
        self.past = []
        self.left = None
        self.right = None
        self.space_index = space_index
        self.time_index = time_index
        self.space_time = space_time

    def global_index(self):
        sss = self.space_time.space_slice_sizes
        return np.sum(sss[: self.time_index]) + self.space_index


class space_time(object):
    """docstring for space_time."""

    def __init__(self, space_slice_sizes, n_time_slices):
        super(space_time, self).__init__()
        self.nodes = []
        self.space_slice_sizes = space_slice_sizes
        self.num_time_slices = n_time_slices

    def get_node(self, space_index, time_index):
        sss = self.space_slice_sizes
        global_index = np.sum(sss[:time_index]) + space_index
        return self.nodes[global_index]

    def move(self):
        random_node = np.random.choice(self.nodes)
        random_future_edge = np.random.choice(random_node.future)
        random_past_edge = np.random.choice(random_node.future)

    def inverse_move(self):

        random_node = np.random.choice(self.nodes)
        new_node = node(self, None, None)

        new_node.left = random_node.left
        new_node.right = random_node.right.right
        new_node.past = np.union1d(random_node.past, random_node.right.past)
        new_node.future = np.union1d(random_node.future, random_node.right.future)

        self.nodes.remove(random_node)
        self.nodes.remove(random_node.right)
        self.nodes.append(new_node)


def make_flat_spacetime(n_space_slices, n_time_slices):
    """docstring"""

    fst = space_time(np.full(n_time_slices, n_space_slices), n_time_slices)

    # add all nodes

    for t_index in range(n_time_slices):
        for x_index in range(n_space_slices):
            fst.nodes.append(node(fst, x_index, t_index))

    # connect spatial nodes

    for node1 in fst.nodes:
        x = node1.space_index
        t = node1.time_index
        next_space_index = np.mod(x + 1, fst.space_slice_sizes[t])
        prev_space_index = np.mod(x - 1, fst.space_slice_sizes[t])
        next_time_index = np.mod(t + 1, fst.num_time_slices)
        past_time_index = np.mod(t - 1, fst.num_time_slices)
        node1.right = fst.get_node(next_space_index, t)
        node1.left = fst.get_node(prev_space_index, t)
        node1.future.append(fst.get_node(x, next_time_index))
        node1.future.append(fst.get_node(next_space_index, next_time_index))
        node1.past.append(fst.get_node(x, past_time_index))
        node1.past.append(fst.get_node(prev_space_index, past_time_index))

    return fst


def vizualize_space_time(space_time, radius=5):

    cyl_coord_dict = {}

    # there should be a better way to select out nodes with a certain property
    num_nodes_in_space_slice = space_time.space_slice_sizes[0]

    n = space_time.nodes[0]
    d_theta = 2*np.pi/num_nodes_in_space_slice
    theta = 0
    for n in space_time.nodes:
        if n.time_index == 0:
            theta += d_theta
            h = 0
            cyl_coord_dict[n] = [theta, h]


    for n in space_time.nodes:
        if n.time_index != 0:
            theta = np.mean([cyl_coord_dict[n][0] for theta in n.past])
            h = n.time_index
            cyl_coord_dict[n] = [theta, h]

    cart_coord_dict = {}

    for n in space_time.nodes:
        theta = cyl_coord_dict[n][0]
        h = cyl_coord_dict[n][1]
        cart_coord_dict[n] = [radius*cos(theta), radius*sin(theta), h]


simple_st = make_flat_spacetime(16, 8)

vizualize_space_time(simple_st)
# vizualization test

x_coords = []
y_coords = []
lines = []
for n in simple_st.nodes:
    x = 2 * n.space_index
    y = 2 * n.time_index

    x1 = 2 * n.right.space_index
    y1 = 2 * n.right.time_index

    x2 = 2 * n.future[1].space_index
    y2 = 2 * n.future[1].time_index

    x3 = 2 * n.future[0].space_index
    y3 = 2 * n.future[0].time_index

    x4 = 2 * n.past[1].space_index
    y4 = 2 * n.past[1].time_index

    x5 = 2 * n.past[0].space_index
    y5 = 2 * n.past[0].time_index

    offset = .1
    lines.append([(x, y), (x1, y1)])
    lines.append([(x, y), (x1, y1)])
    lines.append([(x, y), (x2, y2)])
    lines.append([(x, y), (x3, y3)])
    lines.append([(x, y), (x4, y4)])
    lines.append([(x, y), (x5, y5)])

    x_coords.append(x)
    y_coords.append(y)

lc = mc.LineCollection(lines, linewidths=2)
fig, ax = plt.subplots()
ax.add_collection(lc)
ax.autoscale()
ax.margins(0.1)

plt.plot(x_coords, y_coords, "r.")
plt.show()
