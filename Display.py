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
        n = st.node_left[n]
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
            future = st.node_future[n]
            value1 = 0
            value2 = 0
            for p in past:
                theta = theta_x[p]
                value1 += sin(theta)
                value2 += cos(theta)
            # for f in future:
            #     theta = theta_x[p]
            #     value1 += sin(theta)
            #     value2 += cos(theta)
            theta_x[n] = arctan2(value1, value2)

            n = st.node_right[n]
            if n in used:
                n = st.node_future[n][0]

    return (theta_x, theta_t)


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

    if shading is None:
        shading = {
            "flat": True,  # Flat or smooth shading of triangles
            "wireframe": True,
            "wire_width": 100,
            "wire_color": "black",  # Wireframe rendering
            "width": 600,
            "height": 600,  # Size of the viewer canvas
            "antialias": True,  # Antialising, might not work on all GPUs
            "scale": 2.0,  # Scaling of the model
            "side": "DoubleSide",  # FrontSide, BackSide or DoubleSide rendering of the triangles
            "colormap": "Spectral",
            "normalize": [None, None],  # Colormap and normalization for colors
            "background": "#222",  # Background color of the canvas
            "line_width": 1.0,
            "line_color": "black",  # Line properties of overlay lines
            "bbox": False,  # Enable plotting of bounding box
            "point_color": "red",
            "point_size": 0.01,  # Point properties of overlay points
        }
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
    colors = []
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
        if len(st.node_all_connections(n)) - 6 != 0:
            print(len(st.node_all_connections(n)) - 6)
        colors.append((len(st.node_all_connections(n)) - 6))
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
        arbitraryN = next(iter(face))

        # doesnt add triangles that span the inside of the cyl
        if all([abs(theta_t[n] - theta_t[arbitraryN]) < pi for n in face]):
            f.append(mapped_face)

    # mp.plot(np.array(v), filename="plots/test", shading={"point_size": 3})
    v = np.array(v)
    f = np.array(f)
    p = mp.plot(
        v,
        f,
        c=np.array(colors),
        filename="plots/test",
        shading=shading,
        return_plot=True,
    )


def plot_3d_cyl(st, shading=None):
    # remove the ignored time triangles! This only works for spetial geometries.

    if shading is None:
        shading = {
            "flat": True,  # Flat or smooth shading of triangles
            "wireframe": True,
            "wire_width": 0.001,
            "wire_color": "#222",  # Wireframe rendering
            "width": 600,
            "height": 600,  # Size of the viewer canvas
            "antialias": True,  # Antialising, might not work on all GPUs
            "scale": 1.5,  # Scaling of the model
            "side": "DoubleSide",  # FrontSide, BackSide or DoubleSide rendering of the triangles
            "colormap": "Spectral",
            "normalize": [None, None],  # Colormap and normalization for colors
            "background": "#222",  # Background color of the canvas
            "line_width": 1.0,
            "line_color": "black",  # Line properties of overlay lines
            "bbox": False,  # Enable plotting of bounding box
            "point_color": "red",
            "point_size": 0.01,  # Point properties of overlay points
        }
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
    colors = []
    for n in st.nodes:
        idx_to_node[idx] = n
        node_to_idx[n] = idx
        v = theta_x[n]
        u = theta_t[n]

        coords[n] = (
            v,
            u,
            0,
        )

        colors.append((len(st.node_all_connections(n)) - 6))
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
        arbitraryN = next(iter(face))

        # doesnt add triangles that span the inside of the cyl
        if all([abs(theta_t[n] - theta_t[arbitraryN]) < pi for n in face]):
            if all([abs(theta_x[n] - theta_x[arbitraryN]) < pi for n in face]):
                f.append(mapped_face)

    # mp.plot(np.array(v), filename="plots/test", shading={"point_size": 3})
    v = np.array(v)
    f = np.array(f)
    p = mp.plot(
        v,
        f,
        c=np.array(colors),
        filename="plots/test",
        shading=shading,
        return_plot=True,
    )


def plot_2d(st, offeset=0):
    theta_x, theta_t = get_smart_coords(st)
    theta_x, theta_t = get_naive_coords(st)

    import numpy as np
    from numpy import sin, cos
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    import random

    c = 3
    a = 1
    idx = 0
    idx_to_node = {}
    node_to_idx = {}
    coords = {}
    colors = []
    for n in st.nodes:
        idx_to_node[idx] = n
        node_to_idx[n] = idx
        v = theta_x[n]
        u = theta_t[n]

        coords[n] = (
            v,
            u,
        )

        colors.append((len(st.node_all_connections(n)) - 6))
        idx += 1

    x = [coords[n][0] for n in st.nodes]
    y = [coords[n][1] for n in st.nodes]

    plt.scatter(x, y)

    edges1 = []

    import itertools

    for face in st.faces:
        for pair in itertools.product(face, repeat=2):
            n1 = pair[0]
            n2 = pair[1]
            # doesnt add triangles that span the inside of the cyl
            if abs(theta_t[n1] - theta_t[n2]) < pi:
                if abs(theta_x[n1] - theta_x[n2]) < pi:
                    edges1.append(
                        [
                            coords[n1] - np.array([offeset, offeset]),
                            coords[n2] - np.array([offeset, offeset]),
                        ]
                    )

    edges2 = []

    import itertools

    for node in st.nodes:
        for adjacent in st.node_all_connections(node):
            if abs(theta_t[node] - theta_t[adjacent]) < pi:
                if abs(theta_x[node] - theta_x[adjacent]) < pi:
                    edges2.append(
                        [
                            coords[node] + np.array([offeset, offeset]),
                            coords[adjacent] + np.array([offeset, offeset]),
                        ]
                    )

    plt.gca().add_collection(
        LineCollection(
            edges1, color=(0.345, 0.0941, 0.2705, 1), antialiaseds=True, linewidth=4
        )
    )
    plt.gca().add_collection(
        LineCollection(edges2, color=(1, 0.764, 0, 1), antialiaseds=True)
    )
    # plt.gca().add_collection(
    #     LineCollection(mismatch, color=(0, 0, 0, 1), antialiaseds=True)
    # )
    plt.scatter(x, y, color="black", zorder=2)
    plt.show()
