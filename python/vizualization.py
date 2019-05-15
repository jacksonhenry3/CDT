import numpy as np
from numpy import sin, cos
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D


def get_coordinates(space_time, radius=5):

    cyl_coord_dict = {}

    num_nodes_in_space_slice = space_time.space_slice_sizes[0]

    d_theta = 2 * np.pi / num_nodes_in_space_slice
    theta = 0
    h = 0

    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        cyl_coord_dict[current_zero_level_node] = [theta, h]
        theta += d_theta

        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right
    for time_index in range(1, space_time.num_time_slices):
        for index, n in space_time.nodes.items():
            if n.time_index == time_index:
                past_angles = []
                for past_index, past_node in n.past.items():
                    # print(n)current_zero_level_node
                    past_angles.append(cyl_coord_dict[past_node][0])
                # past_angles = [cyl_coord_dict[past][0] for past in n.past]
                theta = np.arctan2(
                    1 / len(n.past) * np.sum(sin(past_angles)),
                    1 / len(n.past) * np.sum(cos(past_angles)),
                )
                h = n.time_index
                cyl_coord_dict[n] = [theta, h]

    cart_coord_dict = {}

    for index, n in space_time.nodes.items():
        theta = cyl_coord_dict[n][0]
        h = cyl_coord_dict[n][1]
        cart_coord_dict[n] = [radius * cos(theta), radius * sin(theta), h]

    return cart_coord_dict


def space_time_mesh(space_time):

    coord_dict = get_coordinates(space_time)

    import plotly as py
    import plotly.graph_objs as go

    x = []
    y = []
    z = []
    for node, coord in coord_dict.items():
        x.append(coord[0])
        y.append(coord[1])
        z.append(coord[2])

    trace = go.Mesh3d(x=x, y=y, z=z, color="#FFB6C1", opacity=0.50)
    py.offline.iplot([trace])


def vizualize_space_time(space_time, radius=8 / (2 * np.pi)):

    cart_coord_dict = get_coordinates(space_time)
    x_coords = []
    y_coords = []
    z_coords = []

    for index, n in space_time.nodes.items():
        x_coords.append(cart_coord_dict[n][0])
        y_coords.append(cart_coord_dict[n][1])
        z_coords.append(cart_coord_dict[n][2])

    # This plots the points
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(x_coords, y_coords, z_coords)

    # This plot the line between the points
    unused_nodes = space_time.nodes
    for index, n in unused_nodes.items():
        this_x = cart_coord_dict[n][0]
        this_y = cart_coord_dict[n][1]
        this_z = cart_coord_dict[n][2]

        adjacent_nodes = [n.right] + list(n.future.values())

        for adjacent_node in adjacent_nodes:
            if (adjacent_node.time_index - n.time_index) in [0, 1, -1]:
                adjacent_node_x = cart_coord_dict[adjacent_node][0]
                adjacent_node_y = cart_coord_dict[adjacent_node][1]
                adjacent_node_z = cart_coord_dict[adjacent_node][2]
                ax.plot(
                    [this_x, adjacent_node_x],
                    [this_y, adjacent_node_y],
                    [this_z, adjacent_node_z],
                    "Black",
                )
    ax.set_aspect(1.0)
    plt.show()


"""
def vizualize_space_time_flattened(space_time, radius=5):
    coord_dict = {}

    d_x = 1
    x = 0
    h = 0

    unused_zero_level_nodes = [n for n in space_time.nodes if n.time_index == 0]
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        coord_dict[current_zero_level_node] = [x, h]
        x += d_x

        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right

    plotted_nodes = []
    for time_index in range(1, space_time.num_time_slices):
        for n in space_time.nodes:
            if n.time_index == time_index:
                past_x = []
                for past in n.past:
                    past_x.append(coord_dict[past][0])
                    # 5 is random
                if np.max(past_x) - np.min(past_x) < 2.1:
                    plotted_nodes.append(n)
                x = np.mean(past_x)
                h = n.time_index
                coord_dict[n] = [x, h]

    x_coords = []
    y_coords = []

    for n in space_time.nodes:
        x_coords.append(coord_dict[n][0])
        y_coords.append(coord_dict[n][1])

    # This plots the points
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x_coords, y_coords)

    # This plots the line between the points
    for n in plotted_nodes:
        this_x = coord_dict[n][0]
        this_y = coord_dict[n][1]

        adjacent_nodes = n.future

        for adjacent_node in adjacent_nodes:
            if (adjacent_node.time_index - n.time_index) == 1:
                adjacent_node_x = coord_dict[adjacent_node][0]
                adjacent_node_y = coord_dict[adjacent_node][1]
                ax.plot([this_x, adjacent_node_x], [this_y, adjacent_node_y], "Black")

    plt.show()
"""


