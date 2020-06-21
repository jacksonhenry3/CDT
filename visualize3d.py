from math import pi as pi
from numpy import mean, sin, cos, arctan2, abs, round
from mayavi.mlab import triangular_mesh
import random
import time


def disp3d(st):
    sss = st.space_slice_sizes()

    def torus_angle(n, t, x, i):
        u = float(t) / len(sss) * 2 * pi
        v = float(x) / sss[t] * 2 * pi
        return {"u": u, "v": v, "t": t}

    def modify(n, t, x, i):
        past_v = [torus_angles[p]["v"] for p in n.past]
        past_v = past_v + [torus_angles[f]["v"] for f in n.future]
        past_v.append(torus_angles[n.right]["v"])
        past_v.append(torus_angles[n.left]["v"])
        lv = torus_angles[n.left]["v"]
        rv = torus_angles[n.right]["v"]

        avg_past_v = angle_avg(past_v)
        V = torus_angles[n.index]["v"]

        return {
            "u": torus_angles[n.index]["u"],
            "v": angle_avg([avg_past_v, V, V, V, V]),
            "t": torus_angles[n.index]["t"],
        }

    def check(n, t, x, i):
        lv = torus_angles[n.left]["v"]
        rv = torus_angles[n.right]["v"]
        v = torus_angles[n.index]["v"]
        a = lv - v
        a = (a + pi) % (2 * pi) - pi
        b = rv - v
        b = (b + pi) % (2 * pi) - pi
        # print(a)
        if a >= 0:
            torus_angles[n.index]["v"] = lv + 0.01
            return False
        return True

    torus_angles = st.loop(torus_angle)
    INDEX = list(torus_angles.keys())[2]
    # print(round(torus_angles[INDEX]["v"], 2))
    for l in range(20):
        print(l)
        torus_angles = st.loop(modify)
        # print(round(torus_angles[INDEX]["v"], 2))
        res = st.loop(check)
        print(len(torus_angles))
        print(len([1 for value in res.values() if not value]))
        # print(round(torus_angles[INDEX]["v"], 2))

    x = []
    y = []
    z = []
    scalars = []
    triangles = []
    node_indices = {}
    i = 0
    for n in st.nodes:
        node_indices[n] = i
        i += 1

        u = torus_angles[n]["u"]
        v = torus_angles[n]["v"]
        t = torus_angles[n]["t"]

        outer_radius = 8
        inner_radius = 4 * sss[t] / max(sss)

        # for torus
        x.append((outer_radius + inner_radius * cos(v)) * cos(u))
        y.append((outer_radius + inner_radius * cos(v)) * sin(u))
        z.append(inner_radius * sin(v))

        # for cylinder
        # x.append(inner_radius * cos(v))
        # y.append(inner_radius * sin(v))
        # z.append(3 * u)

        # set scalar (color) based on curavture at each node
        r = st.get_node(n).R()
        scalars.append(r)

    for n in st.nodes:
        n = st.get_node(n)
        r = st.nodes[n.right]
        future_comon = [value for value in n.future if value in r.future]
        past_common = [value for value in n.past if value in r.past]
        # if abs(torus_angles[n.index]["t"] - torus_angles[future_comon[0]]["t"]) == 1:
        if True:
            for common in future_comon:
                triangles.append(
                    (node_indices[n.index], node_indices[common], node_indices[n.right])
                )
        # if abs(torus_angles[n.index]["t"] - torus_angles[past_common[0]]["t"]) == 1:
        if True:
            for common in past_common:
                triangles.append(
                    (node_indices[n.index], node_indices[common], node_indices[n.right])
                )

    triangular_mesh(
        x,
        y,
        z,
        triangles,
        representation="fancymesh",
        scalars=scalars,
        tube_radius=0.03,
        color=(0.0, 0.0, 0.0),
    )
    triangular_mesh(
        x,
        y,
        z,
        triangles,
        scalars=scalars,
        representation="surface",
        # color=(0.0, 0.0, 0.0),
    )


def angle_avg(a_list):
    y = mean([sin(a) for a in a_list])
    x = mean([cos(a) for a in a_list])
    return arctan2(y, x)


import space_time
from cdt import run

random.seed(0)
st = space_time.space_time()
st.generate_flat(200, 200)
run(st, 10 ** 5, 0.6, debug=True)
disp3d(st)
from mayavi import mlab

mlab.show()
