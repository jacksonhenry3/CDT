"""
Trying to use node and face NOT vertex and simplex
"""


import numpy as np
import Display


class SpaceTime(object):
    """docstring for SpaceTime."""

    # __slots__ = []

    def __init__(self):
        super(SpaceTime, self).__init__()

        # consider adding curvature here aswell
        self.nodes = []  # nodes is just a list of indicies
        self.node_x = {}  # a dict with node indices as keys
        self.node_t = {}  # a dict with node indices as keys
        self.faces_containing = {}

        self.faces = []  # faces is a frozenset of node indeces
        self.face_dilaton = {}  # a dict with keys of face tuples and field vals
        self.face_x = {}  # a dict with keys of face tuples space-like connected
        self.face_t = {}  # a dict with keys of face tuples time-like connected

        # If this ST contains refrences to a node not in nodes.
        self.contains_dead_refrences = False

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
                self.node_x[index] = [
                    left,
                    right,
                ]  # each node is connected to those to its left and right

                # get the first node of the spatial slice above and below this one
                future_start = (start + space_size) % (space_size * time_size)
                past_start = (start - space_size) % (space_size * time_size)

                future_right = future_start + (index + 1) % space_size
                future = future_start + (index) % space_size

                past_left = past_start + (index - 1) % space_size
                past = past_start + (index) % space_size

                # these are the time connections of a node
                self.node_t[index] = [
                    past,
                    past_left,
                    future,
                    future_right,
                ]

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

    # Made redundant by faces_containing dict, remove once fully validated
    def get_faces_containing(self, n):
        # get all simplices that contain a particular vertex
        return {face for face in self.faces if n in face}

    def pop(self, node):
        """
        This creates a new space-time by removing all nodes adjacent to node and returning that sub_space
        """
        sub_space = SpaceTime()

        nodes = self.node_x[node] + self.node_t[node] + [node]
        faces = self.faces_containing[node]

        for n in nodes:
            self.nodes.remove(n)
        sub_space.nodes = nodes

        for n in sub_space.nodes:
            sub_space.node_x[n] = self.node_x.pop(n)
            sub_space.node_t[n] = self.node_t.pop(n)
            sub_space.faces_containing[n] = self.faces_containing.pop(n)

        for f in faces:
            self.faces.remove(f)
        sub_space.faces = faces

        for f in sub_space.faces:
            sub_space.face_dilaton[f] = self.face_dilaton.pop(f)
            sub_space.face_x[f] = self.face_x.pop(f)
            sub_space.face_t[f] = self.face_t.pop(f)

        self.contains_dead_refrences = True
        sub_space.contains_dead_refrences = True

        return sub_space

    def push(self, sub_space):
        """
        This reinserts sub_space
        """
        nodes = sub_space.nodes
        faces = sub_space.faces

        for n in nodes:
            self.nodes.append(n)

        for n in nodes:
            self.node_x[n] = sub_space.node_x.pop(n)
            self.node_t[n] = sub_space.node_t.pop(n)
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

        # add  a check that future and past are aproapriatly connected to node
        nodes = [node, future, past]
        possibly_modified_nodes = [self.node_x[node] + self.node_t[node]]
        possibly_modified_faces = self.faces_containing[node]


FST = SpaceTime()
FST.generate_flat(12, 12)

sub_space = FST.pop(4)
FST.push(sub_space)
Display.show_node_adjacency_matrix(FST)
