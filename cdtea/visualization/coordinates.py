import numpy as np
from math import pi
from cdtea import event
import math

"""
a coordinate function is one that takes in a spacetime and outputs a dictionairy with node indices as keys and coordinate tuples as values.
"""


# utility functions
# finds the minimum angular distance beween two given angles
def angular_seperation(theta_1, theta_2):
    res = -(((theta_1 - theta_2) + pi) % (2 * pi) - pi)
    if math.isnan(res):
        print()
        print(theta_1, theta_2)
        print("FAILED")
        quit()
    return res


# returns a boole describing if arg is between theta_1 and theta_2 in the shortest direction
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


# gives the total legnth of all edges in a layout.
def total_length(coords):
    pass


# coordinate definitions

def get_naive_coords(st):
    """
    Returns two dicts with (space angle , time angle)
    """
    layers = st.get_layers()
    T = len(layers)
    theta_x = {}
    theta_t = {}

    for t, layer in enumerate(layers):
        N = len(layer)
        slot_width = 2 * pi / N
        for x, n in enumerate(layer):
            theta_x[n] = ((x + t / 2.) * slot_width) % (2 * pi)
            theta_t[n] = t / T * 2 * pi

    return theta_x, theta_t


def untwist(coords, st):
    """
    It is common for coordinates to become "twisted" meaning for example, that the past layer is left shifted while the  future layer is right shifted. this occurs becouse most
    measures weight past and future edge lengths similarly so the minimum edge length that can be reached by adjusting a single node adds a twist.
    """
    theta_x, theta_t = coords
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

            offset = offset + d_offset
        for m in layer:
            theta_x[m] = (theta_x[m] + offset / 2.0) % (2 * pi)

    return theta_x, theta_t


def get_average_coords(st):
    theta_x, theta_t = get_naive_coords(st)

    for i in range(200):
        # print(i)
        for n in st.nodes:
            # print(n)
            # sums the x length of all connections to n
            e = event.Event(st, n)

            total_x_length = sum(
                [
                    angular_seperation(theta_x[n], theta_x[c.key])
                    for c in e.neighbors
                ]
            )
            # print(angular_seperation(total_x_length, 0))
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
