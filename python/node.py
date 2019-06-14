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
        self.future = {}
        self.past = {}
        self.left = None
        self.right = None
        self.space_index = space_index
        self.time_index = time_index
        self.space_time = space_time
        self.index = space_time.max_index
        space_time.max_index += 1

    def __repr__(self):
        return "node" + str((self.space_index, self.time_index))

    def add_future(self, new_future_node):
        """adds new_future_node to selfs future"""
        self.future[new_future_node.index] = new_future_node
        new_future_node.past[self.index] = self

    def remove_future(self, old_future_node):
        """removes old_future_node from selfs future"""
        del self.future[old_future_node.index]
        del old_future_node.past[self.index]

    def add_past(self, new_past_node):
        """adds new_past_node to selfs past"""
        self.past[new_past_node.index] = new_past_node
        new_past_node.future[self.index] = self

    def remove_past(self, old_past_node):
        """removes old_past_node from selfs past"""
        del self.past[old_past_node.index]
        del old_past_node.future[self.index]

    def replace_future(self, new_future):
        """replaces selfs future with all the nodes in the list new_future"""
        all_future = self.future.copy()
        for index, old_future_node in all_future.items():
            self.remove_future(old_future_node)
        for new_future_node in new_future:
            self.add_future(new_future_node)

    def replace_past(self, new_past):
        """replaces selfs past with all the nodes in the list new_past"""
        all_past = self.past.copy()
        for index, old_past_node in all_past.items():
            self.remove_past(old_past_node)
        for new_past_node in new_past:
            self.add_past(new_past_node)

    def global_index(self):
        sss = self.space_time.space_slice_sizes
        return np.sum(sss[: self.time_index]) + self.space_index
