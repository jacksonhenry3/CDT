import plotly.graph_objects as go
from matplotlib.collections import LineCollection
import random
from cdtea.visualization.coordinates import *
from plotly.offline import iplot
import matplotlib.pyplot as plt

"""
Valuable details
 https://chart-studio.plotly.com/~empet/14742/mesh3d-with-intensity-tests/#/
 https://plotly.com/python/reference/mesh3d/
"""


def standard_intensity(x, y, z):
    return z


def plotly_triangular_mesh(x, y, z, i, j, k, fc, intensities=standard_intensity, colorscale="Viridis",
                           flatshading=True, showscale=False, reversescale=False, plot_edges=False):
    # vertices = a numpy array of shape (n_vertices, 3)
    # faces = a numpy array of shape (n_faces, 3) dtype=
    # intensities can be either a function of (x,y,z) or a list of values

    # if hasattr(intensities, '__call__'):
    #     intensity = intensities(x, y, z)  # the intensities are computed here via the set function,
    #     # that returns the list of vertices intensities
    # elif isinstance(intensities, (list, np.ndarray)):
    #     intensity = intensities  # intensities are given in a list
    # else:
    #     raise ValueError("intensities can be either a function or a list, np.array")

    mesh = dict(type='mesh3d',
                x=x,
                y=y,
                z=z,
                colorscale=colorscale,
                reversescale=reversescale,
                # intensity=intensity,
                flatshading=flatshading,
                i=i,
                j=j,
                k=k,
                name='',
                showscale=showscale,
                facecolor=fc
                # vertexcolor

                )

    if showscale is True:
        mesh.update(colorbar=dict(thickness=20, ticklen=4, len=0.75))

    if plot_edges is False:  # the triangle sides are not plotted
        return [mesh]
    else:  # plot edges
        # define the lists Xe, Ye, Ze, of x, y, resp z coordinates of edge end points for each triangle
        # None separates data corresponding to two consecutive triangles
        # tri_vertices = vertices[faces]
        Xe = []
        Ye = []
        Ze = []
        # for T in tri_vertices:
        #     Xe += [T[k % 3][0] for k in range(4)] + [None]
        #     Ye += [T[k % 3][1] for k in range(4)] + [None]
        #     Ze += [T[k % 3][2] for k in range(4)] + [None]
        for index in range(len(i)):
            Xe += [x[i[index]], x[j[index]], x[k[index]], x[i[index]]] + [None]
            Ye += [y[i[index]], y[j[index]], y[k[index]], y[i[index]]] + [None]
            Ze += [z[i[index]], z[j[index]], z[k[index]], z[i[index]]] + [None]
        # define the lines to be plotted
        lines = dict(type='scatter3d',
                     x=Xe,
                     y=Ye,
                     z=Ze,
                     mode='lines',
                     name='',
                     opacity=1,
                     line=dict(color='rgb(20,20,20)', width=5)

                     )

        return [mesh, lines]


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
            z.append(inner_radius * u * np.sqrt(3) / 2.)

        """
        new types can be added here
        """

        idx += 1
    fc = []
    import statistics
    for face in st.faces:
        face = list(face)

        i.append(node_to_idx[face[0]])
        j.append(node_to_idx[face[1]])
        k.append(node_to_idx[face[2]])
        layers = [theta_t[n] for n in face]
        mode = statistics.mode(layers)
        outlier = [theta_t[n]  for n in face if theta_t[n]!= mode][0]
        print(layers, mode, outlier)
        if mode > outlier: #downwards pointing
            print("a")
            fc.append((0, 0, 200))
        elif mode < outlier: #upwards pointing
            print("b")
            fc.append((200, 0, 0))
        else:
            print("?SDFSDFDSFSDFSDFSDFSDFSDDSFS?")


    data = plotly_triangular_mesh(x, y, z, i, j, k, fc, plot_edges=True)

    noaxis = dict(
        showbackground=False,
        showgrid=False,
        showline=False,
        showticklabels=False,
        ticks='',
        title='',
        zeroline=False)

    layout = dict(
        # title="Mesh 3d intensity test",
        width=1000,
        height=1000,
        showlegend=False,
        scene=dict(xaxis=noaxis,
                   yaxis=noaxis,
                   zaxis=noaxis,
                   # aspectratio=dict(x=1,
                   #                  y=1,
                   #                  z=2
                   #                  ),
                   camera=dict(eye=dict(x=1.55, y=-1.55, z=1.55)),
                   ),

        hovermode=False,

    )

    fig = dict(data=data, layout=layout)
    iplot(fig)

    # # TODO forward extra args so they can be used here
    # fig = go.Figure(data=[
    #     go.Mesh3d(
    #         x=x,
    #         y=y,
    #         z=z,
    #
    #         # i, j and k give the vertices of triangles
    #         i=i,
    #         j=j,
    #         k=k,
    #
    #         flatshading=True,
    #         facecolor=color
    #     )
    # ])
    #
    # fig.show()


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
