from cdtea.visualization.coordinates import *

# 3d plots
shading_config = {
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
    "point_size": 0.01  # Point properties of overlay points
}


def plot_3d_torus(st, shading=shading_config):
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
def plot_3d_cyl(st, shading=shading_config):
    # remove the ignored time triangles! This only works for spetial geometries.

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
    theta_x, theta_t = get_naive_layer_shift(st)
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

        colors.append((len(n.neighbors) - 6))
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
