import random

random.seed(1)


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
                [[(i + j) % 2, 0] for i in range(space_size)] for j in range(time_size)
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

    def connected_to(self, x, t, disp=False):
        slice = self.data[t]
        direction = slice[x][0]

        idx = 0
        for prev_dir in slice[:x]:
            if prev_dir[0] == direction:
                idx += 1

        # connect it to the the !"direction" pointing triangle
        t2 = int((t + (direction - 0.5) * 2)) % self.time_size

        count = 0
        # x3 = 0

        for i, prev_dir in enumerate(self.data[t2]):
            if prev_dir[0] != direction:

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
        value = slice[x][0]
        xp = (x + 1) % self.spatial_slice_sizes[t]

        future = [xp]
        while slice[xp][0] != value:

            xp = (xp + 1) % self.spatial_slice_sizes[t]
            future.append(xp)
        return future

    def get_past(self, node):
        # MUST BE VERY CAREGUL ABOUT OFF BY ONE
        x, t = node
        x2, t2 = self.connected_to(x, t)
        slice2 = self.data[t2]
        value2 = slice2[x2][0]
        xp2 = (x2 + 1) % self.spatial_slice_sizes[t2]

        past = [xp2]
        while slice2[xp2][0] != value2:
            xp2 = (xp2 + 1) % self.spatial_slice_sizes[t2]
            past.append(xp2)
        return past

    def move(self, x, t):
        value = self.data[t][x][0]
        t2 = int((t + (value - 0.5) * 2)) % self.time_size

        future = self.get_future((x, t))
        past = self.get_past((x, t))
        newt1 = random.choices(future)[0]

        newt2 = random.choices(past)[0]

        self.data[t].insert(newt1, [value, 0])
        self.data[t2].insert(newt2, [(value + 1) % 2, 0])

        self.spatial_slice_sizes[t] += 1
        self.spatial_slice_sizes[t2] += 1
        # print()
        self.length += 2
        self.totalChanges += 1

    def inverse_move(self, x, t):
        row = self.data[t]
        dir = row[x]
        if dir in row[:x] + row[x + 1 :]:
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
            print(
                "Inverse move failed becouse (x,t)-(x2,t2) bounds both sides of a face"
            )

    def save(self, name="test"):
        with open(name + ".txt", "w") as filehandle:
            for listitem in self.data:
                filehandle.write("%s\n" % listitem)
