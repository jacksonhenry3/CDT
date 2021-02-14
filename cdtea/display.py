import numpy as np
from math import pi
import math

# utility functions
from cdtea import event


def angular_seperation(theta_1, theta_2):
    res = -(((theta_1 - theta_2) + pi) % (2 * pi) - pi)
    if math.isnan(res):
        print()
        print(theta_1, theta_2)
        print("FAILED")
        quit()
    return res


def is_between(theta_1, theta_2, arg):
    # sanitize the angles
    start = theta_1 % (2 * pi)
    end = (theta_2) % (2 * pi)
    arg = arg % (2 * pi)

    # get how far aspart the bounds are and in what direction
    sep = angular_seperation(start, end)
    # get how far apart the arg is from the starting bound
    delta = angular_seperation(start, arg)

    # check if they are the same sign and check if delta is smaller than sep
    return sep / delta > 0 and abs(delta) < abs(sep)


# Adjacency matrices
# these need to be revamped


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


# coordinate definitions


def get_naive_coords(st):
    """
    Returns two dicts with (space angle , time angle)
    """
    layers = np.array(st.get_layers())
    T = len(layers)
    theta_x = []
    theta_t = []

    # this whole shift thing is, it think, unesescarily complicated, perhaps ther is a mod 2 pi that copuld deal with it like in the  time weighted coords function
    shift = -np.repeat(np.arange(0, T), 2)
    for t, layer in enumerate(layers):
        N = len(layer)
        slot_width = 2 * pi / N
        theta_x.append(
            np.roll(np.arange(N) + slot_width / 2.0, shift[t]) * slot_width
            + slot_width / 2.0 * (-t % 2)
        )
        theta_t.append(np.full(N, t) / T * 2 * pi)
    theta_x = theta_x
    theta_t = theta_t
    theta_x_dict = {}
    theta_t_dict = {}

    for t, layer in enumerate(layers):
        for x, n in enumerate(layer):
            theta_x_dict[n] = theta_x[t][x]
            theta_t_dict[n] = theta_t[t][x]

    return (theta_x_dict, theta_t_dict)


# def get_naive_coords(st):
#     """
#     Returns two dicts with (space angle , time angle)
#     """
#     layers = np.array(st.get_layers())
#     T = len(layers)
#     theta_x = []
#     theta_t = []
#
#     for t, layer in enumerate(layers):
#         N = len(layer)
#         slot_width = 2 * pi / N
#         theta_x.append((np.arange(N) + slot_width / 2.0) * slot_width)
#         theta_t.append(np.full(N, t) / T * 2 * pi)
#     theta_x = theta_x
#     theta_t = theta_t
#     theta_x_dict = {}
#     theta_t_dict = {}
#
#     for t, layer in enumerate(layers):
#         for x, n in enumerate(layer):
#             theta_x_dict[n] = theta_x[t][x]
#             theta_t_dict[n] = theta_t[t][x]
#
#     return (theta_x_dict, theta_t_dict)


def get_naive_layer_shift(st, theta_x=False, theta_t=False):
    if not theta_x or not theta_t:
        theta_x, theta_t = get_spring_coords(st)
    layers = st.get_layers()
    for t, layer in enumerate(layers[1:]):
        t += 1
        offset = 0
        for n in event.events(st, layer):
            d_offset = sum(
                [
                    angular_seperation(theta_x[n.key], theta_x[c.key]) / len(layer)
                    for c in n.past
                ]
            )
            print(d_offset)
            offset = offset + d_offset
        print(t)
        print(offset / len(layer))

        print()
        for m in layer:
            theta_x[m] = (theta_x[m] + offset / 2.0) % (2 * pi)

    return (theta_x, theta_t)


def get_time_weighted_coords(st):
    """
        Returns two dicts with (space angle , time angle)
        """
    layers = np.array(st.get_layers())
    T = len(layers)
    theta_x_dict = {}
    theta_t_dict = {}
    shift = -np.repeat(np.arange(0, T), 2)
    total_time_edges = [sum([len(st.node_t(n)) for n in layer]) for layer in layers]
    for t, layer in enumerate(layers):
        X = len(layer)
        slot_width = 2 * pi / total_time_edges[t]
        # this 4 should be replaced by a calcuation of the first node time connections
        node = layer[0]
        theta_x = len(st.node_t(node)) * slot_width / 2.0 * t
        for n in layer:
            theta_x = (theta_x + 1 / 2.0 * slot_width * len(st.node_t(n))) % (2 * pi)
            theta_x_dict[n] = theta_x
            theta_t_dict[n] = t / T * 2 * pi
            theta_x = (theta_x + 1 / 2.0 * slot_width * len(st.node_t(n))) % (2 * pi)
            prev_n = n

    return (theta_x_dict, theta_t_dict)


