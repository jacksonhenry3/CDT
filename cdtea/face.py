from collections.abc import Iterable
import typing


class PassThruAttr:
    """Constants class for pass thru attributes"""
    Left = 'left'
    Right = 'right'
    Temporal = 'temporal'
    Type = 'type'


PASS_THRU_ATTR_MAP = {  # Mapping of attribute name in Node object and corresponding lookup-dict in SpaceTime object
    # NOTE: this depends on implementation details of SpaceTime class, and should be updated in tandem
    PassThruAttr.Left: 'face_left', PassThruAttr.Right: 'face_right', PassThruAttr.Temporal: 'face_t', PassThruAttr.Type: 'face_type'}
FACE_RETURNING_ATTRS = ('left', 'right', 'temporal')


class Face:
    """A light-weight representation of a node in a SpaceTime. Since the SpaceTime contains
    lookup-dicts of all relevant node-edge relationships, the Node class serves as a syntactic
    sugar for passing between a particular node identifier and various feature lookups in the
    SpaceTime object.
    """

    def __init__(self, space_time, nodes):
        """Create a Face instance

        Args:
            space_time:
                SpaceTime, the spacetime object
            nodes:
                int, the Face label
        """
        self.space_time = space_time
        if isinstance(nodes, Face):
            # TODO check space_time equivalence
            nodes = nodes.nodes
        # Check that event exists in space_time (consistency)
        if space_time.closed and nodes not in space_time.faces:
            raise ValueError('Face Key {} not defined in spacetime: {}'.format(nodes, space_time))
        self.nodes = nodes

    def __eq__(self, other):
        """Equality comparison operator

        Args:
            other:
                Any, if an Face instance compare for equality

        Returns:
            bool, True if equivalent events, False otherwise
        """
        # TODO add "and other.space_time == self.space_time" once __eq__ defined for SpaceTime
        return isinstance(other, Face) and (other.space_time == self.space_time) and (other.nodes == self.nodes)

    def __hash__(self):
        """Make Face hashable

        Returns:
            int, the has value of the Face
        """
        # TODO add spacetime hash
        return hash(('Face', self.nodes))

    def __repr__(self):
        """Define convenient representation for events"""
        # TODO update this to use the SpaceTime repr, now it's just using STN
        # TODO update this to include a time coordinate if possible
        return 'Face(ST{:d}, {:s})'.format(len(self.space_time.nodes), -1 if self.nodes is None else str(set(self.nodes)))

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
            value = getattr(self.space_time, PASS_THRU_ATTR_MAP[key])[self.nodes]
            if key in FACE_RETURNING_ATTRS:
                if isinstance(list(value)[0], Iterable) and isinstance(value, Iterable):
                    return set([v if v is None else Face(space_time=self.space_time, nodes=v) for v in value])
                return value if value is None else Face(space_time=self.space_time, nodes=value)
            return value

    @property
    def temporal_neighbor(self):
        """Pass-thru accessor for future neighbors

        Returns:
            List[Face], the future neighbors
        """
        return self._get_pass_thru_attr_(PassThruAttr.Temporal)

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


def faces(space_time, keys: typing.Union[frozenset, typing.Iterable[frozenset]] = None) -> typing.Union[Face, typing.List[Face]]:
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
    if isinstance(list(keys)[0], Iterable) and isinstance(keys, Iterable):
        return [Face(space_time=space_time, nodes=k) for k in keys]
    return Face(space_time=space_time, nodes=keys)
