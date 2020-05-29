import numpy as np
from numpy import sin, cos
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D

# idealy i would like to be able to create a proper 3d mesh with different
# colored triangles depending if they point up or down in time


def cylinder_coordinates_3d(space_time, radius=5):
    """
    gets coordinates such that space time is displayed on a 3d cylinder.

    It takes a spacetime as an argument and returns a dictionairy of
    nodes-> [x,y,z]
    """

    # dictionairy of node-> [r,theta,z]
    cyl_coord_dict = {}

    num_nodes_in_space_slice = space_time.space_slice_sizes[0]

    d_theta = 2 * np.pi / num_nodes_in_space_slice
    theta = 0
    h = 0

    # list of all nodes in a specific time slice chosen as the start
    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]

    #  loop through each zero level node and give it a location
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        cyl_coord_dict[current_zero_level_node] = [theta, h]
        theta += d_theta

        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right

    # loop through all nodes giving them a location based on the average
    # of all nodes they are connected to in the past
    for time_index in range(1, space_time.num_time_slices):
        for index, n in space_time.nodes.items():
            if n.time_index == time_index:
                past_angles = []
                for past_index, past_node in n.past.items():
                    # print(n)current_zero_level_node
                    past_angles.append(cyl_coord_dict[past_node][0])
                # past_angles = [cyl_coord_dict[past][0] for past in n.past]

                # this is an average over angles.
                theta = np.arctan2(
                    1 / len(n.past) * np.sum(sin(past_angles)),
                    1 / len(n.past) * np.sum(cos(past_angles)),
                )

                h = n.time_index
                cyl_coord_dict[n] = [theta, h]

    # the rest of this function just converts the coordinates to cartesian
    cart_coord_dict = {}

    for index, n in space_time.nodes.items():
        theta = cyl_coord_dict[n][0]
        h = cyl_coord_dict[n][1]
        cart_coord_dict[n] = [radius * cos(theta), radius * sin(theta), h]

    return cart_coord_dict


def get_rectangular_past_average_coordinates_2d(space_time):
    """
    creates a line of nodes at a particular time slice and choses the x
    position of nodes by the average of their past.

    this leads to wierd artifacts becouse some nodes have their past splits
    between both sides of the previous time layer making their average position
    very different from their past.
    """
    coords_dict = {}

    d_x = 1
    x = 0
    y = 0

    # list of all nodes in a specific time slice chosen as the start
    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]

    #  loop through each zero level node and give it a location
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        coords_dict[current_zero_level_node.index] = [x, y]
        print(current_zero_level_node.index)
        x += d_x

        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right

    # loop through all nodes giving them a location based on the average
    # of all nodes they are connected to in the past
    for time_index in range(1, space_time.num_time_slices):
        for index, n in space_time.nodes.items():
            if n.time_index == time_index:
                past_x = []
                print(str(time_index) + "============")
                for past_index in n.past:
                    print(past_index)
                    past_x.append(coords_dict[past_index][0])

                past_x = np.sort(past_x)

                # split the past in to sections in case the past nodes end up
                # on opposite sides
                g1 = [past_x[0]]

                # get all past nodes that are on the left
                for i in range(len(past_x) - 1):
                    if (
                        np.abs(past_x[i] - past_x[i + 1])
                        <= min(space_time.space_slice_sizes) / 2.0
                    ):
                        g1.append(past_x[i + 1])
                    else:
                        break

                # get all the remaining past nodes
                g2 = [x for x in past_x if x not in g1]

                lg1 = len(g1)
                lg2 = len(g2)

                # if the left and right are the same size alternate which side is used
                if lg1 == lg2:
                    if time_index % 2 == 0:
                        lg1 += 1
                    if time_index % 2 == 1:
                        lg2 += 1

                # if the left past is larger push the node left
                if lg1 >= lg2:
                    for x in g2:
                        g1.append(x - (max(past_x) + 1) + min(past_x))
                    g = g1

                # if the right past is larger push the node right
                elif lg2 >= lg1:
                    for x in g1:
                        g2.append(x + max(past_x) + 1)
                    g = g2

                x = np.mean(np.array(g))

                y = n.time_index

                print("added " + str(n.index))
                coords_dict[n.index] = [x, y]
    return coords_dict