def get_average_coords(st):
    theta_x, theta_t = get_naive_coords(st)

    for i in range(200):
        for n in st.nodes:
            # print(n)
            # sums the x length of all connections to n
            total_x_length = sum(
                [
                    angular_seperation(theta_x[n], theta_x[c])
                    for c in st.node_all_connections(n)
                ]
            )
            print(angular_seperation(total_x_length, 0))
            # attempt to change posiotion by the total difference therby reducing the total difference to zero
            new_x_theta = (theta_x[n] + total_x_length / 200.0) % (2 * pi)
            l = theta_x[st.node_left[n]]
            r = theta_x[st.node_right[n]]

            if is_between(l, r, new_x_theta):
                theta_x[n] = new_x_theta

    return (theta_x, theta_t)


def get_spring_coords(st, dt=0.015, k=1.0, b=2.0):
    theta_x, theta_t = get_naive_coords(st)

    v = {n: 0 for n in st.nodes}

    for i in range(500):
        for n in event.events(st, st.nodes):
            # print(n)
            # sums the x length of all connections to n
            dx = sum([angular_seperation(theta_x[n.key], theta_x[c.key]) for c in n.temporal_neighbors])
            a = k * dx
            for c in n.spatial_neighbors:
                dx = angular_seperation(theta_x[n.key], theta_x[c.key])
                sign = dx / abs(dx)
                a -= sign * 0.07 / (dx ** 2)
            a -= b * v[n.key]
            vel = v[n.key] + a * dt
            new_x_theta = (theta_x[n.key] + vel * dt) % (2 * pi)

            l = theta_x[n.left.key]
            r = theta_x[n.right.key]

            error_l = angular_seperation(new_x_theta, l)
            error_r = angular_seperation(new_x_theta, r)
            bounds_sep = angular_seperation(l, r)
            if is_between(l, r, new_x_theta):
                v[n] = vel
                theta_x[n.key] = new_x_theta % (2 * pi)

            # elif abs(error_l) < abs(error_r):
            #     print(l, r, new_x_theta)
            #     print(error_l, error_r)
            #     theta_x[n] = l - error_l / abs(error_l) * bounds_sep / 10.0
            # elif abs(error_r) < abs(error_l):
            #     # print(error_l, error_r)
            #     theta_x[n] = r - error_r / abs(error_r) * bounds_sep / 10.0

    return (theta_x, theta_t)

    # def get_spring_coords(st, dt=0.015, k=1.0, b=2.0):
    theta_x, theta_t = get_naive_coords(st)

    v = {n: 0 for n in st.nodes}

    for i in range(500):
        for n in st.nodes:
            # print(n)
            # sums the x length of all connections to n

            dx = sum([angular_seperation(theta_x[n], theta_x[c]) for c in n.temporal_neighbors])
            # dxp = sum(
            #     [angular_seperation(theta_x[n], theta_x[c]) for c in st.node_past[n]]
            # )
            # dxf = sum(
            #     [angular_seperation(theta_x[n], theta_x[c]) for c in st.node_future[n]]
            # )

            # for future_node in st.node_future[n]:
            #     v[future_node] -= dxf * 0.02
            # for past_node in st.node_past[n]:
            #     v[past_node] -= dxp * 0.02

            a = k * dx / abs(dx) * abs(dx) ** 0.1
            a = 0.0
            for c in n.spatial_neighbors:
                dx = angular_seperation(theta_x[n], theta_x[c])
                sign = dx / abs(dx)
                a -= sign * 0.03 / (dx ** 2)
            a -= b * v[n]
            vel = v[n] + a * dt
            new_x_theta = (theta_x[n] + vel * dt) % (2 * pi)

            l = theta_x[n.left]
            r = theta_x[n.right]

            error_l = angular_seperation(new_x_theta, l)
            error_r = angular_seperation(new_x_theta, r)
            bounds_sep = angular_seperation(l, r)
            if is_between(l, r, new_x_theta):
                v[n] = vel
                theta_x[n] = new_x_theta

            elif abs(error_l) < abs(error_r):
                print(l, r, new_x_theta)
                print(error_l, error_r)
                theta_x[n] = l - error_l / abs(error_l) * bounds_sep / 10.0
            elif abs(error_r) < abs(error_l):
                # print(error_l, error_r)
                theta_x[n] = r - error_r / abs(error_r) * bounds_sep / 10.0

    return (theta_x, theta_t)


