import numpy as np
from node import node
import random


class space_time(object):
    """docstring for space_time."""

    __slots__ = ["nodes", "space_slice_sizes", "num_time_slices", "max_index"]

    def __init__(self, space_slice_sizes, n_time_slices):
        super(space_time, self).__init__()
        self.nodes = {}
        self.space_slice_sizes = space_slice_sizes
        self.num_time_slices = n_time_slices
        self.max_index = 0

    def get_node(self, space_index, time_index):
        global_index = np.sum(self.space_slice_sizes[:time_index]) + space_index
        return self.nodes[global_index]

    def move(self, random_node):
        """inserts a new node to the right of a random node"""

        # selects a random node and a random future and past edge to be split
        random_future_index = random.choice(list(random_node.future))
        random_future_node = random_node.future[random_future_index]
        random_past_index = random.choice(list(random_node.past))
        random_past_node = random_node.past[random_past_index]

        new_node = node(
            self, str(random_node.space_index) + " right", random_node.time_index
        )
        random_node.space_index = str(random_node.space_index) + " left"

        # splits the set of future nodes in two
        future_left = [random_future_node]
        future_right = [random_future_node]
        n = random_future_node.right
        while n in list(random_node.future.values()):
            future_right.append(n)
            n = n.right
            # print("LOOPED")
            if n == random_future_node.right:
                break
        future_left += list(set(random_node.future.values()) - set(future_right))

        # assigns the two halfs to the new node and the random node
        random_node.replace_future(future_left)
        new_node.replace_future(future_right)
        # print(random_node.future)

        # splits the set of past nodes in two
        past_left = [random_past_node]
        past_right = [random_past_node]
        n = random_past_node.right
        while n in list(random_node.past.values()):
            past_right.append(n)
            n = n.right
            if n == random_past_node.right:
                break
        past_left += list(set(random_node.past.values()) - set(past_right))

        # assigns the two halfs to the new node and the random node
        random_node.replace_past(past_left)
        new_node.replace_past(past_right)

        # corrects the spatial connections of the new node and the random node
        new_node.right = random_node.right
        new_node.left = random_node
        random_node.right.left = new_node
        random_node.right = new_node

        self.nodes[new_node.index] = new_node
        self.space_slice_sizes[new_node.time_index] += 1

    def inverse_move(self, random_node):
        """ merges random_node with random_node.right"""

        random_node.space_index = "merged"

        for index, new_past_node in random_node.right.past.items():
            random_node.add_past(new_past_node)
        for index, new_future_node in random_node.right.future.items():
            random_node.add_future(new_future_node)

        random_node.right.replace_past([])
        random_node.right.replace_future([])

        del self.nodes[random_node.right.index]
        self.space_slice_sizes[random_node.time_index] -= 1

        random_node.right.right.left = random_node
        random_node.right = random_node.right.right