def get_rectangular_naive_coordinates_2d(space_time):

    coords_dict = {}
    used_node_indices = []

    # list of all nodes in a specific time slice chosen as the start
    # This is technichally unnescairy, you could start at any node.
    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]

    # this should just select a random node
    current_node_index = unused_zero_level_nodes[0].index
    x = 0
    y = 0

    # loop through all nodes
    for index, n in space_time.nodes.items():

        # add the current node to a list of used nodes
        used_node_indices.append(current_node_index)
        current_node = space_time.nodes[current_node_index]

        # get the coordiantes for the current_node
        coords_dict[current_node] = [
            x - space_time.space_slice_sizes[current_node.time_index] * 0.5,
            y,
        ]

        # if the node to the right of current node has not been used do the next
        # iteration with that node and increment x position by 1.
        if current_node.right.index not in used_node_indices:
            current_node_index = current_node.right.index
            x += 1

        # If the node to the right has been used then an entire spatial slice
        # has been completed. Therfore we should reset the x position and
        # switch to the next time slice

        # this is where the problem of plotting something twice in a row manifests.
        # something is destroy current_node.right.future
        elif min(list(current_node.right.future.keys())) not in used_node_indices:
            current_node_index = min(list(current_node.right.future.keys()))
            x = 0
            y += 1
        else:
            break

    return coords_dict


def get_circular_coordinates_2d(space_time, r0=1):
    """
    gets coordinates where theta is spatial position and radius is time position
    """

    coords_dict = {}

    # the number of theta positions in the inner most level
    num_spokes = space_time.space_slice_sizes[0]

    d_theta = 2 * np.pi / num_spokes
    theta = -np.pi
    r = r0

    # list of all nodes in a specific time slice chosen as the start
    unused_zero_level_nodes = [
        n for index, n in space_time.nodes.items() if n.time_index == 0
    ]

    # loop through each zero level node and give it a location
    current_zero_level_node = unused_zero_level_nodes[0]
    while current_zero_level_node in unused_zero_level_nodes:
        coords_dict[current_zero_level_node] = [r, theta]
        theta += d_theta
        unused_zero_level_nodes.remove(current_zero_level_node)
        current_zero_level_node = current_zero_level_node.right

    # loops through all the other nodes
    for time_index in range(1, space_time.num_time_slices):
        for index, n in space_time.nodes.items():
            if n.time_index == time_index:
                num_spokes = space_time.space_slice_sizes[time_index]
                d_theta = 2 * np.pi / num_spokes
                past_theta = []
                for past_index, past_node in n.past.items():
                    past_theta.append(coords_dict[past_node][1])

                #  make the thea coordinate the average of thetas in nodes past.
                theta = np.arctan2(
                    1 / len(n.past) * np.sum(sin(past_theta)),
                    1 / len(n.past) * np.sum(cos(past_theta)),
                )

                y = n.time_index
                coords_dict[n] = [r0 + y / 10.0, theta]

    # convert to cartesian
    for index, n in space_time.nodes.items():
        r = coords_dict[n][0]
        theta = coords_dict[n][1]
        coords_dict[n] = [
            r * np.cos((theta) + np.pi / 2.0),
            r * np.sin((theta) + np.pi / 2.0),
        ]

    return coords_dict


def vizualize_space_time_2d(space_time, seed=0):
    np.random.seed(seed)

    # get the corodinate dictionairy
    coord_dict = get_rectangular_past_average_coordinates_2d(space_time)

    # find the minimum spatial size
    minSpaceSize = np.min(space_time.space_slice_sizes)

    fig = plt.figure()

    ax = fig.add_subplot(111)
    # ax.set_title(str(seed))

    # removes the past from zero level nodes
    # this should be unnescesary?
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
        this_x = coord_dict[n.index][0]
        this_y = coord_dict[n.index][1]

        # create a list of all adjacent nodes. I have chosen to include only the
        # right and future nodes so as not to double plot edges.
        adjacent_nodes = list(n.past)
        adjacent_nodes.append(n.left.index)

        for adjacent_node in adjacent_nodes:
            print(adjacent_node)
            adjacent_node_x = coord_dict[adjacent_node][0]
            adjacent_node_y = coord_dict[adjacent_node][1]

            # this wont plot deges that are to long (i.e longer than the
            # shortest spatial slice)
            if (this_x - adjacent_node_x) ** 2 + (this_y - adjacent_node_y) ** 2 < (
                minSpaceSize - 5
            ) ** 2:
                ax.plot(
                    [this_x, adjacent_node_x],
                    [this_y, adjacent_node_y],
                    "Black",
                    alpha=0.3,
                )

    # this draws the nodes
    # for node, coord in coord_dict.items():
    # ax.scatter(coord[0], coord[1],c = "blue")
    # ax.annotate(np.round(np.random.random(),2), (coord[0], coord[1]))

    # plt.savefig(str(seed) + ".png")
    plt.axis("off")
    plt.show()
    plt.close("all")


def vizualize_space_time_3d(space_time, radius=8 / (2 * np.pi)):
    """
    creates a 3d plot of the given space_time .
    """

    # seperate the x y and z coordinates in to their own lists.
    cart_coord_dict = cylinder_coordinates_3d(space_time)
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
