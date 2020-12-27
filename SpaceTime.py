import numpy as np


class SpaceTime(object):
    """docstring for SpaceTime."""

    # __slots__ = []

    def __init__(self):
        super(SpaceTime, self).__init__()

        self.nodes = []  # nodes is just a list of indicies
        self.node_x = {}  # a dict with node indices as keys
        self.node_t = {}  # a dict with node indices as keys

        self.faces = []  # faces is a list of node index tuples
        self.face_dilaton = {}  # a dict with keys of face tuples
        self.face_x = {}  # a dict with keys of face tuples
        self.face_t = {}  # a dict with keys of face tuples

    def generate_flat(self, space_size, time_size):
        index = 0
        for t in range(time_size):
            start = index
            for x in range(space_size):
                self.nodes.append(index)
                left = start + (index - 1) % space_size
                right = start + (index + 1) % space_size
                self.node_x[index] = [left, right]
                future_start = (start + space_size) % (space_size * time_size)
                past_start = (start - space_size) % (space_size * time_size)

                future_right = future_start + (index + 1) % space_size
                future = future_start + (index) % space_size
                past_left = past_start + (index - 1) % space_size
                past = past_start + (index) % space_size
                self.node_t[index] = [
                    future,
                    future_right,
                    past,
                    past_left,
                ]

                f1 = frozenset({index, right, future_right})
                f2 = frozenset({index, left, past_left})
                self.faces.append(f1)
                self.faces.append(f2)

                self.face_dilaton[f1] = 1
                self.face_dilaton[f2] = 1

                self.face_x[f1] = [
                    frozenset({index, future_right, future}),
                    frozenset(
                        {right, future_right, future_start + (index + 2) % space_size}
                    ),
                ]

                self.face_x[f2] = [
                    frozenset({index, past, past_left}),
                    frozenset({left, past_left, past_start + (index - 2) % space_size}),
                ]
                self.face_t[f1] = frozenset({index, right, past})
                self.face_t[f2] = frozenset({index, left, future})
                index += 1

    def move(self, node, future, past):
        pass


from scipy.sparse import coo_matrix

a = SpaceTime()
a.generate_flat(5, 10)
data = []
row = []
col = []

idx = 0
map = {}
for i in a.faces:
    map[i] = idx
    idx += 1
    connections = a.face_x[i]
    for c in connections:
        row.append(i)
        col.append(c)
        if isinstance(c, int):
            print("FAIL")
        data.append(1)
    connections = a.face_t[i]

    row.append(i)
    col.append(connections)
    data.append(2)

for i in range(len(data)):
    # print(col[i])
    row[i] = map[row[i]]
    col[i] = map[col[i]]

import matplotlib.pyplot as plt

plt.imshow(coo_matrix((data, (row, col))).toarray())
plt.show()
# print(a.node_x[10])
