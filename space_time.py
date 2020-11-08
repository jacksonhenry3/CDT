import random


class space_time(object):
    """
    the data array holds a list of each spatial slice. Each spatial slice contain one
    value for each triangle in that slice. The value indicates weather the triangle is
    upwards pointing (1) or downwards pointing (0)
    """

    def __init__(self, time_size, space_size, data=None):
        """
        time_size must be even. Space size can be arbitrary. If you want to initialize
        a space_time with exisiting data these two params will be overwritten
        """
        super(space_time, self).__init__()

        if data is None:
            self.data = [
                [
                    {"dir": (i + j) % 2, "phi": random.random(), "R": 0}
                    for i in range(space_size)
                ]
                for j in range(time_size)
            ]
        else:
            self.data = data

        # time size will not change
        self.time_size = len(self.data)

        # these change with moves and inverse moves
        # a possible validation test would be to recalculate and compare.
        self.spatial_slice_sizes = [len(slice) for slice in self.data]
        self.length = sum(self.spatial_slice_sizes)
        self.totalChanges = 0

        self.s = self.action()

        # for t, row in enumerate(self.data):
        #     for x, simplex in enumerate(row):
        #         direction = simplex[0]
        #         field = simplex[1]

    def curvature(self, x, t):
        num_future_connections = len(self.get_future([x, t]))
        num_past_connections = len(self.get_past([x, t]))
        f1 = 2 + num_future_connections + num_past_connections
        f1 = (f1 - 6.0) / f1
        row = self.data[t]
        dir = row[x]["dir"]
        found_left = False
        found_time = False
        dir = self.data[t][(x - 1) % self.spatial_slice_sizes[t]]["dir"]
        x2 = x - 1

        while not found_left or not found_time:
            if row[x2]["dir"] == dir and not found_left:
                found_left = True
                xl = x2
            if row[x2]["dir"] != dir and not found_time:
                found_time = True
                xt = x2
            x2 = x2 - 1
        num_future_connections = len(self.get_future([xl, t]))
        num_past_connections = len(self.get_past([xl, t]))
        f2 = 2 + num_future_connections + num_past_connections
        f2 = (f2 - 6.0) / f2

        num_future_connections = len(self.get_future([xt, t]))
        num_past_connections = len(self.get_past([xt, t]))
        f3 = 2 + num_future_connections + num_past_connections
        f3 = (f3 - 6.0) / f3

        return (f1 + f2 + f3) * 2.0 / 3.0

    def space_derivative(self, x, t, l=1):
        row = self.data[t]
        width = self.spatial_slice_sizes[t]
        return (row[(x + 1) % width]["phi"] - row[(x - 1) % width]["phi"]) / (2 * l)

    def time_derivative(self, x, t, l=1):
        simplex = self.data[t][x]
        x2, t2 = self.connected_to(x, t)

        if simplex["dir"] == 1:
            return (simplex["phi"] - self.data[t2][x2]["phi"]) / l
        elif simplex["dir"] == 0:
            return (self.data[t2][x2]["phi"] - simplex["phi"]) / l
        else:
            print("WHAT!")

    def action(self):
        area = 1
        s = 0
        for t, row in enumerate(self.data):
            for x, simplex in enumerate(row):
                phi = simplex["phi"]
                R = self.curvature(x, t)
                s_delta = 0
                s_delta += phi * R
                s_delta -= (
                    self.space_derivative(x, t) ** 2 + self.time_derivative(x, t) ** 2
                )
                s += s_delta
        return area * s

    def connected_to(self, x, t, disp=False):
        slice = self.data[t]
        direction = slice[x]["dir"]

        idx = 0
        for prev_dir in slice[:x]:
            if prev_dir["dir"] == direction:
                idx += 1

        # connect it to the the !"direction" pointing triangle
        t2 = int((t + (direction - 0.5) * 2)) % self.time_size

        count = 0
        # x3 = 0

        for i, prev_dir in enumerate(self.data[t2]):
            if prev_dir["dir"] != direction:

                if count == idx:
                    x3p = i
                    break
                count += 1

        if disp:
            return (x3p, int((t + (direction - 0.5) * 2)))
        return (x3p, t2)

    def random_vertex(self):
        random_index = random.randint(0, self.length - 1)
        total_previous_triangles = 0
        t = 0
        while total_previous_triangles <= random_index:
            t += 1
            total_previous_triangles += self.spatial_slice_sizes[t - 1]
        t -= 1
        total_previous_triangles -= self.spatial_slice_sizes[t]
        x = random_index - total_previous_triangles
        return (x, t)

    # future and past designations are arbitrary
    def get_future(self, node):
        # MUST BE VERY CAREFUL ABOUT OFF BY ONE
        x, t = node
        slice = self.data[t]
        value = slice[x]["dir"]
        xp = (x + 1) % self.spatial_slice_sizes[t]

        future = [(xp, t)]
        while slice[xp]["dir"] != value:

            xp = (xp + 1) % self.spatial_slice_sizes[t]
            future.append((xp, t))
        return future

    def get_past(self, node):
        # MUST BE VERY CAREFUL ABOUT OFF BY ONE
        x, t = node
        x2, t2 = self.connected_to(x, t)
        slice2 = self.data[t2]
        value2 = slice2[x2]["dir"]
        xp2 = (x2 + 1) % self.spatial_slice_sizes[t2]

        past = [(xp2, t2)]
        while slice2[xp2]["dir"] != value2:
            xp2 = (xp2 + 1) % self.spatial_slice_sizes[t2]
            past.append((xp2, t2))
        return past

    def get_all(self, node):
        nodes = self.get_future(node)
        nodes += self.get_past(node)
        nodes.append(node)
        nodes.append(self.connected_to(*node))
        return nodes

    def get_possible_modified_move(self, node0, node1, dir1, node2, dir2):
        """node0 is the move location, node1 and node2 are the location of triangle insertion"""
        nodes = self.get_all(node0)

        t = node1[1]
        x = node1[0]
        slice = self.data[t]
        width = self.spatial_slice_sizes[t]

        xp = (x - 1) % width
        new_direction = slice[xp]["dir"]
        while new_direction is dir1:
            xp = (xp - 1) % width
            new_direction = slice[xp]["dir"]
        nodes += self.get_all((xp, t))

        t = node2[1]
        x = node2[0]
        slice = self.data[t]
        width = self.spatial_slice_sizes[t]

        xp = (x - 1) % width
        new_direction = slice[xp]["dir"]
        while new_direction is dir2:
            xp = (xp - 1) % width
            new_direction = slice[xp]["dir"]
        nodes += self.get_all((xp, t))

        return nodes

    def get_possible_modified_imove(self, node0):
        """node0 is the move location, node1 and node2 are the location of triangle insertion"""
        nodes = self.get_all(node0)
        x = node0[0]
        t = node0[1]
        width = self.spatial_slice_sizes[t]
        xp = (x - 1) % width
        slice = self.data[t]
        new_direction = slice[xp]["dir"]
        dir1 = self.data[t][x]["dir"]
        while new_direction is not dir1:
            xp = (xp - 1) % width
            new_direction = slice[xp]["dir"]
        nodes += self.get_all((xp, t))

        xp = (x - 1) % width
        new_direction = slice[xp]["dir"]
        while new_direction is dir1:
            xp = (xp - 1) % width
            new_direction = slice[xp]["dir"]
        nodes += self.get_all((xp, t))

        xp, tp = self.connected_to(x, t)
        slice = self.data[tp]
        width = self.spatial_slice_sizes[tp]
        xpp = (xp - 1) % width
        new_direction = slice[xpp]["dir"]
        while new_direction is not dir1:
            xpp = (xpp - 1) % width
            new_direction = slice[xpp]["dir"]
        nodes += self.get_all((xpp, tp))

        return nodes

    def move(self, x, t):
        simplex = self.data[t][x]
        dir = simplex["dir"]
        t2 = int((t + (dir - 0.5) * 2)) % self.time_size

        future = self.get_future((x, t))
        past = self.get_past((x, t))
        newt1 = random.choices(future)[0]
        newt2 = random.choices(past)[0]

        pschng = self.get_possible_modified_move(
            (x, t), newt1, dir, newt2, (dir + 1) % 2
        )
        for n in pschng:
            self.data[n[1]][n[0]]["R"] += 1
        newt1 = newt1[0]

        newt2 = newt2[0]

        self.data[t].insert(newt1, {"dir": dir, "phi": random.random(), "R": 10})
        self.data[t2].insert(
            newt2, {"dir": (dir + 1) % 2, "phi": random.random(), "R": 10}
        )

        self.spatial_slice_sizes[t] += 1
        self.spatial_slice_sizes[t2] += 1

        self.length += 2
        self.totalChanges += 1

    def inverse_move(self, x, t):
        row = self.data[t]
        dir = row[x]["dir"]

        pschng = self.get_possible_modified_imove((x, t))
        for n in pschng:
            self.data[n[1]][n[0]]["R"] -= 1

        if dir in [item["dir"] for item in row[:x] + row[x + 1 :]]:
            x2, t2 = self.connected_to(x, t)

            # self.data[t] = np.delete(self.data[t], x)
            self.data[t].pop(x)
            # self.data[t2] = np.delete(self.data[t2], x2)
            self.data[t2].pop(x2)

            self.spatial_slice_sizes[t] -= 1
            self.spatial_slice_sizes[t2] -= 1
            self.length -= 2
            self.totalChanges += 1
        else:
            print(row)
            print(
                "Inverse move failed becouse (x,t)-(x2,t2) bounds both sides of a face"
            )

    def save(self, name="test"):
        with open("logs/" + name + ".txt", "w") as filehandle:
            for listitem in self.data:
                filehandle.write("%s\n" % listitem)
