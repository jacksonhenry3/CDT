# pretty sure all of this importing  is unnsescsary
import numpy as np
from node import node
import random

from numpy.random import default_rng

rg = default_rng(12345)


class space_time(object):
    """space_time objects contain all nodes and their connections.
     They also allow for ergotic forward and inverse moves

     fixes and optimizations:
        1. The initialization should only require Figure_1space_slice_sizes
        2. get_node is only used for initialization, can this be removed?
     """

    __slots__ = ["nodes", "space_slice_sizes", "num_time_slices", "max_index"]

    def __init__(self, space_slice_sizes, n_time_slices):
        super(space_time, self).__init__()
        self.nodes = {}  # a dictionairy from of all node ids to nodes.
        self.space_slice_sizes = space_slice_sizes
        self.num_time_slices = n_time_slices
        self.max_index = 0

    def get_node(self, space_index, time_index):
        global_index = np.sum(self.space_slice_sizes[:time_index]) + space_index
        return self.nodes[global_index]

    def move(self, random_node):
        """
        Inserts a new node to the right of a random node. The newly created
        node should have a randomly selected half of the future and half of the
        past edges of random_node
        """

        # selects a random future and past edge to be split
        random_future_index = rg.integers(len(random_node.future))
        random_future_node = self.nodes[random_node.future[random_future_index]]
        random_past_index = rg.integers(len(random_node.past))
        random_past_node = self.nodes[random_node.past[random_past_index]]

        new_node = node(
            self, str(random_node.space_index) + " right", random_node.time_index
        )
        random_node.space_index = str(random_node.space_index) + " left"

        # splits the set of future nodes in two
        future_left = [random_future_index]
        future_right = [random_future_index]
        n = random_future_node.right
        while n in random_node.future:
            future_right.append(n)
            n = self.nodes(n).right
            if n == random_future_node.right.index:
                break
        future_left += list(set(random_node.future) - set(future_right))

        # assigns the two halfs to the new node and the random node
        # future_left = [self.nodes[index] for index in future_left]
        random_node.replace_future(future_left)
        new_node.replace_future(future_right)

        # splits the set of past nodes in two
        past_left = [random_past_index]
        past_right = [random_past_index]
        n = random_past_node.right
        while n in list(random_node.past):
            past_right.append(n)
            n = self.nodes(n).right
            if n == random_past_node.right:
                break
        past_left += list(set(random_node.past) - set(past_right))

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

        # adds the past and future of random_node.right to random_node
        for index, new_past_node in random_node.right.past.items():
            random_node.add_past(new_past_node)
        for index, new_future_node in random_node.right.future.items():
            random_node.add_future(new_future_node)

        # removes the past and future from random_node.right
        random_node.right.replace_past([])
        random_node.right.replace_future([])

        # remove random_node.right from self
        del self.nodes[random_node.right.index]

        # since a node was removed the time slice from which it was removed is
        # smaller by one.
        self.space_slice_sizes[random_node.time_index] -= 1

        # fix the spatial indeced of the remaining random_node
        random_node.right.right.left = random_node
        random_node.right = random_node.right.right

    def get_random_node(self):
        """ Does what it says on the tin, gets a random node from self"""
        num_nodes = np.sum(self.space_slice_sizes)
        random_node_list_index = np.random.randint(num_nodes)
        random_index = list(self.nodes.keys())[random_node_list_index]
        return self.nodes[random_index]
