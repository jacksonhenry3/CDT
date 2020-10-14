import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
from matplotlib import collections as mc

# this disp displays all time-like lines as vertical
def disp_2d(st):
    # each element is a list of tuples of the form [(x1,x2),(y1,y2)]
    map = {}
    for t, slice in enumerate(st.data):
        bias = 0
        cnt = 0
        if t == 0:
            for x, direction in enumerate(slice):
                map[(x, t)] = (x, t)
        else:
            for x, direction in enumerate(slice):
                if slice[x] == 0:
                    cnt += 1
                    bias += map[st.connected_to(x, t)][0] - x
                    # print(st.connected_to(x, t)[0] - x)

            bias = bias / cnt
            print((bias, t))
            for x, direction in enumerate(slice):
                map[(x, t)] = (x + bias, t)

    lines = []
    Xup = []
    Tup = []
    Xdown = []
    Tdown = []
    colors = []
    sc = []
    markers = []
    for t, slice in enumerate(st.data):
        for x, direction in enumerate(slice):
            xdisp, tdisp = map[(x, t)]
            if st.data[t][x] == 1:
                Xup.append(xdisp)
                Tup.append(tdisp)
            if st.data[t][x] == 0:
                Xdown.append(xdisp)
                Tdown.append(tdisp)
            xright, tright = map[((x + 1) % st.spatial_slice_sizes[t], t)]
            if (x + 1) % st.spatial_slice_sizes[t] == 0 and x == st.spatial_slice_sizes[
                t
            ] - 1:
                xright = map[(x, t)][0] + 1
            lines.append([map[(x, t)], (xright, t)])
            # print(x, t, map[(x, t)], st.data[t][x])
            if direction == 1:

                x2, t2 = st.connected_to(x, t, disp=False)
                x2, t2 = map[(x2, t2)]
                if t2 == 0 and t == st.time_size - 1:
                    t2 = st.time_size
                    x2 = map[(x, t)][0]
                lines.append([map[(x, t)], (x2, t2)])

    lc = mc.LineCollection(
        lines, linewidths=1, color="black", alpha=0.5, linestyle="solid"
    )
    fig, ax = pl.subplots()
    ax.add_collection(lc)
    # ax.set_aspect(1)
    ax.autoscale()
    ax.margins(0.1)
    plt.scatter(Xup, Tup, s=10, color="red", alpha=0.5, marker="v")
    plt.scatter(Xdown, Tdown, s=10, color="blue", alpha=0.5, marker="^")
    plt.show()


def disp_2d2(st):
    # each element is a list of tuples of the form [(x1,x2),(y1,y2)]
    map = {}
    for t, slice in enumerate(st.data):
        for x, direction in enumerate(slice):
            map[(x, t)] = (x / st.spatial_slice_sizes[t] * st.time_size, t)

    lines = []
    Xup = []
    Tup = []
    Xdown = []
    Tdown = []
    Cup = []
    Cdown = []
    colors = []
    sc = []
    markers = []
    for t, slice in enumerate(st.data):
        for x, direction in enumerate(slice):
            direction = direction[0]
            xdisp, tdisp = map[(x, t)]
            if st.data[t][x][0] == 1:
                Xup.append(xdisp)
                Tup.append(tdisp)
                Cup.append(st.data[t][x][1])
            if st.data[t][x][0] == 0:
                Xdown.append(xdisp)
                Tdown.append(tdisp)
                Cdown.append(st.data[t][x][1])
            xright, tright = map[((x + 1) % st.spatial_slice_sizes[t], t)]
            if (x + 1) % st.spatial_slice_sizes[t] == 0 and x == st.spatial_slice_sizes[
                t
            ] - 1:
                xright = map[(x, t)][0] + 1
            lines.append([map[(x, t)], (xright, t)])
            # print(x, t, map[(x, t)], st.data[t][x])
            if direction == 1:

                x2, t2 = st.connected_to(x, t, disp=False)
                x2, t2 = map[(x2, t2)]
                if t2 == 0 and t == st.time_size - 1:
                    t2 = st.time_size
                lines.append([map[(x, t)], (x2, t2)])

    # lc = mc.LineCollection(
    #     lines, linewidths=1, color="black", alpha=0.5, linestyle="solid"
    # )
    # fig, ax = pl.subplots()
    # ax.add_collection(lc)
    # ax.set_aspect(1)
    # ax.autoscale()
    # ax.margins(0.1)
    plt.scatter(Xup, Tup, s=60, c=Cup, alpha=1, cmap="Blues", marker="o")
    plt.scatter(Xdown, Tdown, s=60, c=Cdown, cmap="Reds", alpha=1, marker="o")
    plt.show()


