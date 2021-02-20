import plotly.graph_objects as go
from matplotlib.collections import LineCollection
import random
from cdtea.visualization.coordinates import *
from plotly.offline import iplot, plot
import matplotlib.pyplot as plt

"""
Valuable details
 https://chart-studio.plotly.com/~empet/14742/mesh3d-with-intensity-tests/
 https://plotly.com/python/reference/mesh3d/
"""

# default styles
line_settings = {'opacity': 1, 'line': dict(color='rgb(20,20,20)', width=5)}
mesh_settings = {'opacity': .5}

# display configuration
no_axis = {'showbackground': False, 'showgrid': False, 'showline': False, 'showticklabels': False, 'ticks': '', 'title': '', 'zeroline': False}
layout = {'width': 1000, 'height': 1000, 'showlegend': False, 'scene': {'xaxis': no_axis, 'yaxis': no_axis, 'zaxis': no_axis}, 'hovermode': False}


def plotly_triangular_mesh(nodes, faces, face_color=None, node_color=None, name="", plot_edges=True, line_set=line_settings, mesh_set=mesh_settings):
    x, y, z = nodes
    i, j, k = faces

    mesh = {'type': 'mesh3d', 'x': x, 'y': y, 'z': z, 'i': i, 'j': j, 'k': k, 'name': name, 'hoverinfo': 'skip'}
    mesh = {**mesh, **mesh_set}
    if node_color:
        mesh["vertexcolor"] = node_color
    elif face_color:
        mesh["facecolor"] = face_color

    if plot_edges is False:  # the triangle sides are not plotted
        return [mesh]
    else:  # plot edges
        # define the lists x_e, y_e, z_e, of x, y, and z coordinates of edge end points for each triangle
        x_e, y_e, z_e = [], [], []

        for index in range(len(i)):
            # None separates data corresponding to two consecutive triangles
            x_e += [x[i[index]], x[j[index]], x[k[index]], x[i[index]]] + [None]
            y_e += [y[i[index]], y[j[index]], y[k[index]], y[i[index]]] + [None]
            z_e += [z[i[index]], z[j[index]], z[k[index]], z[i[index]]] + [None]

        lines = {'type': 'scatter3d', 'x': x_e, 'y': y_e, 'z': z_e, 'mode': 'lines', 'name': name}
        lines = {**lines, **line_set}

        return [mesh, lines]


# 3d plots

# color functions
# BROKEN, idealy prompts some change to space-time
def face_color_time_direction(face):
    import statistics
    T = len(st.get_layers())

    face = list(face)

    layers = [theta_t[n] for n in face]
    mode = statistics.mode(layers)
    outlier = [theta_t[n] for n in face if theta_t[n] != mode][0]

    # this colors past pointing triangles blue
    if mode > outlier:  # past pointing
        return ((0, 0, 200))
    # this colors future pointing triangles red
    elif mode < outlier:  # future pointing
        return ((200, 0, 0))


def node_color_random(n):
    return ((random.random(), random.random(), random.random()))


def plot_3d(st, type="torus", filename=None, get_coords=get_naive_coords, radius_1=2, radius_2=1, plot_edges=True, node_color_function=node_color_random):
    """
    Generate a 3d plot of the space-time embedded in the surface of a torus.
    """

    theta_x, theta_t = get_coords(st)
    x, y, z, i, j, k, color = [], [], [], [], [], [], []

    idx = 0
    node_to_idx = {}  # maps an event to an index.

    node_color = []

    # loop through each node and append its coordinates
    for n in st.nodes:
        node_to_idx[n] = idx
        v = theta_x[n]
        u = theta_t[n]

        # node color is set here
        node_color.append(node_color_function(n))

        if type == "torus":
            x.append((radius_1 + radius_2 * np.cos(v)) * np.cos(u))
            y.append((radius_1 + radius_2 * np.cos(v)) * np.sin(u))
            z.append(radius_2 * np.sin(v))

        if type == "cylinder":
            x.append(radius_2 * np.cos(v))
            y.append(radius_2 * np.sin(v))
            z.append(radius_2 * u * np.sqrt(3) / 2.)

        """
        new types can be added here
        """

        idx += 1

    face_color = []

    for face in st.faces:
        face = list(face)

        # doesn't draw any triangles that would stretch across two time slices. This removes the middle triangles connecting the top to the bottom
        # needs more info from space time to find triangle orientation, should this be stored in each triangle?
        # if type == "cylinder" and abs(mode - outlier) > 2 * pi / T * 2:
        #     continue

        i.append(node_to_idx[face[0]])
        j.append(node_to_idx[face[1]])
        k.append(node_to_idx[face[2]])

    # generate the mesh
    data = plotly_triangular_mesh((x, y, z), (i, j, k), face_color=face_color, node_color=node_color, name=filename, plot_edges=plot_edges)

    layout["title"] = filename
    fig = dict(data=data, layout=layout)

    if filename:
        plot(fig, filename="./" + filename + ".html")
    else:
        iplot(fig)


# 2d plot (cutting a space and time slice)

def plot_2d(st, offeset=2 * pi / 600., get_coords=get_naive_coords):
    theta_x, theta_t = get_coords(st)

    idx = 0
    coords = {}
    colors = []
    for n in event.events(st, st.nodes):
        v = theta_x[n.key]
        u = theta_t[n.key]

        coords[n.key] = (v, u)

        colors.append((len(n.neighbors) - 6))
        idx += 1

    x = [coords[n][0] for n in st.nodes]
    y = [coords[n][1] for n in st.nodes]

    edges1 = []

    # import itertools
    #
    xx, yy = [], []
    for face in st.faces:
        face = list(face)
        xx, yy = [], []
        if max([abs(theta_t[face[0]] - theta_t[face[1]]), abs(theta_t[face[0]] - theta_t[face[2]])]) < pi:
            if max([abs(theta_x[face[0]] - theta_x[face[1]]), abs(theta_x[face[0]] - theta_x[face[2]])]) < pi:
                print(face)
                for n in face:
                    xx.append(theta_x[n])
                    yy.append(theta_t[n])
                avg_x = np.mean(xx)
                avg_y = np.mean(yy)
                xx = [p - (p-avg_x) / 5. for p in xx]
                yy = [p - (p-avg_y) / 5. for p in yy]
                plt.fill(xx, yy, c=(1, 0, 0, .1))

    edges_past_pointing, edges_future_pointing, edges_left_pointing, edges_right_pointing = [], [], [], []

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

    plt.scatter(x, y, color="white", zorder=2, s=300, edgecolors="black")

    for n in st.nodes:
        plt.annotate(n, coords[n], va="center", ha="center", c="black")

    plt.axis("off")
    plt.show()