def get_flattened_coordinates(space_time):
    coords_dict = {}

    d_x = 1
    x = 0
    y = 0

    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        coords_dict[current_zero_level_node] = [x, y]
        x += d_x

        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right

    for time_index in range(1, space_time.num_time_slices):
        for index, n in space_time.nodes.items():
            if n.time_index == time_index:
                past_x = []
                for past_index, past_node in n.past.items():
                    past_x.append(coords_dict[past_node][0])
                # x = np.mean(np.array(past_x)) - (1 + (-1) ** (n.time_index)) * 0.5
                # if np.mean(np.abs(past_x - np.mean(x))) > 3:
                #     x = 7 + (1 + (-1) ** (n.time_index - 1)) * 0.25
                x = np.mean(np.array(past_x))
                if np.mean(np.abs(past_x - np.mean(x))) > 3:
                    x = 15 + 0.5 * n.time_index

                y = n.time_index
                coords_dict[n] = [x, y]
    return coords_dict


def get_flattened_coordinates_dumb(space_time):

    coords_dict = {}
    used_node_indeces = []
    # current_node_index = list(space_time.nodes.keys())[0]
    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]
    current_node_index = unused_zero_level_nodes[0].index
    x = 0
    y = 0
    for index, n in space_time.nodes.items():
        used_node_indeces.append(current_node_index)
        current_node = space_time.nodes[current_node_index]
        coords_dict[current_node] = [
            x - space_time.space_slice_sizes[current_node.time_index] * 0.5,
            y,
        ]

        if current_node.right.index not in used_node_indeces:
            current_node_index = current_node.right.index
            x += 1
        elif np.min(list(current_node.right.future.keys())) not in used_node_indeces:
            current_node_index = np.min(list(current_node.right.future.keys()))
            x = 0
            y += 1
        else:
            break

    return coords_dict


def get_flattened_circular_coordinates(space_time, r0=1):
    coords_dict = {}
    num_spokes = space_time.space_slice_sizes[0]

    d_theta = 2 * np.pi / num_spokes
    theta = -np.pi
    r = r0

    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        coords_dict[current_zero_level_node] = [r, theta]
        theta += d_theta
        print(theta)

        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right

    for time_index in range(1, space_time.num_time_slices):
        # print(range(1, space_time.num_time_slices))
        for index, n in space_time.nodes.items():
            if n.time_index == time_index:
                num_spokes = space_time.space_slice_sizes[time_index]
                d_theta = 2 * np.pi / num_spokes
                # print(n)
                past_theta = []
                for past_index, past_node in n.past.items():
                    past_theta.append(coords_dict[past_node][1])
                theta = np.arctan2(
                    1 / len(n.past) * np.sum(sin(past_theta)),
                    1 / len(n.past) * np.sum(cos(past_theta)),
                )

                y = n.time_index
                coords_dict[n] = [r0 + y / 10.0, theta]
    for index, n in space_time.nodes.items():
        r = coords_dict[n][0]
        theta = coords_dict[n][1]
        coords_dict[n] = [
            r * np.cos((theta) + np.pi / 2.0),
            r * np.sin((theta) + np.pi / 2.0),
        ]

    return coords_dict


def vizualize_space_time_flattened(space_time):
    coord_dict = get_flattened_coordinates_dumb(space_time)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # theta = np.linspace(0, 2 * np.pi, 100)
    # for r in np.arange(0, space_time.num_time_slices / 1000.0, 1 / 1000.0):
    #    ax.plot((1 + r) * np.cos(theta), (1 + r) * np.sin(theta), "Blue")

    # removes the past from zero level nodes
    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        current_zero_level_node.replace_past([])
        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right

    # This plots the line between the points
    for n in space_time.nodes.values():
        this_x = coord_dict[n][0]
        this_y = coord_dict[n][1]

        adjacent_nodes = list(n.future.values())
        # print(n.left)
        adjacent_nodes.append(n.left)
        for adjacent_node in adjacent_nodes:
            adjacent_node_x = coord_dict[adjacent_node][0]
            adjacent_node_y = coord_dict[adjacent_node][1]
            if (this_x - adjacent_node_x) ** 2 + (
                this_y - adjacent_node_y
            ) ** 2 < 10 ** 5:
                ax.plot([this_x, adjacent_node_x], [this_y, adjacent_node_y], "Black")
    for node, coord in coord_dict.items():
        ax.scatter(coord[0], coord[1])
    plt.show()
