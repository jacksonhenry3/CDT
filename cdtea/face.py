from collections.abc import Iterable
import typing


class PassThruAttr:
    """Constants class for pass thru attributes"""
    Left = 'left'
    Right = 'right'
    Temporal = 'temporal'
    Type = 'type'
    Nodes = 'nodes'


PASS_THRU_ATTR_MAP = {  # Mapping of attribute name in Node object and corresponding lookup-dict in SpaceTime object
    # NOTE: this depends on implementation details of SpaceTime class, and should be updated in tandem
    PassThruAttr.Left: 'face_left', PassThruAttr.Right: 'face_right', PassThruAttr.Temporal: 'face_t', PassThruAttr.Type: 'face_type', PassThruAttr.Nodes: 'face_nodes'}
FACE_RETURNING_ATTRS = ('left', 'right', 'temporal')


class Face:
    """A light-weight representation of a node in a SpaceTime. Since the SpaceTime contains
    lookup-dicts of all relevant node-edge relationships, the Node class serves as a syntactic
    sugar for passing between a particular node identifier and various feature lookups in the
    SpaceTime object.
    """

    def __init__(self, space_time, key):
        """Create a Face instance

        Args:
            space_time:
                SpaceTime, the spacetime object
            key:
                int, the Face label
        """
        self.space_time = space_time
        if isinstance(key, Face):
            # TODO check space_time equivalence
            key = key.key
        # Check that event exists in space_time (consistency)
        if space_time.closed and key not in space_time.faces:
            raise ValueError('Face Key {} not defined in spacetime: {}'.format(key, space_time))
        self.key = key

    def __eq__(self, other):
        """Equality comparison operator

        Args:
            other:
                Any, if an Face instance compare for equality

        Returns:
            bool, True if equivalent events, False otherwise
        """
        # TODO add "and other.space_time == self.space_time" once __eq__ defined for SpaceTime
        return isinstance(other, Face) and (other.space_time == self.space_time) and (other.key == self.key)

    def __hash__(self):
        """Make Face hashable

        Returns:
            int, the has value of the Face
        """
        # TODO add spacetime hash
        return hash(('Face', self.key))

    def __repr__(self):
        """Define convenient representation for events"""
        # TODO update this to use the SpaceTime repr, now it's just using STN
        # TODO update this to include a time coordinate if possible
        return 'Face(ST{:d}, {:s})'.format(len(self.space_time.nodes), -1 if self.key is None else str(self.key))

    def _get_pass_thru_attr_(self, key: str):
        """Helper private method for looking up pass-thru attributes.For these attributes only,
        the call will be redirected to the underlying SpaceTime object from which the key originates

        Args:
            key:
                str, the name of the attribute to get

        Returns:
            Face, List[Face], or List[frozenset] depending on whether a single neighbor,
            multiple neighbors, or faces are requested
        """
        if key in PASS_THRU_ATTR_MAP:
            value = getattr(self.space_time, PASS_THRU_ATTR_MAP[key])[self.key]
            if key in FACE_RETURNING_ATTRS:
                if isinstance(value, Iterable):
                    return set([v if v is None else Face(space_time=self.space_time, key=v) for v in value])
                return value if value is None else Face(space_time=self.space_time, key=value)
            return value

    @property
    def temporal_neighbor(self):
        """Pass-thru accessor for future neighbors

        Returns:
            List[Face], the future neighbors
        """
        return self._get_pass_thru_attr_(PassThruAttr.Temporal)

    @property
    def nodes(self):
        """Pass-thru accessor for right neighbor

        Returns:
            Face, the right neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Nodes)

    @property
    def left(self):
        """Pass-thru accessor for left neighbor

        Returns:
            Face, the left neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Left)

    @property
    def right(self):
        """Pass-thru accessor for right neighbor

        Returns:
            Face, the right neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Right)

    @property
    def type(self):
        """Pass-thru accessor for right neighbor

        Returns:
            Face, the right neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Type)

    @property
    def neighbors(self):
        """All neighbors, events connected to this event via any kind of edge

        Returns:
            List[Face], all neighbor events
        """
        return self.spatial_neighbors.union({self.temporal_neighbor})

    @property
    def spatial_neighbors(self):
        """Spatial Neighbors are those that are connected to this event via space-like edges

        Returns:
            List[Face], the left and right neighbors
        """
        return {self.left, self.right}


def faces(space_time, keys: typing.Union[int, typing.Iterable[int]] = None) -> typing.Union[Face, typing.List[Face]]:
    """Helper function for creating multiple Event instances from an iterable
    of SpaceTime keys

    Args:
        space_time:
            SpaceTime, the spacetime from which events will be produced
        keys:
            Iterable[int], a collection of SpaceTime keys from which to create Events

    Returns:
        List[Event], a list of Events corresponding to the order of the given iterable of keys
    """
    if isinstance(space_time, Iterable):  # TODO more thorough check in case we make spacetime iterable..
        return list(zip(*[Face(st, keys) for st in space_time]))
    if keys is None:
        keys = space_time.faces
    if isinstance(keys, Iterable):
        return [Face(space_time=space_time, key=k) for k in keys]
    return Face(space_time=space_time, key=keys)


def connect_spatial(left: Face, right: Face):
    """Make a consistent spatial connection between two Faces

    Args:
        left:
            Face, the event to be on the left side of the spatial connection
        right:
            Face, the event to be on the right side of the spatial connection

    Notes:
        Edge Consistency:
            The below code ensures that both ends of edges are maintained in a way that
            preserves the following consistency relations between events A and B:

                (1) A.right = B    <==>  A = B.left
                (2) A.left = B     <==>  A = B.right
    """
    # Set left.right = right
    if left.right != right:
        original_right_of_left = left.right
        getattr(left.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Right])[left.key] = right.key
        if original_right_of_left is not None:
            getattr(original_right_of_left.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Left])[original_right_of_left.key] = None

    # Set right.left = left
    if right.left != left:
        original_left_of_right = right.left
        getattr(right.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Left])[right.key] = left.key
        if original_left_of_right is not None:
            getattr(original_left_of_right.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Right])[original_left_of_right.key] = None


def connect_temporal(present: Face, t: Face):
    """Make a consistent connection between a present event and a time-like connected event

    Args:
        present:
            Face, the face for which to update the temporal_connection of
        t:
            Face, set the temporal_nieghbor of present equal to this face


    Notes:
        Edge Consistency:
            The below code ensures that both ends of face connection are maintained in a way that
            preserves the following consistency relations between events A and B:

                (3) B = A.temporal_neighbor    <==>  A = B.temporal_neighbor
                (4) B = A.temporal_neighbor    <==>  A = B.temporal_neighbor
    """
    # Set left.right = right
    if present.temporal_neighbor != t:
        original_t_of_present = present.temporal_neighbor
        getattr(present.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Right])[present.key] = t.key
        if original_t_of_present is not None:
            getattr(original_t_of_present.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Left])[original_t_of_present.key] = None

    # Set t.present = present
    if t.temporal_neighbor != present:
        original_present_of_t = t.temporal_neighbor
        getattr(t.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Left])[t.key] = present.key
        if original_present_of_t is not None:
            getattr(original_present_of_t.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Right])[original_present_of_t.key] = None
