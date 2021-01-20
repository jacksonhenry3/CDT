"""
Trying to use node and face NOT vertex and simplex
"""

import Display


class SpaceTime(object):
    """docstring for SpaceTime."""

    # __slots__ = []

    def __init__(self):
        super(SpaceTime, self).__init__()

        # consider adding curvature here aswell
        self.nodes = []  # nodes is just a list of indicies
        self.node_left = {}  # a dict with node indices as keys
        self.node_right = {}  # a dict with node indices as keys
        self.node_past = {}  # a dict with node indices as keys
        self.node_future = {}  # a dict with node indices as keys
        self.faces_containing = {}

        self.faces = []  # faces is a frozenset of node indeces
        self.face_dilaton = {}  # a dict with keys of face tuples and field vals
        self.face_x = {}  # a dict with keys of face tuples space-like connected
        self.face_t = {}  # a dict with keys of face tuples time-like connected

        # This could be modified to include a list of dead refrences
        self.dead_refrences = []

        self.max_node = 0

    def node_x(self, node):
        return [self.node_left[node], self.node_right[node]]

    def node_t(self, node):
        return self.node_past[node] + self.node_future[node]

    def node_all_connections(self, node):
        return self.node_x(node) + self.node_t(node)

    def generate_flat(self, space_size, time_size):
        """
        There is a lot of 'frontloaded thought' here. Very possible a source of errors. I Have done some initial validation by inspecting the adjacency matrices. I'm fairly confident that the node structure is correct. The simplex structure sems reasonable but i have less control over the ordering so it isn't as clear. A 3d plot would be a good idea to make sure the simplices are all defined correctly with correct neighbors. Wouldnt hurt to ha e that for the vertices either.
        """
        index = 0  # this index counts vertices
        for t in range(time_size):
            start = index  # the first index in the current time slice
            for x in range(space_size):
                self.nodes.append(index)

                left = start + (index - 1) % space_size
                right = start + (index + 1) % space_size

                self.node_left[index] = left
                self.node_right[index] = right

                # get the first node of the spatial slice above and below this one
                future_start = (start + space_size) % (space_size * time_size)
                past_start = (start - space_size) % (space_size * time_size)

                future_right = future_start + (index + 1) % space_size
                future = future_start + (index) % space_size

                past_left = past_start + (index - 1) % space_size
                past = past_start + (index) % space_size

                # these are the time connections of a node
                self.node_past[index] = [past_left, past]

                self.node_future[index] = [future, future_right]

                # There are twice as many simplices as nodes, so there are 2 faces defined per iteration
                # These are the faces (a different two can be chosen, the only important thing is that they are uniquly defined by the vertex (t,x))
                f1 = frozenset({index, right, future_right})
                f2 = frozenset({index, left, past_left})

                self.faces.append(f1)
                self.faces.append(f2)

                # This is where we chose the initial dilaton values for each simplex
                self.face_dilaton[f1] = 1
                self.face_dilaton[f2] = 1

                # This defines the two spatialy adjacent simplices to f1
                f1_l = frozenset({index, future_right, future})
                f1_r = frozenset(
                    {right, future_right, future_start + (index + 2) % space_size}
                )
                self.face_x[f1] = [f1_l, f1_r]

                # This defines the two spatialy adjacent simplices to f2
                f2_l = frozenset({index, past, past_left})
                f2_r = frozenset(
                    {left, past_left, past_start + (index - 2) % space_size}
                )
                self.face_x[f2] = [f2_l, f2_r]

                # These are the faces in the future of f1 and f2
                f1_t = frozenset({index, right, past})
                self.face_t[f1] = f1_t
                f2_t = frozenset({index, left, future})
                self.face_t[f2] = f2_t

                self.faces_containing[index] = {f1, f2, f1_l, f2_l, f1_t, f2_t}
                index += 1
        self.max_node = index

    # Made redundant by faces_containing dict, remove once fully validated
    def get_faces_containing(self, n):
        # get all simplices that contain a particular vertex
        return {face for face in self.faces if n in face}

    def pop(self, node):
        """
        This creates a new space-time by removing all nodes adjacent to node and returning that sub_space
        """
        sub_space = SpaceTime()

        dead_nodes = self.node_all_connections(node)

        self.dead_refrences = dead_nodes
        sub_space.dead_refrences = dead_nodes

        nodes = dead_nodes + [node]
        faces = self.faces_containing[node]

        for n in nodes:
            self.nodes.remove(n)
        sub_space.nodes = nodes

        for n in sub_space.nodes:
            sub_space.node_left[n] = self.node_left.pop(n)
            sub_space.node_right[n] = self.node_right.pop(n)
            sub_space.node_past[n] = self.node_past.pop(n)
            sub_space.node_future[n] = self.node_future.pop(n)
            sub_space.faces_containing[n] = self.faces_containing.pop(n)

        for f in faces:
            self.faces.remove(f)
        sub_space.faces = faces

        for f in sub_space.faces:
            sub_space.face_dilaton[f] = self.face_dilaton.pop(f)
            sub_space.face_x[f] = self.face_x.pop(f)
            sub_space.face_t[f] = self.face_t.pop(f)

        return sub_space

    def push(self, sub_space):
        """
        This reinserts sub_space
        """
        # add a check to make sure that we are inserting unique new nodes
        nodes = sub_space.nodes
        faces = sub_space.faces

        for n in nodes:
            self.nodes.append(n)

        for n in nodes:
            self.node_left[n] = sub_space.node_left.pop(n)
            self.node_right[n] = sub_space.node_right.pop(n)
            self.node_past[n] = sub_space.node_past.pop(n)
            self.node_future[n] = sub_space.node_future.pop(n)
            self.faces_containing[n] = sub_space.faces_containing.pop(n)

        for f in faces:
            self.faces.append(f)

        for f in sub_space.faces:
            self.face_dilaton[f] = sub_space.face_dilaton.pop(f)
            self.face_x[f] = sub_space.face_x.pop(f)
            self.face_t[f] = sub_space.face_t.pop(f)

        # This should probably be validated
        self.contains_dead_refrences = False
        # Can we get rid of sub_space at this point somehow?

    def move(self, node, future, past):
        """
        A move should add one node and 2 simplices. we can pop all the structures to be modified out of the dicts and then push them back in once they've been modified. This mean we need to know what could get modfified in any given move.
        """

        sub_space = self.pop(node)

        # self.max_node += 1
        # new_node = self.max_node
        #
        # sub_space.nodes.append(new_node)
        #
        # # Im labeling these as left and right but actual orientation is unknown. Could this possible cause a bias? Need to pick one OR make sure it's properly random.
        # left = sub_space.node_x(node).pop()
        # right = sub_space.node_x(node).pop()
        #
        # # This fixes all the spatial relations of the new node
        # sub_space.node_x(node).append(new_node)
        # sub_space.node_x(node).append(right)
        # sub_space.node_x(left).remove(node)
        # sub_space.node_x(left).append(new_node)
        # sub_space.node_x(new_node).append(node)
        # sub_space.node_x(new_node).append(left)

        # to fix the time connections i need an ordering of the past and future nodes. One option is to find an edge (I.E. one whos spatial connections aren't both in the sub_space) and treat graph distance from that node as a rank. This should give a spatial ordering.

        # another (perhaps smarter) way is to start from the split point and move in one direction or the other untill leaving the set.

        # This is another opourtunity for orintation biases.

        self.push(sub_space)


FST = SpaceTime()
FST.generate_flat(12, 12)
# FST.move(30, 0, 0)

# Display.show_node_adjacency_matrix(FST)
