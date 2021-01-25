"""
Trying to use node and face NOT vertex and simplex
"""

import Display
import random
from NodeObject import NodeObject


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

        # consider inserting using something like this rather than max
        # https://stackoverflow.com/questions/28176866/find-the-smallest-positive-number-not-in-list
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
                self.face_dilaton[f2] = -1

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

                self.faces_containing[index] = [f1, f2, f1_l, f2_l, f1_t, f2_t]
                index += 1
        self.max_node = index

    def get_random_node(self):
        return random.choice(self.nodes)

    # Made redundant by faces_containing dict, remove once fully validated
    def get_faces_containing(self, n):
        # get all simplices that contain a particular vertex
        return {face for face in self.faces if n in face}

    def pop(self, node_list):
        """
        This creates a new space-time by removing all nodes adjacent to node and returning that sub_space
        """
        sub_space = SpaceTime()

        nodes = node_list.copy()
        faces = []
        for node in node_list:
            nodes.extend(self.node_all_connections(node))
            # update this to use the dict instead (requires some work)
            faces.extend(self.get_faces_containing(node))
        faces = list(set(faces))
        nodes = list(set(nodes))
        # remove all nodes from self
        for n in nodes:
            self.nodes.remove(n)
        self.dead_refrences = nodes.copy()  # i.e these nodes are no longer in the st

        # remove all faces that contain anything in node_list
        for f in faces:
            self.faces.remove(f)

        # set the sub_space nodes and faces
        sub_space.nodes = nodes.copy()
        sub_space.faces = faces.copy()

        # loop through all removed nodes and remove their properties from self and add them to sub_space
        for n in sub_space.nodes:
            sub_space.node_left[n] = self.node_left.pop(n)
            sub_space.node_right[n] = self.node_right.pop(n)
            sub_space.node_past[n] = self.node_past.pop(n)
            sub_space.node_future[n] = self.node_future.pop(n)
            sub_space.faces_containing[n] = self.faces_containing.pop(n)

        # loop through all removed faces and remove their properties from self and add them to sub_space
        for f in sub_space.faces:
            sub_space.face_dilaton[f] = self.face_dilaton.pop(f)
            # sub_space.face_x[f] = self.face_x.pop(f)
            # sub_space.face_t[f] = self.face_t.pop(f)

        # dont forget to set sub_space dead refrences
        return sub_space

    def push(self, sub_space):
        """
        This reinserts sub_space
        """

        # Check to make sure that sub_space fills self aproapriatly
        if any(n not in sub_space.nodes for n in self.dead_refrences):
            pass
            # print("sub_space cannot fill space_time gap")
            # print("dead refrences are {}".format(self.dead_refrences))
            # print("sub_space nodes are {}".format(sub_space.nodes))
            # raise ValueError()

        # add a check to make sure that we are inserting unique new nodes
        nodes = sub_space.nodes
        faces = sub_space.faces

        for n in nodes:
            self.nodes.append(n)

        for n in nodes:
            self.node_left[n] = sub_space.node_left[n]
            self.node_right[n] = sub_space.node_right[n]
            self.node_past[n] = sub_space.node_past[n]
            self.node_future[n] = sub_space.node_future[n]
            self.faces_containing[n] = sub_space.faces_containing[n]

        for f in faces:
            self.faces.append(f)

        for f in sub_space.faces:
            self.face_dilaton[f] = sub_space.face_dilaton[f]
            # self.face_x[f] = sub_space.face_x[f]
            # self.face_t[f] = sub_space.face_t[f]

        # This should probably be validated
        self.dead_nodes = []
        # Can we get rid of sub_space at this point somehow?

    def move(self, node, future, past):
        """
        A move should add one node and 2 simplices. we can pop all the structures to be modified out of the dicts and then push them back in once they've been modified. This mean we need to know what could get modfified in any given move.
        """

        # remove the sub_space that is going to be modified
        sub_space = self.pop([node])

        # increment the total node counter
        self.max_node += 1
        new_node = self.max_node

        # create a node object for easy manipulation. This also automatically adds the node to the sub_space
        new_node_obj = NodeObject(sub_space, new_node)
        node_obj = NodeObject(sub_space, node)
        left_obj = NodeObject(sub_space, node_obj.left)
        left = node_obj.left
        right = node_obj.right

        # spatial changes.
        node_obj.set_left(new_node)
        new_node_obj.set_right(node)
        new_node_obj.set_left(left)
        left_obj.set_right(new_node)

        # future changes
        new_future_set = [future]
        f = sub_space.node_left[future]

        while f in node_obj.future:
            new_future_set.append(f)
            sub_space.node_future[node].remove(f)
            sub_space.node_past[f].remove(node)
            f = sub_space.node_left[f]
        new_node_obj.set_future(new_future_set)
        old_future_set = list(
            set(sub_space.node_future[node]) - set(new_future_set)
        ) + [future]
        node_obj.set_future(old_future_set)
        sub_space.node_past[future].append(new_node)

        # past changes
        new_past_set = [past]
        p = sub_space.node_left[past]
        while p in node_obj.past:
            new_past_set.append(p)
            sub_space.node_past[node].remove(p)
            sub_space.node_future[p].remove(node)
            p = sub_space.node_left[p]

        new_node_obj.set_past(new_past_set)
        old_past_set = list(set(sub_space.node_past[node]) - set(new_past_set)) + [past]
        node_obj.set_past(old_past_set)
        sub_space.node_future[past].append(new_node)

        # face changes
        # remove old faces
        sub_space.faces = []

        n = future
        leftmost_future = n
        while sub_space.node_left[n] in new_node_obj.future:
            v1 = n
            n = sub_space.node_left[n]
            leftmost_future = n
            new_face = frozenset([v1, n, new_node])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = -1
        n = past
        leftmost_past = n
        while sub_space.node_left[n] in new_node_obj.past:
            v1 = n
            n = sub_space.node_left[n]
            leftmost_past = n
            new_face = frozenset([v1, n, new_node])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = 100

        n = future
        rightmost_future = n
        while sub_space.node_right[n] in node_obj.future:
            v1 = n
            n = sub_space.node_right[n]
            rightmost_future = n
            new_face = frozenset([v1, n, node])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = -1
        n = past
        rightmost_past = n
        while sub_space.node_right[n] in node_obj.past:
            v1 = n
            n = sub_space.node_right[n]
            rightmost_past = n
            new_face = frozenset([v1, n, node])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = 100

        righmost_future = future

        sub_space.faces.append(frozenset({node, new_node, future}))
        sub_space.face_dilaton[frozenset({node, new_node, future})] = 1
        sub_space.faces.append(frozenset({node, new_node, past}))
        sub_space.face_dilaton[frozenset({node, new_node, past})] = -1

        sub_space.faces.append(frozenset({node, right, rightmost_future}))
        sub_space.face_dilaton[frozenset({node, right, rightmost_future})] = 1
        sub_space.faces.append(frozenset({node, right, rightmost_past}))
        sub_space.face_dilaton[frozenset({node, right, rightmost_past})] = -1

        sub_space.faces.append(frozenset({left, new_node, leftmost_future}))
        sub_space.face_dilaton[frozenset({left, new_node, leftmost_future})] = 1
        sub_space.faces.append(frozenset({left, new_node, leftmost_past}))
        sub_space.face_dilaton[frozenset({left, new_node, leftmost_past})] = -1

        new_node_obj.set_faces([])
        node_obj.set_faces([])
        self.push(sub_space)

    def imove(self, node):
        """ merge two spatially adjacent nodes, always merges in one direction?"""
        left = self.node_left[node]
        sub_space = self.pop([node, left])

        new_future = sub_space.node_future[left]
        new_past = sub_space.node_past[left]
        new_left = sub_space.node_left[left]

        for f in new_future:
            sub_space.node_past[f].remove(left)
            if f not in sub_space.node_future[node]:
                sub_space.node_future[node].append(f)
                sub_space.node_past[f].append(node)

        for p in new_past:
            sub_space.node_future[p].remove(left)
            if p not in sub_space.node_past[node]:
                sub_space.node_past[node].append(p)
                sub_space.node_future[p].append(node)

        sub_space.node_left[node] = new_left
        sub_space.node_right[new_left] = node

        sub_space.nodes.remove(left)
        del sub_space.node_left[left]
        del sub_space.node_right[left]
        del sub_space.node_past[left]
        del sub_space.node_future[left]
        del sub_space.faces_containing[left]

        faces = sub_space.get_faces_containing(left)

        sub_space.faces = [x for x in sub_space.faces if x not in faces]
        for face in faces:
            new_face = []
            if node not in face:
                for n in face:
                    if n == left:
                        n = node
                    new_face.append(n)
                sub_space.faces.append(frozenset(new_face))
                sub_space.face_dilaton[frozenset(new_face)] = -1

        self.push(sub_space)


# move fails when this is executed
FST = SpaceTime()
size = 25
FST.generate_flat(size, size)
random.seed(9)

for i in range(150):
    print(i)
n = FST.get_random_node()
f = random.choice(FST.node_future[n])
p = random.choice(FST.node_past[n])
FST.move(n, f, p)
FST.imove(n)
print("plottin")

Display.plot_2d(FST)
