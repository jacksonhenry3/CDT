"""
Trying to use node and face NOT vertex and simplex
"""

import random
import typing
from cdtea import event
from cdtea.event import Event


class SpaceTimeError(ValueError):
    """Base class for error types"""


class SerializationError(SpaceTimeError):
    """Error class related to serialization"""


class SpaceTime(object):
    """SpaceTime represents a collection of linked events. The structure of those
    links, both spacelike and timelike, determines the geometry of the piecewise
    linear manifold represented by the SpaceTime.
    """

    def __init__(self, nodes: set = None, node_left: dict = None, node_right: dict = None,
                 node_past: dict = None, node_future: dict = None, faces_containing: dict = None,
                 faces: set = None, face_dilation: dict = None, face_x: dict = None,
                 face_t: dict = None, dead_references: set = None, closed: bool = True):
        super(SpaceTime, self).__init__()
        self.closed = closed

        # consider adding curvature here aswell
        self.nodes = set() if nodes is None else nodes  # nodes is just a list of indicies
        self.node_left = {} if node_left is None else node_left  # a dict with node indices as keys
        self.node_right = {} if node_right is None else node_right  # a dict with node indices as keys
        self.node_past = {} if node_past is None else node_past  # a dict with node indices as keys
        self.node_future = {} if node_future is None else node_future  # a dict with node indices as keys
        self.faces_containing = {} if faces_containing is None else faces_containing

        self.faces = set() if faces is None else faces  # faces is a frozenset of node indices
        self.face_dilaton = {} if face_dilation is None else face_dilation  # a dict with keys of face tuples and field vals
        self.face_x = {} if face_x is None else face_x  # a dict with keys of face tuples space-like connected
        self.face_t = {} if face_t is None else face_t  # a dict with keys of face tuples time-like connected

        # This could be modified to include a list of dead references
        self.dead_references = set() if dead_references is None else dead_references

    def __eq__(self, other):
        """Equivalence between """
        if not isinstance(other, SpaceTime):
            return False
        return self.to_dict() == other.to_dict()

    @property
    def max_node(self):
        return max(self.nodes)

    @property
    def ordered_nodes(self) -> list:
        return list(sorted(self.nodes))

    def get_random_node(self):
        return event.Event(self, random.choice(self.nodes))

    def get_layers(self, n=False):
        """returns a list of lists where each list contains all nodes in a specific layer, contains all nodes """
        if not n:
            n = self.ordered_nodes[0]
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
        self.nodes.add(n)
        self.node_left[n] = None
        self.node_right[n] = None
        self.node_future[n] = []
        self.node_past[n] = []
        self.faces_containing[n] = []

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
        sub_space = SpaceTime(closed=False)  # the sub_space will contain references to nodes that do not belong to it (for gluing purposes)

        nodes = node_list.copy()
        faces = []
        for node in node_list:
            nodes.extend(node.neighbors)
            # update this to use the dict instead (requires some work)
            faces.extend(self.get_faces_containing(node))

        # removes duplicates
        faces = list(set(faces))
        nodes = list(set(nodes))
        self.dead_references = set(nodes.copy())  # i.e these nodes are no longer in the st

        # set the sub_space nodes and faces
        for n in nodes:
            sub_space.add_node(n=event.event_key(n))
        sub_space.faces = set(faces.copy())

        # loop through all removed nodes and remove their properties from self and add them to sub_space
        # taking care to label gluing points (references to nodes that do not belong to sub_space)
        coerce = lambda keys: event.coerce_gluing_point(sub_space, keys)
        for n_s, n in event.events([sub_space, self], sub_space.nodes):
            event.connect_spatial(coerce(n.left), n_s)  # n_s.left = coerce(n.left)
            event.connect_spatial(n_s, coerce(n.right))  # n_s.right = coerce(n.right)
            event.connect_temporal(n_s, past=coerce(n.past))  # n_s.past = coerce(n.past)
            event.connect_temporal(n_s, future=coerce(n.future))  # n_s.future = coerce(n.future)
            event.set_faces(n_s, n.faces)

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
        if any(n not in sub_space.nodes for n in self.dead_references):
            pass
            # print("sub_space cannot fill space_time gap")
            # print("dead refrences are {}".format(self.dead_references))
            # print("sub_space nodes are {}".format(sub_space.nodes))
            # raise ValueError()

        # add a check to make sure that we are inserting unique new nodes
        nodes = sub_space.ordered_nodes
        faces = sub_space.faces

        for n in nodes:
            self.add_node(n)

        for n, n_s in event.events([self, sub_space], nodes):
            event.connect_spatial(n_s.left, n)  # n.left = n_s.left
            event.connect_spatial(n, n_s.right)  # n.right = n_s.right
            event.connect_temporal(n, past=n_s.past)  # n.past = n_s.past
            event.connect_temporal(n, future=n_s.future)  # n.future = n_s.future
            event.set_faces(n, n_s.faces)

        for f in faces:
            self.faces.add(f)

        for f in sub_space.faces:
            self.face_dilaton[f] = sub_space.face_dilaton[f]
            # self.face_x[f] = sub_space.face_x[f]
            # self.face_t[f] = sub_space.face_t[f]

        # This should probably be validated
        self.dead_nodes = []
        # Can we get rid of sub_space at this point somehow?

    def to_dict(self):
        """Convert a SpaceTime object to a dict containing all the configuration information

        Returns:
            dict, with all attributes of the SpaceTime
        """
        return {
            'closed': self.closed,
            'nodes': self.nodes,
            'node_left': self.node_left,
            'node_right': self.node_right,
            'node_past': self.node_past,
            'node_future': self.node_future,
            'faces_containing': self.faces_containing,
            'faces': self.faces,
            'face_dilation': self.face_dilaton,
            'face_x': self.face_x,
            'face_t': self.face_t,
            'dead_references': self.dead_references,
        }

    @staticmethod
    def from_dict(config_dict: dict):
        """Create a SpaceTime object from a configuration dict

        Args:
            config_dict:
                dict, the configuration dictionary, MUST have all keys:

        Returns:
            SpaceTime, the reserialized SpaceTime object
        """
        for key in ('closed', 'nodes', 'node_left', 'node_right', 'node_past', 'node_future',
                    'faces_containing', 'faces', 'face_dilation', 'face_x', 'face_t', 'dead_references'):
            if key not in config_dict:
                raise SerializationError('Missing key {} when attempting to create SpaceTime from dict:\n{}'.format(key, str(config_dict)))
        return SpaceTime(**config_dict)  # pass-thru to init method


