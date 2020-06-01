from node import node
from numpy.random import default_rng
import numpy as np

rg = default_rng(12345)


class space_time(object):
    """space_time objects contain all nodes and their connections.
     They also allow for ergotic forward and inverse moves

     fixes and optimizations:
        1. The initialization should only require Figure_1space_slice_sizes
        2. get_node is only used for initialization, can this be removed?
        3. adjacency matrix for viz?
     """

    __slots__ = ["nodes", "space_slice_sizes", "num_time_slices", "max_index"]

    def __init__(self):
        super(space_time, self).__init__()
        self.nodes = {}  # a dictionairy from of all node ids to nodes.
        self.space_slice_sizes = []
        self.num_time_slices = len(self.space_slice_sizes)
        self.max_index = 0

    def generate_flat(self, space_size, time_size):
        if self.max_index > 0:
            print("there are already nodes! This can only run on a new space_time")
            return ()
        self.space_slice_sizes = np.full(time_size, space_size)
        self.num_time_slices = len(self.space_slice_sizes)

        for spacial_slice in range(space_size):
            for time_slice in range(time_size):
                a = self.new_node()
                print(a.index)

        for spacial_slice in range(space_size):
            for time_slice in range(time_size):
                index = time_size * spacial_slice + time_slice
                n = self.get_node(index)
                print(index)
                print("==============")
                n.replace_right(
                    time_size * ((spacial_slice - 1) % space_size) + time_slice
                )

                n.replace_future(
                    [
                        time_size * spacial_slice + (time_slice + 1) % time_size,
                        time_size * ((spacial_slice + 1) % space_size)
                        + (time_slice + 1) % time_size,
                    ]
                )

    def new_node(self):
        return node(self)

    def get_node(self, index):
        "returns the node at idnex"
        return self.nodes[index]

    def get_random_node(self):
        """ Does what it says on the tin, gets a random node from self"""
        # print(self.nodes.values())
        return rg.choice(list(self.nodes.values()))

    def move(self, old_node):
        """
        Inserts a new node to the right of a random node. The newly created
        node should have a randomly selected half of the future and half of the
        past edges of node
        """

        new_node = node(self)

        # selects a random future and past edge to be split
        random_future_index = rg.choice(old_node.future)
        random_future_node = self.get_node(random_future_index)
        random_past_index = rg.choice(old_node.past)
        random_past_node = self.get_node(random_past_index)

        # splits the set of future nodes in two
        future_left = [random_future_index]
        future_right = [random_future_index]
        n = random_future_node.right
        while n in old_node.future:
            future_right.append(n)
            n = self.get_node(n).right
            if n == random_future_node.right:
                break
        future_left += list(set(old_node.future) - set(future_right))

        # assigns the two halfs to the new node and the random node
        # future_left = [self.nodes[index] for index in future_left]
        old_node.replace_future(future_left)
        new_node.replace_future(future_right)

        # splits the set of past nodes in two
        past_left = [random_past_index]
        past_right = [random_past_index]
        n = random_past_node.right
        while n in old_node.past:
            past_right.append(n)
            n = self.get_node(n).right
            if n == random_past_node.right:
                break
        past_left += list(set(old_node.past) - set(past_right))

        # assigns the two halfs to the new node and the random node
        old_node.replace_past(past_left)
        new_node.replace_past(past_right)

        # corrects the spatial connections of the new node and the random node
        new_node.right = old_node.right
        new_node.left = old_node.index
        old_node.right.left = new_node.index
        old_node.right = new_node.index

        self.nodes[new_node.index] = new_node
        self.space_slice_sizes[new_node.time_index] += 1

    def inverse_move(self, random_node):
        """ merges random_node with random_node.right"""

        random_node.space_index = "merged"

        # adds the past and future of random_node.right to random_node
        for new_past_node in random_node.right.past:
            random_node.add_past(new_past_node)
        for new_future_node in random_node.right.future:
            random_node.add_future(new_future_node)

        # removes the past and future from random_node.right
        random_node.right.replace_past([])
        random_node.right.replace_future([])

        # remove random_node.right from self
        del self.nodes[random_node.right]

        # since a node was removed the time slice from which it was removed is
        # smaller by one.
        self.space_slice_sizes[random_node.time_index] -= 1

        # fix the spatial indeced of the remaining random_node
        random_node.right.right.left = random_node
        random_node.right = random_node.right.right
