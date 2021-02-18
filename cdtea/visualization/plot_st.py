import plotly.graph_objects as go
from matplotlib.collections import LineCollection
import random
from cdtea.visualization.coordinates import *


# 3d plots

def plot_3d(st, type="torus", name="temp_plot", get_coords=get_naive_coords, outer_radius=2, inner_radius=1):
    """
    Generate a 3d plot of the space-time embedded in the surface of a torus.
    """

    theta_x, theta_t = get_coords(st)
    x, y, z, i, j, k, color = [], [], [], [], [], [], []

    idx = 0
    node_to_idx = {}  # maps an event to an index.

    # loop through each node and append its coordinates
    for n in st.nodes:
        node_to_idx[n] = idx
        v = theta_x[n]
        u = theta_t[n]

        if type == "torus":
            x.append((outer_radius + inner_radius * np.cos(v)) * np.cos(u))
            y.append((outer_radius + inner_radius * np.cos(v)) * np.sin(u))
            z.append(inner_radius * np.sin(v))

        if type == "cylinder":
            x.append(inner_radius * np.cos(v))
            y.append(inner_radius * np.sin(v))
            z.append(inner_radius  * u)

        """
        new types can be added here
        """

        idx += 1

    for face in st.faces:
        face = list(face)

        i.append(node_to_idx[face[0]])
        j.append(node_to_idx[face[1]])
        k.append(node_to_idx[face[2]])

        color.append((random.random() * 255., random.random() * 255., random.random() * 255.))

    # TODO forward extra args so they can be used here
    fig = go.Figure(data=[
        go.Mesh3d(
            x=x,
            y=y,
            z=z,

            # i, j and k give the vertices of triangles
            i=i,
            j=j,
            k=k,

            flatshading=True,
            facecolor=color
        )
    ])

    fig.show()


# 2d plot (cutting a space and time slice)

def plot_2d(st, offeset=2 * pi / 600.):
    theta_x, theta_t = get_average_coords(st)
    #

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
    edges_left_pointing = []
    edges_right_pointing = []

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
                            coords[e.key] + np.array([0, offeset]),
                            coords[adjacent.key] + np.array([0, offeset]),
                        ]
                    )
        for adjacent in e.future:
            if abs(theta_t[e.key] - theta_t[adjacent.key]) < pi:
                if abs(theta_x[e.key] - theta_x[adjacent.key]) < pi:
                    edges_future_pointing.append(
                        [
                            coords[e.key] - np.array([0, offeset]),
                            coords[adjacent.key] - np.array([0, offeset]),
                        ]
                    )

        if abs(theta_t[e.key] - theta_t[e.left.key]) < pi:
            if abs(theta_x[e.key] - theta_x[e.left.key]) < pi:
                edges_left_pointing.append(
                    [
                        coords[e.key] + np.array([0, offeset]),
                        coords[e.left.key] + np.array([0, offeset]),
                    ]
                )

        if abs(theta_t[e.key] - theta_t[e.right.key]) < pi:
            if abs(theta_x[e.key] - theta_x[e.right.key]) < pi:
                edges_right_pointing.append(
                    [
                        coords[e.key] + np.array([0, -offeset]),
                        coords[e.right.key] + np.array([0, -offeset]),
                    ]
                )

    plt.gca().add_collection(
        LineCollection(
            edges_future_pointing, color=(1, 0, 0, 1), antialiaseds=True, linewidth=0.6,
        )
    )
    plt.gca().add_collection(
        LineCollection(
            edges_past_pointing, color=(0, 0, 1, 1), antialiaseds=True, linewidth=0.6,
        )
    )
    plt.gca().add_collection(
        LineCollection(
            edges_left_pointing, color=(0, 1, 0, 1), antialiaseds=True, linewidth=0.6,
        )
    )
    plt.gca().add_collection(
        LineCollection(
            edges_right_pointing, color=(.5, 0, .5, 1), antialiaseds=True, linewidth=0.6,
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