# this disp displays all time-like lines as vertical
def disp_2d_vert(st):
    # each element is a list of tuples of the form [(x1,x2),(y1,y2)]
    map = {}
    for t, slice in enumerate(st.data):
        for J in [0, 1]:
            for x, direction in enumerate(slice):

                if t != 0:

                    x2, t2 = st.connected_to(x, t)
                    if st.data[t][x][0] == 0 and J == 0:
                        x2, tpoop = map[(x2, t2)]
                        map[(x, t)] = (x2, t)
                    # if st.data[t][x] == 0 and J == 2:
                    #     print(x2, t)
                    #     map[(x, t)] = map[(x2, t)]
                    #     # map[(x2, t2)] = (x2, t2)
                    if st.data[t][x][0] == 1 and J == 1:
                        xr = x
                        xl = x
                        while slice[xr] == 1:
                            xr = (xr + 1) % st.spatial_slice_sizes[t]
                        while slice[xl] == 1:
                            xl = (xl - 1) % st.spatial_slice_sizes[t]
                        xlp, t = map[(xl, t)]
                        xrp, t = map[(xr, t)]
                        map[(x, t)] = (xlp + (x - xl) / (xr - xl) * (xrp - xlp), t)
                        # map[(x, t)] = (x, t)

                else:
                    map[(x, t)] = (x, t)
                # print(map)

    lines = []
    Xup = []
    Tup = []
    Xdown = []
    Tdown = []
    colors = []
    sc = []
    markers = []
    for t, slice in enumerate(st.data):
        for x, direction in enumerate(slice):
            direction = direction[0]
            xdisp, tdisp = map[(x, t)]
            if st.data[t][x] == 1:
                Xup.append(xdisp)
                Tup.append(tdisp)
            if st.data[t][x] == 0:
                Xdown.append(xdisp)
                Tdown.append(tdisp)
            xright, tright = map[((x + 1) % st.spatial_slice_sizes[t], t)]
            if xright == 0 and x == st.spatial_slice_sizes[t] - 1:
                xright = st.spatial_slice_sizes[t]
            lines.append([map[(x, t)], (xright, t)])
            # print(x, t, map[(x, t)], st.data[t][x])
            if direction == 1:

                x2, t2 = st.connected_to(x, t, disp=False)
                x2, t2 = map[(x2, t2)]
                if t2 == 0 and t == st.time_size - 1:
                    t2 = st.time_size
                lines.append([map[(x, t)], (x2, t2)])

    lc = mc.LineCollection(
        lines, linewidths=1, color="black", alpha=0.5, linestyle="solid"
    )
    fig, ax = pl.subplots()
    ax.add_collection(lc)
    # ax.set_aspect(1)
    ax.autoscale()
    ax.margins(0.1)
    plt.scatter(Xup, Tup, s=10, color="red", alpha=0.5, marker="v")
    plt.scatter(Xdown, Tdown, s=10, color="blue", alpha=0.5, marker="^")
    plt.show()


def force_layout(st):
    map = {}
    velocities = {}
    Xup = []
    Tup = []
    Cup = []
    Xdown = []
    Tdown = []
    Cdown = []
    colors = []
    for t, slice in enumerate(st.data):
        for x, direction in enumerate(slice):
            colors.append(direction[1])
            map[(x, t)] = (x - len(slice) * 0.5, t)
            velocities[(x, t)] = 0

    # one step
    for i in range(50):
        print(i)
        new_map = {}
        for t, slice in enumerate(st.data):
            for x, direction in enumerate(slice):

                xi = map[(x, t)][0]
                xr = map[((x + 1) % len(slice), t)][0]
                xl = map[((x - 1) % len(slice), t)][0]
                xt = map[st.connected_to(x, t)][0]
                xt_clamped = max(min(xt, xr), xl)

                new_map[(x, t)] = (
                    xi
                    + 0.25 * (xt_clamped - xi)
                    + 0.25 * ((xl + xr) * 0.5 - xi) / max((xt_clamped - xi), 1),
                    t,
                )
                if x == len(slice) - 1:
                    new_map[(x, t)] = (xi + (xt - xi) * 0.25, t)
                if x == 0:
                    new_map[(x, t)] = (xi + (xt - xi) * 0.25, t)
                # new_map[(x, t)] = (x, t)
        map = new_map

    lines = []
    for t, slice in enumerate(st.data):
        for x, direction in enumerate(slice):
            if direction[0] == 1:
                x2, t2 = st.connected_to(x, t)
                x2, t2 = new_map[(x2, t2)]
                if t2 == 0 and t == st.time_size - 1:
                    t2 = st.time_size
                lines.append([new_map[(x, t)], [x2, t2]])
            xi, ti = new_map[(x, t)]
            xright, tright = new_map[((x + 1) % st.spatial_slice_sizes[t], t)]
            if xright == 0 and x == st.spatial_slice_sizes[t] - 1:
                xright = st.spatial_slice_sizes[t]
            # lines.append([new_map[(x, t)], (xright, t)])
            if direction[0] == 1:
                Xup.append(xi)
                Tup.append(ti)
                Cup.append(direction[1])
            if direction[0] == 0:
                Xdown.append(xi)
                Tdown.append(ti)
                Cdown.append(direction[1])
    lc = mc.LineCollection(
        lines, linewidths=1, alpha=0.5, linestyle="solid", color="black"
    )
    import numpy as np

    # lc.set_array(np.array(colors))
    fig, ax = pl.subplots()
    ax.add_collection(lc)
    ax.set_aspect(1)
    ax.autoscale_view()
    plt.scatter(Xup, Tup, alpha=0.5, c=Cup, marker="v", cmap="Reds")
    plt.scatter(Xdown, Tdown, alpha=0.5, c=Cdown, marker="^", cmap="Blues")
    plt.show()
