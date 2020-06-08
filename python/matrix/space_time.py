import numpy as np
import random as r
import matplotlib.pyplot as plt

r.seed(1)


class space_time(object):
    """docstring for space_time."""

    def __init__(self, slice_size=16, num_slices=32):
        super(space_time, self).__init__()
        self.spatial_slice_sizes = np.full(num_slices, slice_size)
        self.update_total_prev_nodes()
        self.num_slices = num_slices
        self.num_nodes = slice_size * num_slices
        # self.data = np.zeros((self.num_nodes, self.num_nodes), dtype=np.bool)
        self.data = np.zeros((self.num_nodes, self.num_nodes))

        for i in range(self.num_nodes):
            x = self.x(i)
            t = self.t(i)

            slice_size = self.spatial_slice_sizes[t]
            n_s = len(self.spatial_slice_sizes)  # number of slices
            connections = []

            # connect to the right
            connections.append(self.get_index((x + 1) % slice_size, t))

            # connect to the emdiate future
            connections.append(self.get_index(x, (t + 1) % n_s))

            # connect to the future one to the right
            connections.append(self.get_index((x - 1) % slice_size, (t + 1) % n_s))

            for connection in connections:
                self.data[i, connection] += 1
                self.data[connection, i] += 1

    def update_total_prev_nodes(self):
        self.total_prev_nodes = np.cumsum(self.spatial_slice_sizes)
        self.total_prev_nodes = np.insert(self.total_prev_nodes, 0, 0)

    def x(self, node_index):
        t = self.t(node_index)
        return node_index - self.total_prev_nodes[t]

    def t(self, node_index):
        t = 0
        for i, tot_nodes in enumerate(self.total_prev_nodes):
            if tot_nodes > node_index:
                return i - 1
        # return np.where(self.total_prev_nodes > node_index)[0][0] - 1

    def slice_size(self, node_index):
        """gets the size of the slice containing node_index"""
        return self.spatial_slice_sizes[self.t(node_index)]

    def get_index(self, x, t):
        return self.total_prev_nodes[t] + x

    def show(self):
        # inserts rows and columns showing the spatial boundaries.
        newm = self.data
        for i, slice_index in enumerate(self.total_prev_nodes):
            newm = np.insert(newm, slice_index + i, np.full((1, self.num_nodes), 2), 0)

        for i, slice_index in enumerate(self.total_prev_nodes):
            col = np.full((self.num_nodes + self.num_slices + 1), 2)
            newm = np.insert(newm, slice_index + i, col, 1)
        return newm

    def inverse_move(self, index):
        t = self.t(index)

        self.data[:, index] = np.logical_or(
            self.data[:, index], self.data[:, self.right(index)]
        )
        self.data[index, :] = np.logical_or(
            self.data[index, :], self.data[self.right(index), :]
        )
        self.data[(index), (index)] = 0
        self.data = np.delete(self.data, self.right(index), 0)
        self.data = np.delete(self.data, self.right(index), 1)

        self.spatial_slice_sizes[t] -= 1
        self.num_nodes -= 1
        self.update_total_prev_nodes()

    def edges(self, index):
        return np.where(self.data[index, :] == 1)

    def get_future(self, index):
        t = self.t(index)
        edges = self.edges(index)[0]
        future_edges = [
            edge for edge in edges if self.t(edge) == (t + 1) % self.num_slices
        ]
        return np.array(future_edges)

    def get_past(self, index):
        t = self.t(index)
        edges = self.edges(index)[0]
        past_edges = [
            edge for edge in edges if self.t(edge) == (t - 1) % self.num_slices
        ]
        return np.array(past_edges)

    def right(self, index):
        t = self.t(index)
        slice_size = self.spatial_slice_sizes[t]
        return self.get_index((self.x(index) + 1) % slice_size, self.t(index))

    def left(self, index):
        t = self.t(index)
        slice_size = self.spatial_slice_sizes[t]
        return self.get_index((self.x(index) - 1) % slice_size, self.t(index))

    def move(self, index):
        t = self.t(index)

        # gets the future, sort, and split
        future = self.get_future(index)
        future_predicate = [
            self.sorted_index_in_row(future, future_node) for future_node in future
        ]
        future_ordering = np.argsort(future_predicate)
        future = future[future_ordering]

        split_point = r.randrange(0, len(future))
        future_left = future[: split_point + 1]
        future_right = future[split_point:]

        # gets the past, sort, and split
        past = self.get_past(index)
        past_predicate = [
            self.sorted_index_in_row(past, past_node) for past_node in past
        ]
        past_ordering = np.argsort(past_predicate)
        past = past[past_ordering]

        split_point = r.randrange(0, len(past))
        past_left = past[: split_point + 1]
        past_right = past[split_point:]

        row_old = self.data[index, :]
        row_old = np.zeros(self.num_nodes, dtype=np.bool)
        row_old = np.zeros(self.num_nodes)
        row_old[future_left] += 1
        row_old[past_left] += 1

        self.data[index, :] = row_old
        self.data[:, index] = row_old

        row_new = np.zeros(self.num_nodes, dtype=np.bool)
        row_new = np.zeros(self.num_nodes)

        row_new[future_right] += 1
        row_new[past_right] += 1
        col_new = np.insert(row_new, index, 0)

        self.data = np.insert(self.data, index + 1, row_new, 0)
        self.data = np.insert(self.data, index + 1, col_new, 1)

        self.spatial_slice_sizes[t] += 1
        self.num_nodes += 1
        self.update_total_prev_nodes()

        slice_size = self.spatial_slice_sizes[t]

        old_right = self.get_index((self.x(index) + 1) % slice_size, t)
        old_left = self.get_index((self.x(index) - 1) % slice_size, t)
        self.data[index, old_right] += 1
        self.data[index, old_left] += 1
        self.data[old_right, index] += 1
        self.data[old_left, index] += 1
        new_right = self.get_index((self.x(index + 1) + 1) % slice_size, t)
        self.data[index + 1, new_right] += 1
        self.data[new_right, index + 1] += 1

    def sorted_index_in_row(self, row_list, index):
        if len(row_list) == self.spatial_slice_sizes[self.t(index)]:
            print("FAIL, one nodes future or past contains an entire slice!")
        else:
            refrence_index = row_list[0]
            while self.left(refrence_index) in row_list:
                refrence_index = self.left(refrence_index)
                # print(refrence_index)
            count = 0
            while refrence_index != index:
                refrence_index = self.right(refrence_index)
                count += 1
            return count

    def get_random_node(self):
        return r.randrange(0, self.num_nodes)

    def plot(self):

        # unzip
        display_connections = {}
        node_start = 0
        node = self.right(node_start)
        display_connections[node_start] = [self.x(node_start), self.t(node_start)]
        while node != node_start:
            display_connections[node] = [self.x(node), self.t(node)]
            node = self.right(node)

        for node in range(self.num_nodes):
            x = self.x(node)
            y = self.t(node)
            for connection in self.get_future(node):
                f_x = self.x(connection)
                f_y = self.t(connection)

                start_node = self.get_past(connection)[0]
                node = self.right(start_node)
                max_past = display_connections[start_node][0]
                while node != start_node:
                    past_x = display_connections[node][0]

                    if past_x > max_past:
                        max_past = past_x
                    node = self.right(node)

                if f_y == y + 1:
                    #
                    past = self.get_past(connection)
                    position = 0
                    num_counted = 0

                    for p in past:
                        p_x = self.x(p)
                        p_y = self.t(p)

                        if f_x - p_x != self.spatial_slice_sizes[f_y] - 1:
                            num_counted += 1
                            position += display_connections[p][0]
                        else:
                            num_counted += 1
                            position += (
                                max_past + display_connections[p][0] - p_y * 0.5 + 1
                            )

                    position = position / num_counted
                    display_connections[connection] = np.array([position, f_y])
        fig, ax = plt.subplots()
        for node in range(self.num_nodes):
            # print(node)
            x = self.x(node)
            y = self.t(node)
            for connection in self.get_future(node):
                x = display_connections[node][0]
                y = display_connections[node][1]
                c_x = display_connections[connection][0]
                c_y = display_connections[connection][1]
                if (
                    self.t(connection) == y + 1
                    and self.x(connection) - self.x(node)
                    != self.spatial_slice_sizes[self.t(connection)] - 1
                ):
                    # print(display_connections[connection])
                    ax.plot([x, c_x], [y, c_y], "k", alpha=0.7)
            # ax.scatter(x, y)
            # ax.annotate(node, (x, y))

        plt.show()
