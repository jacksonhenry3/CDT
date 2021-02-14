"""
Trying to use node and face NOT vertex and simplex
"""

import random
import typing
from cdtea import event
from cdtea.event import Event


class SpaceTime(object):
    """docstring for SpaceTime."""

    # __slots__ = []

    def __init__(self, closed: bool = True):
        super(SpaceTime, self).__init__()
        self.closed = closed

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
        # self.max_node = 0

    @property
    def max_node(self):
        return max(self.nodes)

    def get_random_node(self):
        return event.Event(self, random.choice(self.nodes))

    def get_layers(self, n=False):
        """returns a list of lists where each list contains all nodes in a specific layer, contains all nodes """
        if not n:
            n = self.nodes[0]
        used = []
        layers = []
        layer = []
        while n not in used:
            layer.append(n)
            used.append(n)
            n = self.node_left[n]
            if n in used:
                layers.append(layer)
                layer = []
                n = self.node_future[n][0]
        return layers

    def add_node(self, n: int = None):
        """Function for keeping consistency across various lookup dict keys and nodes list"""
        if n is None:
            n = self.max_node + 1
        else:
            if n in self.nodes:
                raise ValueError('Cannot add node {:d} to spacetime {}, already exists'.format(n, self))
        self.nodes.append(n)
        self.node_left[n] = None
        self.node_right[n] = None
        self.node_future[n] = None
        self.node_past[n] = None
        self.faces_containing[n] = None

    def remove_node(self, n: int):
        """Function for removing node"""
        n = event.event_key(n)
        self.nodes.remove(n)
        self.node_left.pop(n)
        self.node_right.pop(n)
        self.node_future.pop(n)
        self.node_past.pop(n)
        self.faces_containing.pop(n)

    # TODO Made redundant by faces_containing dict, remove once fully validated
    def get_faces_containing(self, n: Event):
        # get all simplices that contain a particular vertex
        # TODO add "Face" pass-thru abstraction?
        return {face for face in self.faces if event.event_key(n) in face}

    def pop(self, node_list: typing.List[Event]):
        """
        This creates a new space-time by removing all nodes adjacent to node and returning that sub_space
        """
        sub_space = SpaceTime(
            closed=False)  # the sub_space will contain references to nodes that do not belong to it (for gluing purposes)

        nodes = node_list.copy()
        faces = []
        for node in node_list:
            nodes.extend(node.neighbors)
            # update this to use the dict instead (requires some work)
            faces.extend(self.get_faces_containing(node))

        # removes duplicates
        faces = list(set(faces))
        nodes = list(set(nodes))
        self.dead_refrences = nodes.copy()  # i.e these nodes are no longer in the st

        # set the sub_space nodes and faces
        sub_space.nodes = [event.event_key(n) for n in nodes]
        sub_space.faces = faces.copy()

        # loop through all removed nodes and remove their properties from self and add them to sub_space
        # taking care to label gluing points (references to nodes that do not belong to sub_space)
        coerce = lambda keys: event.coerce_gluing_point(sub_space, keys)
        for n_s, n in event.events([sub_space, self], sub_space.nodes):
            n_s.left = coerce(n.left)
            n_s.right = coerce(n.right)
            n_s.past = coerce(n.past)
            n_s.future = coerce(n.future)
            n_s.faces = n.faces

        # loop through all removed faces and remove their properties from self and add them to sub_space
        for f in sub_space.faces:
            sub_space.face_dilaton[f] = self.face_dilaton.pop(f)
            # sub_space.face_x[f] = self.face_x.pop(f)
            # sub_space.face_t[f] = self.face_t.pop(f)

        # dont forget to set sub_space dead refrences
        for n in sub_space.nodes:
            self.remove_node(n)

        # remove all faces that contain anything in node_list
        for f in faces:
            self.faces.remove(f)

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
            self.add_node(n)

        for n, n_s in zip(event.events(self, nodes), event.events(sub_space, nodes)):
            n.left = n_s.left
            n.right = n_s.right
            n.past = n_s.past
            n.future = n_s.future
            n.faces = n_s.faces

        for f in faces:
            self.faces.append(f)

        for f in sub_space.faces:
            self.face_dilaton[f] = sub_space.face_dilaton[f]
            # self.face_x[f] = sub_space.face_x[f]
            # self.face_t[f] = sub_space.face_t[f]

        # This should probably be validated
        self.dead_nodes = []
        # Can we get rid of sub_space at this point somehow?


def generate_flat(space_size, time_size):
    """
    Generates a flat spacetime with the specified dimensions.
    """
    st = SpaceTime()
    index = 0  # this index counts vertices
    for t in range(time_size):
        start = index  # the first index in the current time slice
        for x in range(space_size):
            st.nodes.append(index)

            left = start + (index - 1) % space_size
            right = start + (index + 1) % space_size

            st.node_left[index] = left
            st.node_right[index] = right

            # get the first node of the spatial slice above and below this one
            future_start = (start + space_size) % (space_size * time_size)
            past_start = (start - space_size) % (space_size * time_size)

            future_right = future_start + (index + 1) % space_size
            future = future_start + (index) % space_size

            past_left = past_start + (index - 1) % space_size
            past = past_start + (index) % space_size

            # these are the time connections of a node
            st.node_past[index] = [past_left, past]

            st.node_future[index] = [future, future_right]

            # There are twice as many faces as nodes, so there are 2 faces defined per iteration
            # These are the faces (a different two can be chosen, the only important thing is that they are uniquly defined by the vertex (t,x))
            f1 = frozenset({index, right, future_right})
            f2 = frozenset({index, left, past_left})

            st.faces.append(f1)
            st.faces.append(f2)

            # This is where we chose the initial dilaton values for each simplex
            # TODO make these random, for now they are usefull for adding colors to visualizations.
            st.face_dilaton[f1] = 1
            st.face_dilaton[f2] = -1

            # This defines the two spatially adjacent faces to f1
            f1_l = frozenset({index, future_right, future})
            f1_r = frozenset(
                {right, future_right, future_start + (index + 2) % space_size}
            )
            st.face_x[f1] = [f1_l, f1_r]

            # This defines the two spatially adjacent faces to f2
            f2_l = frozenset({index, past, past_left})
            f2_r = frozenset(
                {left, past_left, past_start + (index - 2) % space_size}
            )
            st.face_x[f2] = [f2_l, f2_r]

            # These are the faces in the future of f1 and f2
            f1_t = frozenset({index, right, past})
            st.face_t[f1] = f1_t
            f2_t = frozenset({index, left, future})
            st.face_t[f2] = f2_t

            st.faces_containing[index] = [f1, f2, f1_l, f2_l, f1_t, f2_t]
            index += 1
    return (st)
