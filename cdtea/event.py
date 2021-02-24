"""This module defines properties related to nodes in spacetime as well as their manipulation. Most
non-trivial operations are reserved for the SpaceTime object, and the Node class is largely a syntactic
sugar for code readability
"""

import typing
from collections import Iterable


class PassThruAttr:
    """Constants class for pass thru attributes"""
    Left = 'left'
    Right = 'right'
    Past = 'past'
    Future = 'future'
    Faces = 'faces'


PASS_THRU_ATTR_MAP = {
    # Mapping of attribute name in Node object and corresponding lookup-dict in SpaceTime object
    # NOTE: this depends on implementation details of SpaceTime class, and should be updated in tandem
    PassThruAttr.Left: 'node_left',
    PassThruAttr.Right: 'node_right',
    PassThruAttr.Past: 'node_past',
    PassThruAttr.Future: 'node_future',
    PassThruAttr.Faces: 'faces_containing'
}
EVENT_RETURNING_ATTRS = ('left', 'right', 'past', 'future')
EDGE_CONSISTENCY_ATTR_DUALS = [
    # Mapping of attributes that define edge consistency relationships, which
    # may also be viewed as parity and time-reversal duals
    (PassThruAttr.Left, PassThruAttr.Right),
    (PassThruAttr.Past, PassThruAttr.Future),
]
EDGE_CONSISTENCY_ATTR_DUALS_DICT = dict(EDGE_CONSISTENCY_ATTR_DUALS + [(v, k) for k, v in EDGE_CONSISTENCY_ATTR_DUALS])


