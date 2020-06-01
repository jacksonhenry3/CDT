import numpy as np  # is this nescesary? Unlikely.


class node(object):
    """
    one node in the space-time network. A node has a left and right neighbor index
    as well as an unorderd dictionairy of future and past node indices. Each node is
    given a unique index for increased refrencing speed.
    """

    __slots__ = ["space_time", "future", "past", "left", "right", "index"]

    def __init__(self, space_time):
        self.future = []
        self.past = []
        self.left = None
        self.right = None
        self.space_time = space_time
        self.index = space_time.max_index
        space_time.max_index += 1
        space_time.nodes[self.index] = self

    def __repr__(self):
        return "self:{index}, left:{left}, right:{right}, past:{past}, future:{future}".format(
            future=self.future,
            past=self.past,
            left=self.left,
            right=self.right,
            index=self.index,
        )

    def num_connections(self):
        return len(self.future) + len(self.past) + 2

    def R(self, a=1):
        n = self.num_connections()
        return ((n - 6.0) * np.pi / 3.0) / (1 / 3.0 * n * a)

    def replace_right(self, right):
        self.right = right
        self.space_time.get_node(self.right).left = self.index

    def replace_left(self, left):
        self.left = left
        self.space_time.get_node(self.left).right = self.index

    def add_future(self, new_future_node):
        """adds new_future_node to selfs future"""
        self.future.append(new_future_node.index)
        new_future_node.past.append(self.index)

    def remove_future(self, old_future_node):
        """removes old_future_node from selfs future"""
        self.future.remove(old_future_node.index)
        old_future_node.past.remove(self.index)

    def add_past(self, new_past_node):
        """adds new_past_node to selfs past"""
        self.past.append(new_past_node.index)
        new_past_node.future.append(self.index)

    def remove_past(self, old_past_node):
        """removes old_past_node from selfs past"""
        self.past.remove(old_past_node.index)
        old_past_node.future.remove(self.index)

    def replace_future(self, new_future):
        """replaces selfs future with all the nodes with indices in the list new_future"""
        new_future = [self.space_time.get_node(index) for index in new_future]
        all_future = self.future.copy()
        for old_future_node in all_future:
            self.remove_future(self.space_time.get_node(old_future_node))
        for new_future_node in new_future:
            self.add_future(new_future_node)

    def replace_past(self, new_past):
        """replaces selfs past with all the nodes with indices in the list new_past"""
        new_past = [self.space_time.get_node(index) for index in new_past]
        all_past = self.past.copy()
        for old_past_node in all_past:
            self.remove_past(self.space_time.get_node(old_past_node))
        for new_past_node in new_past:
            self.add_past(new_past_node)
