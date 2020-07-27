import numpy as np
import random as r

from core.node import node

# MAKE SURE ALL INDICES ARE UNIQUE!!
class space_time(object):
    """space_time objects contain all nodes and their connections.
     They also allow for ergotic forward and inverse moves
     """

    __slots__ = ["nodes", "max_index", "origin", "invalid_nodes", "totalChanges", "SSS"]

    def __init__(self):
        super(space_time, self).__init__()
        self.nodes = {}  # a dictionairy from of all node ids to nodes.
        self.max_index = 0
        self.origin = 0
        self.invalid_nodes = []
        self.totalChanges = 0
        self.SSS = []

    # utilities
    def loop(self, func, start_index=None):
        """loops through all nodes arround each spatial slice sequentially strating at
        start_index,
        the result will be a dictionairy of node_index:func(n, time_index, index) """
        if start_index is None:
            start_index = self.origin

        if start_index not in self.nodes:
            print(start_index)
            print("bad start")
            return
        print("Starting Loop")
        result_dict = {}
        n_start = self.get_node(start_index)
        row_start = n_start.index
        n = n_start

        time_index = 0
        used_node_indices = []
        index = 0
        space_index = 0
        while n.index not in used_node_indices:
            result_dict[n.index] = func(n, time_index, space_index, index)
            used_node_indices.append(n.index)
            n = self.get_node(n.right)
            space_index += 1
            index += 1

            if n.index == row_start:
                space_index = 0
                time_index += 1
                n = self.get_node(n.future[0])
                row_start = n.index
        return result_dict

    def generate_flat(self, space_size, time_size):
        if self.max_index > 0:
            print("there are already nodes! This can only run on a new space_time")
            return ()

        for time_slice in range(time_size):
            for spacial_slice in range(space_size):
                node(self)

        for time_slice in range(time_size):
            self.SSS.append(0)
            for spacial_slice in range(space_size):
                self.SSS[time_slice] += 1
                index = time_size * spacial_slice + time_slice
                n = self.get_node(index)
                n.t = time_slice
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

    def get_node(self, index):
        "returns the node at index"
        return self.nodes[index]

    def get_random_node(self):
        """ Does what it says on the tin, gets a random node from self"""
        index = r.randrange(len(self.nodes))
        return list(self.nodes.values())[index]

    # def space_slice_sizes(self, start=None):
    #     time_indices = list(self.loop(lambda n, t, x, i: t, start_index=start).values())
    #     unique, counts = np.unique(time_indices, return_counts=True)
    #     res = unique
    #     for index in unique:
    #         res[index] = counts[index]
    #     return res

    def save(self, name=None):
        import pickle as pkl
        from os import mkdir, path

        if name is None:
            name = "testname"

        if not path.exists("./spacetimes/" + name):
            mkdir("./spacetimes/" + name)

        name = "./spacetimes/" + name + "/" + name
        with open(name + ".st", "wb") as file:
            pkl.dump(self, file)

        with open(name + ".data", "w") as file:
            lines = ["spatial slice sizes : " + str(self.SSS)]
            lines.append("a list of all nodes and connections")
            for n in self.nodes:
                lines.append(self.nodes[n].__repr__())
            file.writelines(line + "\n" for line in lines)

    # physics

    def move(self, old_node):

        """
        Inserts a new node to the right of a random node. The newly created
        node should have a randomly selected half of the future and half of the
        past edges of node
        """

        self.totalChanges += 1
        new_node = node(self)
        new_node.t = old_node.t
        self.SSS[old_node.t] += 1

        # selects a random future and past edge to be split
        random_future_index = r.choice(old_node.future)
        random_future_node = self.get_node(random_future_index)
        random_past_index = r.choice(old_node.past)
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

        future_left = np.unique(future_left)
        future_right = np.unique(future_right)

        # assigns the two halfs to the new node and the random node
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

        past_left = np.unique(past_left)
        past_right = np.unique(past_right)
        # assigns the two halfs to the new node and the random node
        old_node.replace_past(past_left)
        new_node.replace_past(past_right)

        # corrects the spatial connections of the new node and the random node
        new_node.right = old_node.right
        new_node.left = old_node.index
        self.get_node(old_node.right).left = new_node.index
        old_node.right = new_node.index

        self.nodes[new_node.index] = new_node
        if old_node in self.invalid_nodes:
            self.invalid_nodes.append(new_node)

        if not new_node.validate():
            self.invalid_nodes.append(new_node.index)
            # raise ValueError("a move created an invalid node {}".format(new_node))
        if not old_node.validate():
            self.invalid_nodes.append(old_node.index)
        # raise ValueError("a move created an invalid node {}".format(old_node))

    def inverse_move(self, random_node):
        """ merges random_node with random_node.right"""
        self.totalChanges += 1
        self.SSS[random_node.t] -= 1

        # adds the past and future of random_node.right to random_node
        if random_node.right == random_node.index:
            # raise Exception("a spatial layer has only a single node!")
            print("inverse move is invalid becouse this node is its own neighbor")
            return ()
        for new_past_node in self.get_node(random_node.right).past:
            # print(self.get_node(random_node.right).past)
            random_node.add_past(self.get_node(new_past_node))
            # print(new_past_node)
        for new_future_node in self.get_node(random_node.right).future:
            random_node.add_future(self.get_node(new_future_node))

        random_node.replace_past(np.unique(random_node.past))
        random_node.replace_future(np.unique(random_node.future))

        # removes the past and future from random_node.right
        self.get_node(random_node.right).replace_past([])
        self.get_node(random_node.right).replace_future([])

        # fix the spatial indeced of the remaining random_node
        self.get_node(self.get_node(random_node.right).right).left = random_node.index
        prev_right = self.get_node(random_node.right)
        random_node.right = prev_right.right

        if prev_right.index == self.origin:
            self.origin = prev_right.right
        # remove random_node.right from self
        # print("Premptive one " +if random_node.future str(random_node.right))
        if self.nodes[prev_right.index] in self.invalid_nodes:
            self.invalid_nodes.append(random_node)

        if self.nodes[prev_right.index] in self.invalid_nodes:
            self.invalid_nodes.append(random_node)

        if not random_node.validate():
            self.invalid_nodes.append(random_node.index)

        del self.nodes[prev_right.index]

    # useful for visualizations
    def adjacency_matrix(self):

        for n in self.nodes.values():
            if not n.validate():
                self.invalid_nodes.append(n.index)

        row_idex_dict = {}
        slice_sep = 1
        n_start = list(self.nodes.values())[0]
        row_idex_dict = self.loop(
            lambda n, t, x, i: i + slice_sep * (t + 1), n_start.index
        )
        num_time_slices = len(self.space_slice_sizes())
        array_size = len(self.nodes) + slice_sep * num_time_slices
        m = np.zeros((array_size, array_size))
        for i, n in enumerate(self.nodes.values()):
            ro_idx = row_idex_dict[n.index]
            m[ro_idx, row_idex_dict[n.right]] = self.inv(n.index, n.right)
            m[ro_idx, row_idex_dict[n.left]] = self.inv(n.index, n.left)
            for f in n.future:
                m[ro_idx, row_idex_dict[f]] = self.inv(n.index, f)
            for p in n.past:
                m[ro_idx, row_idex_dict[p]] = self.inv(n.index, p)

        if slice_sep != 0:
            total_prev_nodes = np.cumsum(self.space_slice_sizes(start=n_start.index))
            total_prev_nodes = np.insert(total_prev_nodes, 0, 0, axis=0)
            total_prev_nodes = total_prev_nodes[:-1]
            for i, gutter_index in enumerate(total_prev_nodes):
                index = gutter_index + (i + 1) * slice_sep - 1
                for width in range(slice_sep):
                    for j in range(array_size):
                        m[index - width, j] += 0.25
                        m[j, index - width] += 0.25
        return m

    def validate(self):
        # add validationg for total curvature
        allnodes = True
        for node_index in self.nodes:
            allnodes = allnodes and self.get_node(node_index).validate()
        # if allnodes:
        #     print("all nodes pass")
        return allnodes

    def inv(self, i, j):
        if i in self.invalid_nodes or j in self.invalid_nodes:
            return 2
        return 1