class Event:
    """A light-weight representation of a node in a SpaceTime. Since the SpaceTime contains
    lookup-dicts of all relevant node-edge relationships, the Node class serves as a syntactic
    sugar for passing between a particular node identifier and various feature lookups in the
    SpaceTime object.
    """

    def __init__(self, space_time, event_key):
        """Create an Event instance

        Args:
            space_time:
                SpaceTime, the spacetime object
            event_key:
                int, the Event label
        """
        self.space_time = space_time
        if isinstance(event_key, Event):
            # TODO check space_time equivalence
            event_key = event_key.key
        # Check that event exists in space_time (consistency)
        if space_time.closed and event_key not in space_time.nodes:
            raise ValueError('Event Key {} not defined in spacetime: {}'.format(event_key, space_time))
        self.key = event_key

    def __eq__(self, other):
        """Equality comparison operator

        Args:
            other:
                Any, if an Event instance compare for equality

        Returns:
            bool, True if equivalent events, False otherwise
        """
        # TODO add "and other.space_time == self.space_time" once __eq__ defined for SpaceTime
        return isinstance(other, Event) and (other.space_time == self.space_time) and (other.key == self.key)

    def __hash__(self):
        """Make Event hashable

        Returns:
            int, the has value of the Event
        """
        # TODO add spacetime hash
        return hash(('Event', self.key))

    def __repr__(self):
        """Define convenient representation for events"""
        # TODO update this to use the SpaceTime repr, now it's just using STN
        # TODO update this to include a time coordinate if possible
        return 'Event(ST{:d}, {:d})'.format(len(self.space_time.nodes), -1 if self.key is None else self.key)

    def _get_pass_thru_attr_(self, key: str):
        """Helper private method for looking up pass-thru attributes.For these attributes only,
        the call will be redirected to the underlying SpaceTime object from which the key originates

        Args:
            key:
                str, the name of the attribute to get

        Returns:
            Event, List[Event], or List[frozenset] depending on whether a single neighbor,
            multiple neighbors, or faces are requested
        """
        if key in PASS_THRU_ATTR_MAP:
            value = getattr(self.space_time, PASS_THRU_ATTR_MAP[key])[self.key]
            if key in EVENT_RETURNING_ATTRS:
                if isinstance(value, Iterable):
                    return set([v if v is None else Event(space_time=self.space_time, event_key=v) for v in value])
                return value if value is None else Event(space_time=self.space_time, event_key=value)
            return value

    @property
    def faces(self):
        """Pass-thru accessor for faces

        Returns:
            List[frozenset], the faces
        """
        return self._get_pass_thru_attr_(PassThruAttr.Faces)

    @property
    def future(self):
        """Pass-thru accessor for future neighbors

        Returns:
            List[Event], the future neighbors
        """
        return self._get_pass_thru_attr_(PassThruAttr.Future)

    @property
    def is_gluing_point(self):
        """Boolean variable for determining gluing points

        Returns:
            bool, True if this event represents a gluing point, False otherwise.
        """
        return isinstance(self.key, GluingPoint)

    @property
    def left(self):
        """Pass-thru accessor for left neighbor

        Returns:
            Event, the left neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Left)

    @property
    def neighbors(self):
        """All neighbors, events connected to this event via any kind of edge

        Returns:
            List[Event], all neighbor events
        """
        return self.spatial_neighbors.union(self.temporal_neighbors)

    @property
    def past(self):
        """Pass-thru accessor for past neighbors

        Returns:
            List[Event], the past neighbors
        """
        return self._get_pass_thru_attr_(PassThruAttr.Past)

    @property
    def right(self):
        """Pass-thru accessor for right neighbor

        Returns:
            Event, the right neighbor
        """
        return self._get_pass_thru_attr_(PassThruAttr.Right)

    @property
    def spatial_neighbors(self):
        """Spatial Neighbors are those that are connected to this event via space-like edges

        Returns:
            List[Event], the left and right neighbors
        """
        return {self.left, self.right}

    @property
    def temporal_neighbors(self):
        """Temporal neighbors are those that are connected to this event via time-like edges

        Returns:
            List[Event], the past and future neighbors
        """
        return self.past.union(self.future)


def event_key(e: typing.Union[Event, int]) -> int:
    """Small utility function for coercing Event instances to their SpaceTime keys

    Args:
        e:
            Event or int, the event to coerce into a key (if necessary)

    Returns:
        int, the coerced event key
    """
    return e.key if isinstance(e, Event) else e


def events(space_time, keys: typing.Union[int, typing.Iterable[int]] = None) -> typing.Union[Event, typing.List[Event]]:
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
        return list(zip(*[events(st, keys) for st in space_time]))
    if keys is None:
        keys = space_time.nodes
    if isinstance(keys, Iterable):
        return [Event(space_time=space_time, event_key=k) for k in keys]
    return Event(space_time=space_time, event_key=keys)


class GluingPoint(int):
    """A Gluing Point represents a reference to an "open edge" or an event that
    does not belong to a particular spacetime. They are used for gluing spacetimes
    together, which primarily arises as a functional inverse to removing a subset of
    events from a spacetime (or 'cutting'). The terminology of cutting / gluing is
    borrowed from topological literature.

    The Gluing Point int subclass is used to passively identify gluing points
    as event keys without changing and fundamental behavior of the event key.
    """


def coerce_gluing_point(space_time, event: typing.Union[Event, typing.Iterable[Event]]):
    """Coerce event key to GluingPoints if the event does not belong to the space_time

    Args:
        space_time:
            SpaceTime, the spacetime object
        event:
            Event, the event to coerce. key will be wrapped as GluingPoint if event
            does not belong the space_time argument

    Returns:
        Event or List[Event], the coerced events
    """
    # Naive
    if isinstance(event, Iterable):
        return set([coerce_gluing_point(space_time, v) for v in event])
    if event.key not in space_time.nodes:
        return Event(event.space_time, event_key=GluingPoint(event.key))
    return event


def connect_spatial(left: Event, right: Event):
    """Make a consistent spatial connection between two events

    Args:
        left:
            Event, the event to be on the left side of the spatial connection
        left:
            Event, the event to be on the right side of the spatial connection

    Notes:
        Edge Consistency:
            The below code ensures that both ends of edges are maintained in a way that
            preserves the following consistency relations between events A and B:

                (1) A.right = B    <==>  A = B.left
                (2) A.left = B     <==>  A = B.right
    """
    # Set left.right = right
    if not left.is_gluing_point and left.right != right:
        original_right_of_left = left.right
        getattr(left.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Right])[left.key] = coerce_gluing_point(left.space_time, right).key
        if original_right_of_left is not None:
            getattr(original_right_of_left.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Left])[original_right_of_left.key] = None

    # Set right.left = left
    if not right.is_gluing_point and right.left != left:
        original_left_of_right = right.left
        getattr(right.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Left])[right.key] = coerce_gluing_point(right.space_time, left).key
        if original_left_of_right is not None:
            getattr(original_left_of_right.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Right])[original_left_of_right.key] = None


def connect_temporal(present: Event, past: typing.Set[Event] = None, future: typing.Set[Event] = None):
    """Make a consistent connection between a present event and a collection of past or future events

    Args:
        present:
            Event, the event for which to update the past or future
        past:
            List[Event], default None, if specified, set the past of present equal to these events
        future:
            List[Event], default None, if specified, set the future of present equal to these events

    Notes:
        Edge Consistency:
            The below code ensures that both ends of edges are maintained in a way that
            preserves the following consistency relations between events A and B:

                (3) B in A.past    <==>  A in B.future
                (4) B in A.future  <==>  A in B.past
    """
    if past is None and future is None:
        raise ValueError('Must specify either past or future of present event')

    for attr, value in zip((PassThruAttr.Past, PassThruAttr.Future), (past, future)):
        dual_attr = EDGE_CONSISTENCY_ATTR_DUALS_DICT[attr]
        if value is not None:
            # ensure unique
            value = set(value)

            # Set new value and keep track of original
            original = getattr(present, attr)
            getattr(present.space_time, PASS_THRU_ATTR_MAP[attr])[present.key] = set([v.key for v in coerce_gluing_point(present.space_time, value)])

            # Set consistency condition for new nodes
            new = [e for e in value if e not in original]
            for n in new:
                if not n.is_gluing_point and present not in getattr(n, dual_attr):
                    getattr(n.space_time, PASS_THRU_ATTR_MAP[dual_attr])[n.key].add(coerce_gluing_point(n.space_time, present).key)

            # Set consistency condition for replaced nodes
            replaced = [e for e in original if e not in value]
            for r in replaced:
                if not r.is_gluing_point and present in getattr(r, dual_attr):
                    getattr(r.space_time, PASS_THRU_ATTR_MAP[dual_attr])[r.key].remove(coerce_gluing_point(r.space_time, present).key)


def set_faces(event: Event, faces: typing.List[frozenset]):
    """Utility for setting the faces attribute of an event

    Args:
        event:
            Event, the event for which to update the faces
        faces:
            List[frozenset], the faces to assign to the event
    """
    getattr(event.space_time, PASS_THRU_ATTR_MAP[PassThruAttr.Faces])[event.key] = faces
