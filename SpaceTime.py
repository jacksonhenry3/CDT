"""
Trying to use node and face NOT vertex and simplex
"""

import Display
import random


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
        self.contains_dead_refrences = False
        # Can we get rid of sub_space at this point somehow?

    def move(self, node, future, past):
        """
        A move should add one node and 2 simplices. we can pop all the structures to be modified out of the dicts and then push them back in once they've been modified. This mean we need to know what could get modfified in any given move.
        """
        sub_space = self.pop(node)

        self.max_node += 1
        new_node = self.max_node

        new_node_obj = node_object(sub_space, new_node)
        node_obj = node_object(sub_space, node)
        left_obj = node_object(sub_space, node_obj.left)
        left = node_obj.left
        right = node_obj.right
        # spatial changes.
        node_obj.set_left(new_node)
        new_node_obj.set_right(node)
        new_node_obj.set_left(node_obj.left)
        left_obj.set_right(new_node)

        # future changes
        new_future_set = [future]
        f = sub_space.node_left[future]

        while f in node_obj.future:
            # print(f)
            new_future_set.append(f)
            sub_space.node_future[node].remove(f)
            f = sub_space.node_left[f]
        new_node_obj.set_future(new_future_set)

        # past changes
        new_past_set = [past]
        p = sub_space.node_left[past]
        while p in node_obj.past:
            new_past_set.append(p)
            sub_space.node_past[node].remove(p)
            p = sub_space.node_left[p]
        new_node_obj.set_past(new_past_set)

        # face changes
        # remove old faces

        old_faces = sub_space.faces.copy()
        # new_faces = old_faces
        # new_future_set.remove(future)
        # new_past_set.remove(past)
        for face in old_faces:
            if node in face and past in face:
                sub_space.faces.remove(face)
            elif node in face and future in face:
                sub_space.faces.remove(face)
            elif node in face and left in face:
                sub_space.faces.remove(face)
            elif node in face and right in face:
                sub_space.faces.remove(face)

            # elif node in face and left in face:  # should always be true?
            #     if any(n in face for n in new_future_set):
            #
            #         print("BIP")
            #         sub_space.faces.remove(face)
            #         new_face = frozenset([n if n != node else new_node for n in face])
            #         sub_space.faces.append(new_face)
            #         sub_space.face_dilaton[new_face] = 100
            #     if any(n in face for n in new_past_set):
            #         print("BOP")
            #         sub_space.faces.remove(face)
            #         new_face = frozenset([n if n != node else new_node for n in face])
            #         sub_space.faces.append(new_face)
            #         sub_space.face_dilaton[new_face] = -1
        #
        sub_space.faces.append(frozenset({node, new_node, future}))
        sub_space.face_dilaton[frozenset({node, new_node, future})] = 1
        sub_space.faces.append(frozenset({node, new_node, past}))
        sub_space.face_dilaton[frozenset({node, new_node, past})] = -1
        new_node_obj.set_faces([])
        self.push(sub_space)


class node_object(object):
    """This is just syntactic sugar to acces node relationships"""

    def __init__(self, st, node_id):
        super(node_object, self).__init__()
        self.st = st
        self.id = node_id

        if node_id in st.nodes:
            self.left = st.node_left[self.id]
            self.right = st.node_right[self.id]
            self.past = st.node_past[self.id]
            self.future = st.node_future[self.id]
            self.faces = st.faces_containing[self.id]
        else:
            st.nodes.append(self.id)

    def set_left(self, val):
        self.left = val
        self.st.node_left[self.id] = val

    def set_right(self, val):
        self.right = val
        self.st.node_right[self.id] = val

    def set_past(self, val):
        self.past = val
        self.st.node_past[self.id] = val

    def set_future(self, val):
        self.future = val
        self.st.node_future[self.id] = val

    def set_faces(self, val):
        self.faces = val
        self.st.faces_containing[self.id] = val


shading = {
    "flat": True,  # Flat or smooth shading of triangles
    "wireframe": True,
    "wire_width": 1,
    "wire_color": "red",  # Wireframe rendering
    "width": 600,
    "height": 600,  # Size of the viewer canvas
    "antialias": True,  # Antialising, might not work on all GPUs
    "scale": 2.0,  # Scaling of the model
    "side": "DoubleSide",  # FrontSide, BackSide or DoubleSide rendering of the triangles
    "colormap": "viridis",
    "normalize": [None, None],  # Colormap and normalization for colors
    "background": "#ffffff",  # Background color of the canvas
    "line_width": 1.0,
    "line_color": "black",  # Line properties of overlay lines
    "bbox": False,  # Enable plotting of bounding box
    "point_color": "red",
    "point_size": 0.01,  # Point properties of overlay points
}
FST = SpaceTime()
size = 5
FST.generate_flat(size, size)
FST.move(18, 18 + size, 18 - size)
i = 0
for n in FST.nodes:
    i += 1
    N = len(FST.node_all_connections(n)) - 6
    # print(i)
    # print(n, N)
    # print()
print("plottin")
Display.plot_3d_cyl(FST, shading=shading)
