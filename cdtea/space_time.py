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

        self.faces = []  # faces is a frozenset of node indices
        self.face_dilaton = {}  # a dict with keys of face tuples and field vals
        self.face_x = {}  # a dict with keys of face tuples space-like connected
        self.face_t = {}  # a dict with keys of face tuples time-like connected

        # This could be modified to include a list of dead references
        self.dead_references = []


    def __eq__(self, other):
        """Equivalence between """
        if not isinstance(other, SpaceTime):
            return False
        # TODO add checking of edges and faces
        return self.nodes == other.nodes

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
        self.dead_references = nodes.copy()  # i.e these nodes are no longer in the st

        # set the sub_space nodes and faces
        for n in nodes:
            sub_space.add_node(n=event.event_key(n))
        sub_space.faces = faces.copy()

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
        nodes = sub_space.nodes
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
        future_s = Event(sub_space, future)  # Need these two because they have been "popped" out of the original spacetime
        past_s = Event(sub_space, past)

        # increment the total node counter
        new_node_num = max(self.nodes + sub_space.nodes) + 1
        sub_space.add_node(new_node_num)

        # create a node object for easy manipulation. This also automatically adds the node to the sub_space
        new_s = Event(sub_space, new_node_num)
        node_s = Event(sub_space, node)
        left_s = Event(sub_space, node_s.left)
        left = node_s.left
        right = node_s.right

        # spatial changes
        event.connect_spatial(new_s, node_s)  # new_s.right = node_s and node_s.left = new_s
        event.connect_spatial(left_s, new_s)  # new_s.left = left_s and left_s.right = new_s

        # future changes
        # TODO examine algorithm concept of connection vs Spacetime (e.g. after popping a node out, what does asking for "left" mean?)
        new_future_set = [future_s]
        f = future_s.left

        while f in node_s.future:
            if not f.is_gluing_point:
                new_future_set.append(f)
                sub_space.node_future[event.event_key(node)].remove(event.event_key(f))  # TODO cleanup the event key coercion by figuring out workaround for node.future.remove()
                sub_space.node_past[event.event_key(f)].remove(event.event_key(node))
            f = f.left
        event.connect_temporal(new_s, future=list(set(new_future_set)))
        old_future_set = list(
            set(node_s.future) - set(new_future_set)
        ) + [future_s]
        event.connect_temporal(node_s, future=old_future_set)
        # sub_space.node_past[future].append(new_node)

        # past changes
        new_past_set = [past_s]
        p = past_s.left
        while p in node_s.past:
            if not p.is_gluing_point:
                new_past_set.append(p)
                sub_space.node_past[event.event_key(node_s)].remove(event.event_key(p))
                sub_space.node_future[event.event_key(p)].remove(event.event_key(node_s))
            p = p.left

        event.connect_temporal(new_s, past=new_past_set)
        old_past_set = list(set(node_s.past) - set(new_past_set)) + [past_s]
        event.connect_temporal(node_s, past=old_past_set)
        # sub_space.node_future[past].append(new_node)

        # face changes
        # remove old faces
        sub_space.faces = []

        n = future_s
        leftmost_future = n
        while n.left in new_s.future:
            v1 = n
            n = n.left
            leftmost_future = n
            new_face = frozenset([v1.key, n.key, new_s.key])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = -1
        n = past_s
        leftmost_past = n
        while n.left in new_s.past:
            v1 = n
            n = n.left
            leftmost_past = n
            new_face = frozenset([v1.key, n.key, new_s.key])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = 100

        n = future_s
        rightmost_future = n
        while n.right in node_s.future:
            v1 = n
            n = n.right
            rightmost_future = n
            new_face = frozenset([v1.key, n.key, node_s.key])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = -1
        n = past_s
        rightmost_past = n
        while n.right in node_s.past:
            v1 = n
            n = n.right
            rightmost_past = n
            new_face = frozenset([v1.key, n.key, node_s.key])
            sub_space.faces.append(new_face)
            sub_space.face_dilaton[new_face] = 100

        righmost_future = future_s

        sub_space.faces.append(frozenset({node_s.key, new_s.key, future_s.key}))
        sub_space.face_dilaton[frozenset({node_s.key, new_s.key, future_s.key})] = 1
        sub_space.faces.append(frozenset({node_s.key, new_s.key, past_s.key}))
        sub_space.face_dilaton[frozenset({node_s.key, new_s.key, past_s.key})] = -1

        sub_space.faces.append(frozenset({node_s.key, right.key, rightmost_future.key}))
        sub_space.face_dilaton[frozenset({node_s.key, right.key, rightmost_future.key})] = 1
        sub_space.faces.append(frozenset({node_s.key, right.key, rightmost_past.key}))
        sub_space.face_dilaton[frozenset({node_s.key, right.key, rightmost_past.key})] = -1

        sub_space.faces.append(frozenset({left.key, new_s.key, leftmost_future.key}))
        sub_space.face_dilaton[frozenset({left.key, new_s.key, leftmost_future.key})] = 1
        sub_space.faces.append(frozenset({left.key, new_s.key, leftmost_past.key}))
        sub_space.face_dilaton[frozenset({left.key, new_s.key, leftmost_past.key})] = -1

        event.set_faces(new_s, [])
        event.set_faces(node_s, [])
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