# 3d plots


def plot_3d_torus(st, shading=None):
    if shading is None:
        shading = {
            "flat": True,  # Flat or smooth shading of triangles
            "wireframe": True,
            "wire_width": 100,
            "wire_color": "white",  # Wireframe rendering
            "width": 1000,
            "height": 1000,  # Size of the viewer canvas
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
    theta_x, theta_t = get_spring_coords(st)

    import numpy as np
    from numpy import sin, cos
    import meshplot as mp

    mp.offline()

    c = 2
    a = 1
    idx = 0
    idx_to_node = {}
    node_to_idx = {}
    coords = {}
    c = []
    for n in st.nodes:
        idx_to_node[idx] = n
        node_to_idx[n] = idx
        v = theta_x[n]
        u = theta_t[n]
        c.append((len(st.node_all_connections(n)) - 6))

        coords[n] = ((c + a * cos(v)) * cos(u), (c + a * cos(v)) * sin(u), a * sin(v))
        idx += 1
    v = []
    f = []
    # c = []
    for i in range(idx):
        n = idx_to_node[i]
        v.append(coords[n])
    for face in st.faces:
        mapped_face = []
        for node in face:
            n = node
            mapped_face.append(node_to_idx[node])
        f.append(mapped_face)

    mp.plot(
        np.array(v), np.array(f), c=np.array(c), filename="plots/test", shading=shading
    )


# cutting a time slice
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
    theta_x, theta_t = get_spring_coords(st)

    import numpy as np
    from numpy import sin, cos
    import meshplot as mp

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
        # if len(st.node_all_connections(n)) - 6 != 0:
        #     print(len(st.node_all_connections(n)) - 6)
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


# 2d plots (cutting a space and time slice)


def plot_2d(st, offeset=0):
    theta_x, theta_t = get_naive_coords(st)
    #
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    c = 3
    a = 1
    idx = 0
    idx_to_node = {}
    node_to_idx = {}
    coords = {}
    colors = []
    for n in event.events(st, st.nodes):
        idx_to_node[idx] = n.key
        node_to_idx[n.key] = idx
        v = theta_x[n.key]
        u = theta_t[n.key]

        coords[n.key] = (
            v,
            u,
        )

        # colors.append((len(n.neighbors) - 6))
        idx += 1

    x = [coords[n][0] for n in st.nodes]
    y = [coords[n][1] for n in st.nodes]

    edges1 = []

    import itertools

    # for face in st.faces:
    #     for pair in itertools.combinations(face, 2):
    #         n1 = pair[0]
    #         n2 = pair[1]
    #         # doesnt add triangles that span the inside of the cyl
    #         if abs(theta_t[n1] - theta_t[n2]) < pi:
    #             if abs(theta_x[n1] - theta_x[n2]) < pi:
    #                 edges1.append(
    #                     [
    #                         coords[n1] - np.array([offeset, offeset]),
    #                         coords[n2] - np.array([offeset, offeset]),
    #                     ]
    #                 )

    edges2 = []

    edges_past_pointing = []
    edges_future_pointing = []
    edges_space_pointing = []

    for e in event.events(st, st.nodes):
        past_asj = None
        for adjacent in e.past:
            if past_asj == adjacent:
                print(adjacent)
            past_asj = adjacent
            if abs(theta_t[e.key] - theta_t[adjacent.key]) < pi:
                if abs(theta_x[e.key] - theta_x[adjacent.key]) < pi:
                    edges_past_pointing.append(
                        [
                            coords[e.key] + np.array([offeset, offeset]),
                            coords[adjacent.key] + np.array([offeset, offeset]),
                        ]
                    )
        for adjacent in e.future:
            if abs(theta_t[e.key] - theta_t[adjacent.key]) < pi:
                if abs(theta_x[e.key] - theta_x[adjacent.key]) < pi:
                    edges_future_pointing.append(
                        [
                            coords[e.key] + np.array([offeset, offeset]),
                            coords[adjacent.key] + np.array([offeset, offeset]),
                        ]
                    )
        for adjacent in e.spatial_neighbors:
            if abs(theta_t[e.key] - theta_t[adjacent.key]) < pi:
                if abs(theta_x[e.key] - theta_x[adjacent.key]) < pi:
                    edges_space_pointing.append(
                        [
                            coords[e.key] + np.array([offeset, offeset]),
                            coords[adjacent.key] + np.array([offeset, offeset]),
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
    # plt.axis("off")
    plt.show()
