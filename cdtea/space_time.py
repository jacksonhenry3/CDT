"""
Trying to use node and face NOT vertex and simplex
"""
import copy
import itertools
import pathlib
import pickle
import random
import typing

import networkx

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
    _NON_SERIALIZABLE_ATTRIBUTES = ('_ordered_nodes',)
    _SERIALIZABLE_ATTRIBUTES = (
        'closed', 'nodes', 'node_left', 'node_right', 'node_past', 'node_future', 'faces_containing', 'faces', 'face_dilaton', 'face_left', 'face_right', 'face_t', 'face_type',
        'face_nodes')
    _GEOMETRIC_ATTRIBUTES = (
        'nodes', 'node_left', 'node_right', 'node_past', 'node_future', 'faces_containing', 'faces', 'face_left', 'face_right', 'face_t', 'face_type', 'face_nodes')
    __slots__ = _NON_SERIALIZABLE_ATTRIBUTES + _SERIALIZABLE_ATTRIBUTES

    def __init__(self, nodes: set = None, node_left: dict = None, node_right: dict = None, node_past: dict = None, node_future: dict = None,

                 faces_containing: dict = None,

                 faces: set = None, face_dilaton: dict = None, face_left: dict = None, face_right: dict = None, face_t: dict = None, face_type: dict = None, closed: bool = True,
                 face_nodes: dict = None):
        super(SpaceTime, self).__init__()
        self.closed = closed

        # consider adding curvature here aswell
        self.nodes = set() if nodes is None else nodes  # nodes is a set of indicies
        self.node_left = {} if node_left is None else node_left  # a dict with node indices as keys
        self.node_right = {} if node_right is None else node_right  # a dict with node indices as keys
        self.node_past = {} if node_past is None else node_past  # a dict with node indices as keys
        self.node_future = {} if node_future is None else node_future  # a dict with node indices as keys
        self.faces_containing = {} if faces_containing is None else faces_containing

        self.faces = set() if faces is None else faces  # faces is a set of indicies
        self.face_nodes = {} if face_nodes is None else face_nodes
        self.face_dilaton = {} if face_dilaton is None else face_dilaton  # a dict with keys of face tuples and field vals
        self.face_left = {} if face_left is None else face_left  # a dict with keys of face tuples space-like connected
        self.face_right = {} if face_right is None else face_right  # a dict with keys of face tuples space-like connected
        self.face_t = {} if face_t is None else face_t  # a dict with keys of face tuples time-like connected
        self.face_type = {} if face_type is None else face_type

        # stateful cache attributes (performance)
        self._ordered_nodes = None

    def __eq__(self, other):
        """Equivalence between """
        if not isinstance(other, SpaceTime):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        return 'ST({:d}, {:d})'.format(len(self.nodes), len(self.faces))

    def geometric_equal(self, other) -> bool:
        """ Compares self and others geometric properties"""
        if not isinstance(other, SpaceTime):
            return False

        self_dict = self.to_dict(key_filter=list(self._GEOMETRIC_ATTRIBUTES))
        other_dict = other.to_dict(key_filter=list(other._GEOMETRIC_ATTRIBUTES))
        for k in self_dict.keys():
            if self_dict[k] != other_dict[k]:
                print('{} failed'.format(k))
        return self_dict == other_dict

    def copy(self):
        """Deepcopy of this SpaceTime"""
        return SpaceTime.from_dict(copy.deepcopy(self.to_dict()))

    @property
    def max_node(self):
        return max(self.nodes)

    @property
    def max_face(self):
        return max(self.faces, default=-1)

    @property
    def ordered_nodes(self) -> list:
        if self._ordered_nodes is None:
            self._ordered_nodes = list(sorted(self.nodes))
        return self._ordered_nodes

    @property
    def nodes_face(self) -> dict:
        return {v: k for k, v in self.face_nodes.items()}

    def gluing_edges(self, node_subset: typing.List[event.Event] = None) -> typing.List[typing.Tuple[int, str, event.GluingPoint]]:
        """Find and return all references to gluing points"""
        edges = []
        nodes = self.nodes if node_subset is None else [n.key for n in node_subset]
        for n in nodes:
            if isinstance(self.node_left[n], event.GluingPoint):
                edges.append((n, event.PassThruAttr.Left, self.node_left[n]))
            if isinstance(self.node_right[n], event.GluingPoint):
                edges.append((n, event.PassThruAttr.Right, self.node_right[n]))
            for p in self.node_past[n]:
                if isinstance(p, event.GluingPoint):
                    edges.append((n, event.PassThruAttr.Past, p))
            for f in self.node_future[n]:
                if isinstance(f, event.GluingPoint):
                    edges.append((n, event.PassThruAttr.Future, f))
        return edges

    def get_random_node(self):
        return event.Event(self, random.choice(self.ordered_nodes))

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
                n = list(sorted(self.node_future[n]))[0]
        return layers

    def add_key(self, key: int = None):
        """Function for keeping consistency across various lookup dict keys and nodes list"""
        if key is None:
            key = self.max_node + 1
        else:
            if key in self.nodes:
                raise ValueError('Cannot add node {:d} to spacetime {}, already exists'.format(key, self))
        self.nodes.add(key)
        self.node_left[key] = None
        self.node_right[key] = None
        self.node_future[key] = set()
        self.node_past[key] = set()
        self.faces_containing[key] = set()
        self._ordered_nodes = None

    def remove_key(self, key: int):
        """Function for removing node"""
        self.nodes.remove(key)
        self.node_left.pop(key)
        self.node_right.pop(key)
        self.node_future.pop(key)
        self.node_past.pop(key)
        self.faces_containing.pop(key)
        self._ordered_nodes = None

    def add_face(self, nodes: frozenset = None, key: int = None):
        """Function for keeping consistency across various lookup dict keys and nodes list"""
        if key is None:
            key = self.max_face + 1
        else:
            if key in self.faces:
                raise ValueError('Cannot add node {:d} to spacetime {}, already exists'.format(key, self))
        self.faces.add(key)
        self.face_left[key] = None
        self.face_right[key] = None
        self.face_t[key] = None
        self.face_type[key] = None
        self.face_dilaton[key] = None
        self.face_nodes[key] = nodes

        return key

    def remove_face(self, key: frozenset):
        """Function for removing node"""
        self.faces.remove(key)
        self.face_left.pop(key)
        self.face_right.pop(key)
        self.face_t.pop(key)
        self.face_type.pop(key)
        for n in self.face_nodes[key]:
            self.faces_containing[n].remove(key)

    def pop(self, node_list: typing.List[Event]):
        """
        This creates a new space-time by removing all nodes adjacent to node and returning that sub_space
        """
        sub_space = SpaceTime(closed=False)  # the sub_space will contain references to nodes that do not belong to it (for gluing purposes)

        nodes = node_list.copy()
        faces = []
        for node in node_list:
            nodes.extend(node.neighbors)
            faces.extend(self.faces_containing[node.key])

        # removes duplicates
        faces = list(set(faces))
        nodes = list(set(nodes))

        # set the sub_space nodes and faces
        for n in nodes:
            sub_space.add_key(key=n.key)
        sub_space.faces = set(faces.copy())
        sub_space.faces_containing = {n: self.faces_containing[n] for n in sub_space.nodes}

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
            self.faces.remove(f)
            sub_space.face_dilaton[f] = self.face_dilaton.pop(f)
            sub_space.face_left[f] = self.face_left.pop(f)
            sub_space.face_right[f] = self.face_right.pop(f)
            sub_space.face_t[f] = self.face_t.pop(f)
            sub_space.face_type[f] = self.face_type.pop(f)
            sub_space.face_nodes[f] = self.face_nodes.pop(f)

        # dont forget to set sub_space dead refrences
        for n in sub_space.nodes:
            self.remove_key(n)  # self.faces_containing[n] = {}

        return sub_space

    def push(self, sub_space):
        """
        This reinserts sub_space

        Warnings:
            1) This will ONLY work for a subspace that has been cut from THIS spacetime (common usage)
            2) This will ONLY work for sequential pairs of pop/push. pop/pop/push could fail
        """
        # add a check to make sure that we are inserting unique new nodes
        nodes = sub_space.ordered_nodes
        faces = sub_space.faces

        for s in nodes:
            self.add_key(s)

        # Replicate the interior structure from the subspace in the superspace (not gluing)
        # This step will also add edges that reference "gluing points", however, since
        # the subspace was cut from THIS space, then all those references should be valid
        for s, n_s in event.events([self, sub_space], nodes):
            event.connect_spatial(n_s.left, s)  # n.left = n_s.left
            event.connect_spatial(s, n_s.right)  # n.right = n_s.right
            event.connect_temporal(s, past=n_s.past)  # n.past = n_s.past
            event.connect_temporal(s, future=n_s.future)  # n.future = n_s.future
            event.set_faces(s, n_s.faces)

        # Compute neighbors to limit gluing to subspace + neighbors
        gluing_subset = [list(n.neighbors) for n in event.events(self, nodes)]
        gluing_subset = list(set(itertools.chain(*gluing_subset)))
        edges = self.gluing_edges(node_subset=gluing_subset)
        for s, k, t in edges:
            if k in (event.PassThruAttr.Left, event.PassThruAttr.Right):
                getattr(self, event.PASS_THRU_ATTR_MAP[k])[s] = int(t)
            else:
                getattr(self, event.PASS_THRU_ATTR_MAP[k])[s].remove(t)
                getattr(self, event.PASS_THRU_ATTR_MAP[k])[s].add(int(t))

        for f in faces:
            self.faces.add(f)

        for f in sub_space.faces:
            self.face_dilaton[f] = sub_space.face_dilaton[f]
            self.face_left[f] = sub_space.face_left[f]
            self.face_right[f] = sub_space.face_right[f]
            self.face_t[f] = sub_space.face_t[f]
            self.face_type[f] = sub_space.face_type[f]
            self.face_nodes[f] = sub_space.face_nodes[f]

            for n in self.face_nodes[f]:
                self.faces_containing[n].add(f)

    def to_dict(self, key_filter: typing.List[str] = None):
        """Convert a SpaceTime object to a dict containing all the configuration information

        Returns:
            dict, with all attributes of the SpaceTime
        """
        d = {attr: getattr(self, attr) for attr in self._SERIALIZABLE_ATTRIBUTES}
        existing_keys = list(d.keys())
        if key_filter is not None:
            for k in existing_keys:
                if k not in key_filter:
                    d.pop(k)
        return d

    def to_pickle(self, path: typing.Union[str, pathlib.Path] = None):
        """Convert SpaceTime to pickle format

        Args:
            path:
                str or Path, default None. If specified write out the pickle to this location

        Returns:
            bytes, if output_path is None
        """
        if path is None:
            return pickle.dumps(self)

        path = path if isinstance(path, pathlib.Path) else pathlib.Path(path)
        with open(path.as_posix(), 'wb') as fid:
            pickle.dump(self, file=fid)

    def to_networkx(self):
        """Convert a SpaceTime to a networkx Graph object, with edge attributes
        describing the type of edge, either 'spacelike' or 'timelike'

        Returns:
            networkx.Graph
        """
        # Construct initial graph
        layers = self.get_layers()
        G = networkx.Graph(num_layers=len(layers))
        G.add_nodes_from(self.ordered_nodes)

        # Add information about node layers
        layers_dict = {}
        for n, layer in enumerate(layers):
            for node in layer:
                layers_dict[node] = {'layer': n}
        networkx.set_node_attributes(G, layers_dict)

        # Add information about edge types
        edge_types = {}
        for n in self.ordered_nodes:
            for s in (self.node_left[n], self.node_right[n]):
                key = (n, s) if n < s else (s, n)
                if key not in edge_types:
                    edge_types[key] = {'type': 'spacelike'}
            for t in self.node_past[n].union(self.node_future[n]):
                key = (n, t) if n < t else (t, n)
                if key not in edge_types:
                    edge_types[key] = {'type': 'timelike'}
        G.add_edges_from(list(edge_types.keys()))
        networkx.set_edge_attributes(G, edge_types)
        return G

    @staticmethod
    def from_dict(config_dict: dict):
        """Create a SpaceTime object from a configuration dict

        Args:
            config_dict:
                dict, the configuration dictionary, MUST have all keys:

        Returns:
            SpaceTime, the reserialized SpaceTime object
        """
        for key in SpaceTime.__slots__[1:]:
            if key not in config_dict:
                raise SerializationError('Missing key {} when attempting to create SpaceTime from dict:\n{}'.format(key, str(config_dict)))
        return SpaceTime(**config_dict)  # pass-thru to init method

    @staticmethod
    def from_pickle(data: bytes = None, path: typing.Union[str, pathlib.Path] = None):
        """Create a SpaceTime object from a pickle string or file

        Args:
            data:
                str, default None. If specified use this pickle string
            path:
                str or Path, default None. If specified use this full path

        Returns:
            SpaceTime
        """
        if (data is None and path is None) or (data is not None and path is not None):
            raise SerializationError('Must specify only one of source and path when loading SpaceTime from pickle')

        if data is not None:
            return pickle.loads(data)

        path = path if isinstance(path, pathlib.Path) else pathlib.Path(path)
        with open(path.as_posix(), 'rb') as fid:
            return pickle.load(fid)


