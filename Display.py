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
    layers = np.array(st.get_layers())
    T = len(layers)
    theta_x = []
    theta_t = []

    for t, layer in enumerate(layers):
        N = len(layer)
        # print(N)
        theta_x.append(np.arange(N) / N * 2 * pi)
        theta_t.append(np.full(N, t) / T * 2 * pi)
    theta_x = theta_x
    theta_t = theta_t
    theta_x_dict = {}
    theta_t_dict = {}
    # print(theta_t)
    # print(theta_x)
    for t, layer in enumerate(layers):
        for x, n in enumerate(layer):
            theta_x_dict[n] = theta_x[t][x]
            theta_t_dict[n] = theta_t[t][x]

    return (theta_x_dict, theta_t_dict)


import math


def get_smart_coords(st):
    theta_x, theta_t = get_naive_coords(st)
    layers = st.get_layers()

    for layer in layers:
        layer_total = 0
        for n in layer:
            for connection in st.node_all_connections(n):
                delta = theta_x[connection] - theta_x[n]
                delta = (delta + pi) % (2 * pi) - pi
                layer_total += delta
        layer_avg = layer_total / len(layer)
        print(layer_avg)
        for n in layer:
            theta_x[n] += layer_avg / 2

    return (theta_x, theta_t)


def angular_seperation(theta_1, theta_2):
    return -(((theta_1 - theta_2) + pi) % (2 * pi) - pi)


def plot_3d_torus(st, shading=None):
    if shading is None:
        shading = {
            "flat": True,  # Flat or smooth shading of triangles
            "wireframe": True,
            "wire_width": 100,
            "wire_color": "white",  # Wireframe rendering
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


def plot_3d_cyl_SDFIKSJDBFSJDIFB(st, shading=None):
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
    # theta_x, theta_t = get_smart_coords_old(st)
    theta_x, theta_t = get_smart_coords(st)
    #
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

    edges1 = []

    import itertools

    for face in st.faces:
        for pair in itertools.combinations(face, 2):
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

    edges_past_pointing = []
    edges_future_pointing = []
    edges_space_pointing = []
    import itertools

    for node in st.nodes:
        past_asj = None
        for adjacent in st.node_past[node]:
            if past_asj == adjacent:
                print(adjacent)
            past_asj = adjacent
            if abs(theta_t[node] - theta_t[adjacent]) < pi:
                if abs(theta_x[node] - theta_x[adjacent]) < pi:
                    edges_past_pointing.append(
                        [
                            coords[node] + np.array([offeset, offeset]),
                            coords[adjacent] + np.array([offeset, offeset]),
                        ]
                    )
        for adjacent in st.node_future[node]:
            if abs(theta_t[node] - theta_t[adjacent]) < pi:
                if abs(theta_x[node] - theta_x[adjacent]) < pi:
                    edges_future_pointing.append(
                        [
                            coords[node] + np.array([offeset, offeset]),
                            coords[adjacent] + np.array([offeset, offeset]),
                        ]
                    )
        for adjacent in st.node_x(node):
            if abs(theta_t[node] - theta_t[adjacent]) < pi:
                if abs(theta_x[node] - theta_x[adjacent]) < pi:
                    edges_space_pointing.append(
                        [
                            coords[node] + np.array([offeset, offeset]),
                            coords[adjacent] + np.array([offeset, offeset]),
                        ]
                    )

    plt.gca().add_collection(
        LineCollection(
            edges_future_pointing, color=(0, 0, 0, 1), antialiaseds=True, linewidth=0.6,
        )
    )
    plt.gca().add_collection(
        LineCollection(
            edges_past_pointing, color=(0, 0, 0, 1), antialiaseds=True, linewidth=0.6,
        )
    )
    plt.gca().add_collection(
        LineCollection(
            edges_space_pointing, color=(0, 0, 0, 1), antialiaseds=True, linewidth=0.6,
        )
    )
    # plt.gca().add_collection(
    #     LineCollection(edges2, color=(0, 0, 1, 0.1), antialiaseds=True, linewidth=3)
    # )
    # plt.gca().add_collection(
    #     LineCollection(mismatch, color=(0, 0, 0, 1), antialiaseds=True)
    # )
    plt.scatter(x, y, color="white", zorder=2, s=300, edgecolors="black")

    # for n in st.nodes:
    #     plt.annotate(
    #         n, coords[n], backgroundcolor="white", va="center", ha="center",
    #     )
    for n in st.nodes:
        plt.annotate(n, coords[n], va="center", ha="center", c="black")
    # plt.legend(
    #     ("nodes", "Triangles", "node connections"), loc="upper right", shadow=True
    # )
    plt.show()
