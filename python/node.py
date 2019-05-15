import numpy as np


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
        self.future[new_future_node.index] = new_future_node
        new_future_node.past[self.index] = self

    def remove_future(self, old_future_node):
        del self.future[old_future_node.index]
        del old_future_node.past[self.index]

    def add_past(self, new_past_node):
        self.past[new_past_node.index] = new_past_node
        new_past_node.future[self.index] = self

    def remove_past(self, old_past_node):
        del self.past[old_past_node.index]
        del old_past_node.future[self.index]

    def replace_future(self, new_future):
        all_future = self.future.copy()
        for index, old_future_node in all_future.items():
            self.remove_future(old_future_node)
        for new_future_node in new_future:
            self.add_future(new_future_node)

    def replace_past(self, new_past):
        all_past = self.past.copy()
        for index, old_past_node in all_past.items():
            self.remove_past(old_past_node)
        for new_past_node in new_past:
            self.add_past(new_past_node)

    def global_index(self):
        sss = self.space_time.space_slice_sizes
        return np.sum(sss[: self.time_index]) + self.space_index