def generate_flat_spacetime(space_size: int, time_size: int):
    """
    There is a lot of 'frontloaded thought' here. Very possible a source of errors. I Have done some initial validation by inspecting the adjacency matrices. I'm fairly confident that the node structure is correct. The simplex structure sems reasonable but i have less control over the ordering so it isn't as clear. A 3d plot would be a good idea to make sure the simplices are all defined correctly with correct neighbors. Wouldnt hurt to ha e that for the vertices either.
    """
    spacetime = SpaceTime()
    index = 0  # this index counts vertices
    for t in range(time_size):
        start = index  # the first index in the current time slice
        for x in range(space_size):
            spacetime.add_node(index)

            left = start + (index - 1) % space_size
            right = start + (index + 1) % space_size

            spacetime.node_left[index] = left
            spacetime.node_right[index] = right

            # get the first node of the spatial slice above and below this one
            future_start = (start + space_size) % (space_size * time_size)
            past_start = (start - space_size) % (space_size * time_size)

            future_right = future_start + (index + 1) % space_size
            future = future_start + (index) % space_size

            past_left = past_start + (index - 1) % space_size
            past = past_start + (index) % space_size

            # these are the time connections of a node
            spacetime.node_past[index] = [past_left, past]

            spacetime.node_future[index] = [future, future_right]

            # There are twice as many simplices as nodes, so there are 2 faces defined per iteration
            # These are the faces (a different two can be chosen, the only important thing is that they are uniquly defined by the vertex (t,x))
            f1 = frozenset({index, right, future_right})
            f2 = frozenset({index, left, past_left})

            spacetime.faces.add(f1)
            spacetime.faces.add(f2)

            # This is where we chose the initial dilaton values for each simplex
            spacetime.face_dilaton[f1] = 1
            spacetime.face_dilaton[f2] = -1

            # This defines the two spatialy adjacent simplices to f1
            f1_l = frozenset({index, future_right, future})
            f1_r = frozenset(
                {right, future_right, future_start + (index + 2) % space_size}
            )
            spacetime.face_x[f1] = [f1_l, f1_r]

            # This defines the two spatialy adjacent simplices to f2
            f2_l = frozenset({index, past, past_left})
            f2_r = frozenset(
                {left, past_left, past_start + (index - 2) % space_size}
            )
            spacetime.face_x[f2] = [f2_l, f2_r]

            # These are the faces in the future of f1 and f2
            f1_t = frozenset({index, right, past})
            spacetime.face_t[f1] = f1_t
            f2_t = frozenset({index, left, future})
            spacetime.face_t[f2] = f2_t

            spacetime.faces_containing[index] = [f1, f2, f1_l, f2_l, f1_t, f2_t]
            index += 1
    return spacetime
