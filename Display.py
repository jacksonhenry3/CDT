import numpy as np
from numpy import arctan2, cos, sin
from math import pi
import matplotlib.pyplot as plt


def show_face_adjacency_matrix(st):
    # This visualizes the simplex ajacency matrix

    data = []
    row = []
    col = []

    # each simplex maps to a unique ID
    idx = 0
    map = {}

    # Loop through each simplex
    for i in st.faces:
        map[i] = idx  # generate the map
        idx += 1
        connections = st.face_x[i]  # Get both spatial connections
        for c in connections:
            row.append(i)  # add face i (a,b,c)
            col.append(c)  # add face c to cols
            data.append(1)  # The values of the connection between c and i

        # repeat the process for the time like connection
        connections = st.face_t[i]

        row.append(i)
        col.append(connections)
        data.append(2)

    for i in range(len(data)):
        # print(col[i])
        row[i] = map[row[i]]
        col[i] = map[col[i]]

    dense_dat = np.zeros((len(st.faces), len(st.faces)))
    for i in range(len(data)):
        dense_dat[col[i], row[i]] = data[i]

    import matplotlib.pyplot as plt

    plt.imshow(dense_dat, interpolation="none")
    plt.show()


def show_node_adjacency_matrix(st):
    # This visualizes the vertex ajacency matrix

    data = []
    row = []
    col = []

    # Loop through each simplex
    # print(len(st.nodes))
    map = {}
    for idx, node in enumerate(st.nodes):
        map[node] = idx

    for i in st.nodes:
        connections = st.node_x(i)  # Get both spatial connections
        for c in connections:
            row.append(map[i])  # add vertex i to rows
            col.append(map[c])  # add vertex c to cols
            data.append(1)  # The values of the connection between c and i

        # repeat the process for the time like connection
        connections = st.node_t(i)
        for c in connections:
            row.append(map[i])  # add vertex i to rows
            col.append(map[c])  # add vertex c to cols
            data.append(2)  # The values of the connection between c and i

    dense_dat = np.zeros((len(st.nodes), len(st.nodes)))
    for i in range(len(data)):
        dense_dat[col[i], row[i]] = data[i]

    import matplotlib.pyplot as plt

    plt.axis("off")
    plt.imshow(dense_dat, interpolation="none")

    plt.show()


def get_naive_coords(st):
    """
    Returns two dicts with (space angle , time angle)
    """
    used = []
    n = st.nodes[0]

    X = {}
    T = {}
    x = 0
    t = 0

    while n not in used:
        used.append(n)
        X[n] = x
        T[n] = t
        x += 1
        n = st.node_right[n]
        if n in used:
            x = 0
            t += 1
            n = st.node_future[n][0]

    max_x = max(X.values())
    max_t = max(T.values())
    theta_x = {n: X[n] / max_x * 2 * pi for n in st.nodes}
    theta_t = {n: T[n] / max_t * 2 * pi for n in st.nodes}
    return (theta_x, theta_t)


def get_smart_coords(st):
    theta_x, theta_t = get_naive_coords(st)

    for i in range(100):
        used = []
        n = st.nodes[0]
        while n not in used:
            used.append(n)

            past = st.node_past[n]
            value1 = 0
            value2 = 0
            for p in past:
                theta = theta_x[p]
                value1 += sin(theta)
                value2 += cos(theta)
            theta_x[n] = arctan2(value1, value2)

            n = st.node_right[n]
            if n in used:
                n = st.node_future[n][0]

    return (theta_x, theta_t)


def plot_2d(st):
    theta_x, theta_t = get_smart_coords(st)

    x_pnts = []
    y_pnts = []
    for n in st.nodes:
        x_pnts.append(theta_x[n])
        y_pnts.append(theta_t[n])
    plt.scatter(x_pnts, y_pnts)
    plt.show()


def plot_3d_torus(st, shading=None):
    theta_x, theta_t = get_smart_coords(st)

    import numpy as np
    from numpy import sin, cos
    import meshplot as mp
    import random

    mp.offline()

    c = 2
    a = 1
    idx = 0
    idx_to_node = {}
    node_to_idx = {}
    coords = {}
    for n in st.nodes:
        idx_to_node[idx] = n
        node_to_idx[n] = idx
        v = theta_x[n]
        u = theta_t[n]

        coords[n] = ((c + a * cos(v)) * cos(u), (c + a * cos(v)) * sin(u), a * sin(v))
        idx += 1
    v = []
    f = []
    c = []
    for i in range(idx):
        n = idx_to_node[i]
        v.append(coords[n])
    for face in st.faces:
        mapped_face = []
        for node in face:
            n = node
            mapped_face.append(node_to_idx[node])
        f.append(mapped_face)

        c.append([0, 0, st.face_dilaton[face]])

    mp.plot(
        np.array(v), np.array(f), c=np.array(c), filename="plots/test", shading=shading
    )


def plot_3d_cyl(st, shading=None):
    # remove the ignored time triangles! This only works for spetial geometries.
    theta_x, theta_t = get_smart_coords(st)

    import numpy as np
    from numpy import sin, cos
    import meshplot as mp
    import random

    mp.offline()

    c = 3
    a = 1
    idx = 0
    idx_to_node = {}
    node_to_idx = {}
    coords = {}
    for n in st.nodes:
        idx_to_node[idx] = n
        node_to_idx[n] = idx
        v = theta_x[n]
        u = theta_t[n]

        coords[n] = (
            (c + 0.01 * cos(u + pi)) * cos(v),
            2 * u,
            (c + 0.01 * cos(u + pi)) * sin(v),
        )
        # coords[n] = (a * cos(v), a * cos(v), u * 10)
        idx += 1
    v = []
    f = []
    c = []
    for i in range(idx):
        n = idx_to_node[i]
        v.append(coords[n])

    for face in st.faces:
        col = 0
        mapped_face = []
        for node in face:
            n = node
            mapped_face.append(node_to_idx[node])
            col += len(st.node_all_connections(n)) - 6
        f.append(mapped_face)

        c.append([0, st.face_dilaton[face], st.face_dilaton[face]])
    # mp.plot(np.array(v), filename="plots/test", shading={"point_size": 3})
    mp.plot(
        np.array(v), np.array(f), c=np.array(c), filename="plots/test", shading=shading
    )
