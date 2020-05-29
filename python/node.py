import numpy as np  # is this nescesary? Unlikely.


class node(object):
    """
    one node in the space-time network. A node has a left and right neighbor
    as well as an unorderd dictionairy of future and past nodes. Each node is
    given a unique index for increased refrencing speed.

    notes and ideas:
        1. consider making future and past lists of ids.
        2. space_index is not needed for any calculation, just labeling, remove?
    """

    __slots__ = [
        "space_time",
        "space_index",
        "time_index",
        "future",
        "past",
        "left",
        "right",
        "index",
    ]

    def __init__(self, space_time, space_index, time_index):
        self.future = []
        self.past = []
        self.left = None
        self.right = None
        self.space_index = space_index
        self.time_index = time_index
        self.space_time = space_time
        self.index = space_time.max_index
        space_time.max_index += 1

    def __repr__(self):
        return str(self.index) + "node" + str((self.space_index, self.time_index))

    def get_node(self, index):
        return self.space_time.nodes[index]

    def num_connections(self):
        return len(self.future) + len(self.past) + 2

    def R(self, a=1):
        n = self.num_connections()
        return ((n - 6.0) * np.pi / 3.0) / (1 / 3.0 * n * a)

    def add_future(self, new_future_node):
        """adds new_future_node to selfs future"""
        self.future.append(new_future_node)
        self.get_node(new_future_node).past.append(self.index)

    def remove_future(self, old_future_node):
        """removes old_future_node from selfs future"""
        self.future.remove(old_future_node)
        self.get_node(old_future_node).past.remove(self.index)

    def add_past(self, new_past_node):
        """adds new_past_node to selfs past"""
        self.past.append(new_past_node)
        self.get_node(new_past_node).future.append(self.index)

    def remove_past(self, old_past_node):
        """removes old_past_node from selfs past"""
        self.past.remove(old_past_node)
        self.get_node(old_past_node).future.remove(self.index)

    def replace_future(self, new_future):
        """replaces selfs future with all the nodes in the list new_future"""
        all_future = self.future.copy()
        for old_future_node_index in all_future:
            # old_future_node = self.space_time.nodes[old_future_node_index]
            self.remove_future(old_future_node_index)
        for new_future_node in new_future:
            self.add_future(new_future_node)

    def replace_past(self, new_past):
        """replaces selfs past with all the nodes in the list new_past"""
        all_past = self.past.copy()
        for old_past_node in all_past:
            self.remove_past(old_past_node)
        for new_past_node in new_past:
            self.add_past(new_past_node)

    def global_index(self):
        sss = self.space_time.space_slice_sizes
        return np.sum(sss[: self.time_index]) + self.space_index