def generate_flat_spacetime(space_size: int, time_size: int):
    """
    There is a lot of 'frontloaded thought' here. Very possible a source of errors. I Have done some initial validation by inspecting the adjacency matrices. I'm fairly
    confident that the node structure is correct. The simplex structure sems reasonable but i have less control over the ordering so it isn't as clear. A 3d plot would be a good
    idea to make sure the simplices are all defined correctly with correct neighbors. Wouldnt hurt to ha e that for the vertices either.
    """
    spacetime = SpaceTime()
    index = 0  # this index counts vertices
    for t in range(time_size):
        start = index  # the first index in the current time slice
        for x in range(space_size):
            spacetime.add_key(index)

            left = start + (index - 1) % space_size
            right = start + (index + 1) % space_size

            spacetime.node_left[index] = left
            spacetime.node_right[index] = right

            # get the first node of the spatial slice above and below this one
            future_start = (start + space_size) % (space_size * time_size)
            past_start = (start - space_size) % (space_size * time_size)

            future_right = future_start + (index + 1) % space_size
            future_left = future_start + (index - 1) % space_size
            future = future_start + index % space_size

            past_left = past_start + (index - 1) % space_size
            past = past_start + index % space_size

            # these are the time connections of a node
            spacetime.node_past[index] = {past_left, past}
            spacetime.node_future[index] = {future, future_right}

            # There are twice as many simplices as nodes, so there are 2 faces defined per iteration
            # These are the faces (a different two can be chosen, the only important thing is that they are uniquly defined by the vertex (t,x))
            f1 = spacetime.add_face(frozenset({index, right, future_right}))
            f2 = spacetime.add_face(frozenset({index, future_right, future}))

            nodes_face = spacetime.nodes_face

            # define each faces type
            spacetime.face_type[f1] = 0
            spacetime.face_type[f2] = 1

            # This is where we chose the initial dilaton values for each simplex
            spacetime.face_dilaton[f1] = 1
            spacetime.face_dilaton[f2] = -1

            # This defines the two spatialy adjacent simplices to f1
            f1_r = 2 * start + (2 * index + 3) % (2 * space_size)
            f1_l = f2

            spacetime.face_left[f1] = f1_l
            spacetime.face_right[f1] = f1_r

            # This defines the two spatially adjacent simplices to f2
            f2_r = f1
            f2_l = 2 * start + (2 * index - 2) % (2 * space_size)
            spacetime.face_left[f2] = f2_l
            spacetime.face_right[f2] = f2_r

            # These are the faces in the future of f1 and f2
            f1_t = (2 * index - 2 * space_size + 1) % (2 * space_size * time_size)
            spacetime.face_t[f1] = f1_t

            f2_t = (2 * index + 2 * space_size) % (2 * space_size * time_size)
            spacetime.face_t[f2] = f2_t

            index += 1
    # if optimizing this is a good place to start
    # This could be done directly, but at the moment it is error prone and this works
    for n in spacetime.nodes:
        spacetime.faces_containing[n] = {f for f in spacetime.faces if n in spacetime.face_nodes[f]}
    return spacetime
