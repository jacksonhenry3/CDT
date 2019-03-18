import numpy as np
from numpy import cos, sin
import matplotlib.pyplot as plt
from matplotlib import collections as mc
from mpl_toolkits.mplot3d import Axes3D

"""consider removing node spatial index and node time index, i believe they are only needed for falt space time intiailization"""
"""https://stackoverflow.com/questions/472000/usage-of-slots"""


"""still not working, nodes not in space_)time are left in past, if running many moves all nodes concetrate along a small subsection of the bottom ring"""


class node(object):
    """The base structur"""

    __slots__ = [
        "space_time",
        "space_index",
        "time_index",
        "future",
        "past",
        "left",
        "right",
    ]

    def __init__(self, space_time, space_index, time_index):
        self.future = []
        self.past = []
        self.left = None
        self.right = None
        self.space_index = space_index
        self.time_index = time_index
        self.space_time = space_time

    def __repr__(self):

        return "node" + str((self.space_index, self.time_index))

    def global_index(self):
        sss = self.space_time.space_slice_sizes
        return np.sum(sss[: self.time_index]) + self.space_index


class space_time(object):
    """docstring for space_time."""

    __slots__ = ["nodes", "space_slice_sizes", "num_time_slices"]

    def __init__(self, space_slice_sizes, n_time_slices):
        super(space_time, self).__init__()
        self.nodes = []
        self.space_slice_sizes = space_slice_sizes
        self.num_time_slices = n_time_slices

    def get_node(self, space_index, time_index):
        global_index = np.sum(self.space_slice_sizes[:time_index]) + space_index
        return self.nodes[global_index]

    def move(self):
        """inserts a new node to the right of a random node"""

        # selects a random node and a random future and past edge to be split
        random_node = np.random.choice(self.nodes)
        random_future_node = np.random.choice(random_node.future)
        random_past_node = np.random.choice(random_node.past)

        random_node.space_index = "left split node"
        new_node = node(self, "right split node", random_node.time_index)

        # splits the set of future nodes in two
        future_left = [random_future_node]
        future_right = [random_future_node]
        n = random_future_node.right
        while n in random_node.future:
            future_right.append(n)
            n = n.right
        future_left += list(set(random_node.future) - set(future_right))

        # assigns the two halfs to the new node and the random node
        new_node.future = future_right
        random_node.future = future_left

        # splits the set of past nodes in two
        past_left = [random_past_node]
        past_right = [random_past_node]
        n = random_past_node.right
        while n in random_node.past:
            past_right.append(n)
            n = n.right
        past_left += list(set(random_node.past) - set(past_right))

        # assigns the two halfs to the new node and the random node
        new_node.past = past_right
        random_node.past = past_left

        # corrects the spatial connections of the new node and the random node
        new_node.right = random_node.right
        new_node.left = random_node
        random_node.right.left = new_node
        random_node.right = new_node

        self.nodes.append(new_node)
        self.space_slice_sizes[new_node.time_index] += 1

    def inverse_move(self):
        """ merges random_node with random_node.right"""

        random_node = np.random.choice(self.nodes)
        new_node = node(self, "merged node", random_node.time_index)

        # the list set thing forces uniquness
        new_node.left = random_node.left
        new_node.right = random_node.right.right

        new_node.past = np.append(random_node.past, random_node.right.past)
        new_node.past = list(set(new_node.past))

        new_node.future = np.append(random_node.future, random_node.right.future)
        new_node.future = list(set(new_node.future))

        # currently this isnt removing random node from the past of new nodes future

        # print(new_node)
        for n in new_node.future:
            #    print(n)
            #    print(n.past)
            n.past = [
                n if (n != random_node and n != random_node.right) else new_node
                for n in n.past
            ]
            n.past = list(set(n.past))

        for n in new_node.past:
            n.future = [
                n if (n != random_node and n != random_node.right) else new_node
                for n in n.future
            ]
            n.future = list(set(n.future))

        random_node.left.right = new_node
        random_node.right.right.left = new_node

        self.nodes.remove(random_node)
        self.nodes.remove(random_node.right)
        self.nodes.append(new_node)
        self.space_slice_sizes[new_node.time_index] -= 1
        # print(new_node)


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

    d_theta = 2 * np.pi / num_nodes_in_space_slice
    theta = 0
    for n in space_time.nodes:
        if n.time_index == 0:
            # this only works if the 0 level nodes are ordered
            theta += d_theta
            h = 0
            cyl_coord_dict[n] = [theta, h]

    for time_index in range(1, space_time.num_time_slices):
        for n in space_time.nodes:
            if n.time_index == time_index:
                past_angles = []
                for past in n.past:
                    print(n)
                    past_angles.append(cyl_coord_dict[past][0])
                # past_angles = [cyl_coord_dict[past][0] for past in n.past]
                theta = np.arctan2(
                    1 / len(n.past) * np.sum(sin(past_angles)),
                    1 / len(n.past) * np.sum(cos(past_angles)),
                )
                h = n.time_index
                cyl_coord_dict[n] = [theta, h]

    cart_coord_dict = {}

    for n in space_time.nodes:
        theta = cyl_coord_dict[n][0]
        h = cyl_coord_dict[n][1]
        cart_coord_dict[n] = [radius * cos(theta), radius * sin(theta), h]

    x_coords = []
    y_coords = []
    z_coords = []

    for n in space_time.nodes:
        x_coords.append(cart_coord_dict[n][0])
        y_coords.append(cart_coord_dict[n][1])
        z_coords.append(cart_coord_dict[n][2])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(x_coords, y_coords, z_coords)
    plt.show()


simple_st = make_flat_spacetime(32, 16)

for i in range(1100):
    simple_st.move()

vizualize_space_time(simple_st)
